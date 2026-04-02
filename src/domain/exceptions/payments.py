from src.domain.exceptions.base import BaseAppException


class PaymentError(BaseAppException):
    """Base exception for payment-related errors."""

    status_code = 400

    def __init__(self, message: str = "Payment error"):
        super().__init__(message)


class InvalidPriceError(PaymentError):
    """Raised when a price_id is not in the allowed list."""

    status_code = 400

    def __init__(self, price_id: str = ""):
        if price_id:
            super().__init__(f"Invalid price ID: {price_id}")
        else:
            super().__init__("Invalid price ID.")


class InvalidTokenCountError(PaymentError):
    """Raised when a custom token count is out of allowed bounds."""

    status_code = 400

    def __init__(self, message: str = "Invalid token count"):
        super().__init__(message)


class DuplicatePaymentError(PaymentError):
    """Raised when a payment has already been processed (idempotency guard)."""

    status_code = 409

    def __init__(self, payment_provider_id: str = ""):
        if payment_provider_id:
            super().__init__(
                f"Payment already processed: {payment_provider_id}"
            )
        else:
            super().__init__("Payment already processed.")
