from typing import Annotated

import stripe
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from src.domain.exceptions.payments import (
    InvalidPriceError,
    InvalidTokenCountError,
)
from src.domain.use_cases.payments.confirm_top_up import ConfirmTopUpUseCase
from src.infrastructure.services.payment import (
    StripePaymentService,
    get_stripe_settings,
)
from src.presentation.di.auth import get_current_user_id
from src.presentation.di.payments import get_confirm_top_up_use_case
from src.presentation.di.services import get_stripe_payment_service
from src.presentation.schemas import CheckoutRequest, CheckoutResponse

router = APIRouter(prefix="/stripe", tags=["Payment"])


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout_session(
    body: CheckoutRequest,
    stripe_service: Annotated[
        StripePaymentService, Depends(get_stripe_payment_service)
    ],
    user_id: Annotated[str, Depends(get_current_user_id)],
):
    settings = get_stripe_settings()

    # Validate: exactly one of price_id or token_count must be provided
    if body.price_id and body.token_count is not None:
        raise InvalidPriceError(
            "Provide either price_id or token_count, not both."
        )
    if not body.price_id and body.token_count is None:
        raise InvalidPriceError("Provide either price_id or token_count.")

    if body.price_id:
        if body.price_id not in settings.STRIPE_TOKEN_PACKAGES:
            raise InvalidPriceError(price_id=body.price_id)

    if body.token_count is not None:
        if body.token_count < settings.STRIPE_MIN_CUSTOM_TOKENS:
            raise InvalidTokenCountError(
                f"Minimum token count is {settings.STRIPE_MIN_CUSTOM_TOKENS}"
            )
        if body.token_count > settings.STRIPE_MAX_CUSTOM_TOKENS:
            raise InvalidTokenCountError(
                f"Maximum token count is {settings.STRIPE_MAX_CUSTOM_TOKENS}"
            )

    checkout_url = await stripe_service.create_checkout_session(
        user_id=user_id,
        price_id=body.price_id,
        token_count=body.token_count,
    )

    return CheckoutResponse(checkout_url=checkout_url)


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    confirm_top_up_use_case: Annotated[
        ConfirmTopUpUseCase, Depends(get_confirm_top_up_use_case)
    ],
):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    webhook_secret = get_stripe_settings().STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=webhook_secret,
        )
    except stripe.SignatureVerificationError:
        return JSONResponse(
            content={"error": "Invalid signature"}, status_code=400
        )

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session.metadata

        user_id = metadata["user_id"] if metadata else None
        token_count_raw = metadata["token_count"] if metadata else None
        payment_intent_id = session.payment_intent

        if not user_id or not token_count_raw or not payment_intent_id:
            return JSONResponse(
                content={"error": "Missing metadata"}, status_code=400
            )

        await confirm_top_up_use_case.execute(
            user_id=user_id,
            token_count=int(token_count_raw),
            payment_provider_id=payment_intent_id,
        )

    return JSONResponse(content={"status": "success"}, status_code=200)
