"""
Script to modify a user's balance.

Usage:
    python -m scripts.modify_user_balance --email user@example.com --amount 50.0
    python -m scripts.modify_user_balance --user-id abc-123 --amount -10.0

Positive amounts add to the balance, negative amounts deduct from it.
"""

import argparse
import sys

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from src.infrastructure.db.models import User as UserModel
from src.infrastructure.db.settings import get_settings


def main() -> None:
    parser = argparse.ArgumentParser(description="Modify a user's balance.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--email", type=str, help="User email address")
    group.add_argument("--user-id", type=str, help="User ID (UUID)")
    parser.add_argument(
        "--amount",
        type=float,
        required=True,
        help="Amount to add (positive) or deduct (negative)",
    )
    args = parser.parse_args()

    settings = get_settings()
    engine = create_engine(settings.DB_URL_SYNC)

    with Session(engine) as session:
        if args.email:
            query = select(UserModel).where(UserModel.email == args.email)
        else:
            query = select(UserModel).where(UserModel.id == args.user_id)

        user: UserModel | None = session.execute(query).scalar_one_or_none()

        if user is None:
            print("Error: User not found.")
            sys.exit(1)

        old_balance = user.balance
        new_balance = old_balance + args.amount

        if new_balance < 0:
            print(
                f"Error: Resulting balance would be negative ({new_balance:.2f}). "
                f"Current balance: {old_balance:.2f}"
            )
            sys.exit(1)

        user.balance = new_balance
        session.commit()
        session.refresh(user)

        print(f"User:         {user.email} ({user.id})")
        print(f"Old balance:  {old_balance:.2f}")
        print(f"Amount:       {args.amount:+.2f}")
        print(f"New balance:  {user.balance:.2f}")


if __name__ == "__main__":
    main()
