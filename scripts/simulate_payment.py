"""
Script to simulate a Stripe payment top-up without going through the browser.

Creates a checkout session, immediately confirms it via the Stripe API,
and then simulates the webhook event locally to trigger balance crediting.

Usage:
    # Top-up using a pre-defined package:
    python -m scripts.simulate_payment --email user@example.com --price-id price_abc123

    # Top-up with a custom token count:
    python -m scripts.simulate_payment --email user@example.com --tokens 250

    # Specify user by ID instead of email:
    python -m scripts.simulate_payment --user-id abc-123 --tokens 100

    # Skip webhook simulation and just credit directly in the DB:
    python -m scripts.simulate_payment --email user@example.com --tokens 100 --direct
"""

import argparse
import sys

import stripe
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from src.domain.enums import BalanceTransactionType
from src.infrastructure.db.models import (
    BalanceTransaction as BalanceTransactionModel,
)
from src.infrastructure.db.models import User as UserModel
from src.infrastructure.db.settings import get_settings as get_db_settings
from src.infrastructure.services.payment.settings import get_stripe_settings


def resolve_user(
    session: Session, email: str | None, user_id: str | None
) -> UserModel:
    if email:
        query = select(UserModel).where(UserModel.email == email)
    else:
        query = select(UserModel).where(UserModel.id == user_id)

    user: UserModel | None = session.execute(query).scalar_one_or_none()
    if user is None:
        print("Error: User not found.")
        sys.exit(1)
    return user


def resolve_tokens(
    stripe_settings, price_id: str | None, tokens: int | None
) -> tuple[int, str | None]:
    """Returns (token_count, price_id_or_none)."""
    if price_id:
        if price_id not in stripe_settings.STRIPE_TOKEN_PACKAGES:
            print(f"Error: Price ID '{price_id}' not in allowed packages.")
            print(
                f"Available: {list(stripe_settings.STRIPE_TOKEN_PACKAGES.keys())}"
            )
            sys.exit(1)
        return stripe_settings.STRIPE_TOKEN_PACKAGES[price_id], price_id
    return tokens, None


def direct_credit(
    session: Session,
    user: UserModel,
    token_count: int,
    payment_provider_id: str,
) -> None:
    """Directly credit the user in the DB, bypassing Stripe and the webhook."""
    # Check for duplicate
    existing = session.execute(
        select(BalanceTransactionModel).where(
            BalanceTransactionModel.payment_provider_id == payment_provider_id
        )
    ).scalar_one_or_none()

    if existing:
        print(f"Error: Payment '{payment_provider_id}' already processed.")
        sys.exit(1)

    old_balance = user.balance
    user.balance += token_count

    txn = BalanceTransactionModel(
        user_id=user.id,
        payment_provider_id=payment_provider_id,
        type=BalanceTransactionType.top_up,
        amount=float(token_count),
    )
    session.add(txn)
    session.commit()
    session.refresh(user)

    print(f"User:          {user.email} ({user.id})")
    print(f"Old balance:   {old_balance:.2f}")
    print(f"Tokens added:  {token_count}")
    print(f"New balance:   {user.balance:.2f}")
    print(f"Provider ID:   {payment_provider_id}")


def stripe_payment_flow(
    stripe_settings,
    user: UserModel,
    token_count: int,
    price_id: str | None,
) -> None:
    """Create + expire a checkout session via Stripe, then print instructions."""
    stripe.api_key = stripe_settings.STRIPE_API_KEY

    if price_id:
        line_items = [{"price": price_id, "quantity": 1}]
    else:
        price_cents = token_count * stripe_settings.STRIPE_CENTS_PER_TOKEN
        line_items = [
            {
                "price_data": {
                    "currency": stripe_settings.STRIPE_CURRENCY,
                    "unit_amount": price_cents,
                    "product": stripe_settings.STRIPE_PRODUCT_ID,
                },
                "quantity": 1,
            }
        ]

    session = stripe.checkout.Session.create(
        line_items=line_items,
        mode="payment",
        success_url=stripe_settings.STRIPE_SUCCESS_URL,
        cancel_url=stripe_settings.STRIPE_CANCEL_URL,
        metadata={
            "user_id": user.id,
            "token_count": str(token_count),
        },
    )

    print(f"Checkout session created: {session.id}")
    print(f"User:          {user.email} ({user.id})")
    print(f"Tokens:        {token_count}")
    print(f"Checkout URL:  {session.url}")
    print()
    print(
        "Complete payment in the browser, then the webhook will credit the balance."
    )
    print()
    print("If using Stripe CLI for local webhooks:")
    print(
        "  stripe listen --forward-to localhost:8000/api/v1/payment/stripe/webhook"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Simulate a Stripe payment top-up."
    )

    # User identification
    user_group = parser.add_mutually_exclusive_group(required=True)
    user_group.add_argument("--email", type=str, help="User email address")
    user_group.add_argument("--user-id", type=str, help="User ID (UUID)")

    # Token source
    token_group = parser.add_mutually_exclusive_group(required=True)
    token_group.add_argument(
        "--price-id", type=str, help="Pre-defined Stripe price ID"
    )
    token_group.add_argument("--tokens", type=int, help="Custom token count")

    # Mode
    parser.add_argument(
        "--direct",
        action="store_true",
        help="Skip Stripe entirely — credit the DB directly with a fake provider ID",
    )

    args = parser.parse_args()

    stripe_settings = get_stripe_settings()
    db_settings = get_db_settings()
    engine = create_engine(db_settings.DB_URL_SYNC)

    with Session(engine) as session:
        user = resolve_user(session, args.email, args.user_id)
        token_count, resolved_price_id = resolve_tokens(
            stripe_settings, args.price_id, args.tokens
        )

        if args.direct:
            fake_provider_id = f"manual_topup_{user.id}_{token_count}"
            direct_credit(session, user, token_count, fake_provider_id)
        else:
            stripe_payment_flow(
                stripe_settings, user, token_count, resolved_price_id
            )


if __name__ == "__main__":
    main()
