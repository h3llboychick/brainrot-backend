from functools import lru_cache

import stripe

from src.infrastructure.logging import get_logger

from .settings import StripeSettings, get_stripe_settings

logger = get_logger(__name__)


class StripePaymentService:
    def __init__(self, settings: StripeSettings):
        self.settings = settings
        stripe.api_key = settings.STRIPE_API_KEY

    def _resolve_line_items_and_tokens(
        self,
        price_id: str | None,
        token_count: int | None,
    ) -> tuple[list[dict], int]:
        """
        Resolve the checkout line_items and token_count from either
        a pre-defined package (price_id) or custom amount (token_count).

        Returns (line_items, token_count).
        """
        if price_id:
            tokens = self.settings.STRIPE_TOKEN_PACKAGES[price_id]
            line_items = [{"price": price_id, "quantity": 1}]
            return line_items, tokens

        # Custom amount
        price_cents = token_count * self.settings.STRIPE_CENTS_PER_TOKEN  # type: ignore
        line_items = [
            {
                "price_data": {
                    "currency": self.settings.STRIPE_CURRENCY,
                    "unit_amount": price_cents,
                    "product": self.settings.STRIPE_PRODUCT_ID,
                },
                "quantity": 1,
            }
        ]
        return line_items, token_count  # type: ignore

    async def create_checkout_session(
        self,
        user_id: str,
        price_id: str | None = None,
        token_count: int | None = None,
    ) -> str:
        """
        Create a Stripe Checkout session.

        Provide either price_id (pre-defined package) or token_count (custom).
        Returns the checkout session URL.
        """
        line_items, resolved_tokens = self._resolve_line_items_and_tokens(
            price_id=price_id,
            token_count=token_count,
        )

        try:
            session = await stripe.checkout.Session.create_async(
                line_items=line_items,
                mode="payment",
                success_url=self.settings.STRIPE_SUCCESS_URL,
                cancel_url=self.settings.STRIPE_CANCEL_URL,
                metadata={
                    "user_id": user_id,
                    "token_count": str(resolved_tokens),
                },
            )
            return session.url
        except stripe.RateLimitError:
            logger.error(
                "Stripe rate limit hit while creating checkout session"
            )
            raise
        except Exception as e:
            logger.error(f"Error creating checkout session: {e}")
            raise


@lru_cache()
def get_stripe_service() -> StripePaymentService:
    settings = get_stripe_settings()
    return StripePaymentService(settings=settings)
