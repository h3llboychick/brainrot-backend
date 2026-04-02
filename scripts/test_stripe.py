import argparse
import logging
import os

import dotenv
import stripe

logger = logging.getLogger(__name__)


dotenv.load_dotenv()
stripe.api_key = os.getenv("STRIPE_API_KEY")


def test_subscription(subscription_id: str):
    subscription = stripe.Subscription.retrieve(subscription_id)
    latest_invoice_id = subscription.latest_invoice
    customer_id = subscription.customer

    logger.info(
        f"Testing subscription payment for customer {customer_id} and subscription {subscription_id}"
    )
    payment_method = stripe.PaymentMethod.attach(
        payment_method="pm_card_visa",
        customer=subscription.customer,
    )
    stripe.Customer.modify(
        id=customer_id,
        invoice_settings={
            "default_payment_method": payment_method.id,
        },
    )
    logger.info(
        f"Attached payment method {payment_method.id} to customer {customer_id} and set as default"
    )

    subscription = stripe.Subscription.retrieve(subscription_id)
    latest_invoice_id = subscription.latest_invoice
    logger.info(
        f"Paying latest invoice {latest_invoice_id} for subscription {subscription_id}"
    )

    invoice = stripe.Invoice.pay(latest_invoice_id)

    if invoice.status == "paid":
        logger.info(
            f"Successfully processed subscription payment for subscription {subscription_id}"
        )
    else:
        logger.error(
            f"Failed to process subscription payment for subscription {subscription_id}. Invoice status: {invoice.status}"
        )


def test_payment_intent(payment_intent_id: str):
    logger.info(
        f"Testing one-time payment for payment intent {payment_intent_id}"
    )

    payment_response = stripe.PaymentIntent.confirm(
        intent=payment_intent_id, payment_method="pm_card_visa"
    )

    if payment_response.status == "succeeded":
        logger.info(
            f"Successfully processed one-time payment for payment intent {payment_intent_id}"
        )
    else:
        logger.error(
            f"Failed to process one-time payment for payment intent {payment_intent_id}. Status: {payment_response.status}"
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Test Stripe payment")
    parser.add_argument(
        "mode",
        choices=["subscription", "one_time"],
        help="Payment mode to test",
    )
    parser.add_argument(
        "--customer_id", help="Stripe customer ID for subscription test"
    )
    parser.add_argument(
        "--subscription_id", help="Stripe subscription ID for subscription test"
    )
    parser.add_argument(
        "--payment_intent_id",
        help="Stripe payment intent ID for one-time payment test",
    )

    args = parser.parse_args()

    if args.mode == "subscription":
        if not args.subscription_id:
            logger.error("Subscription ID is required for subscription test")
        else:
            test_subscription(args.subscription_id)
    elif args.mode == "one_time":
        if not args.payment_intent_id:
            logger.error(
                "Payment Intent ID is required for one-time payment test"
            )
        else:
            test_payment_intent(args.payment_intent_id)
