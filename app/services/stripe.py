# import stripe
# from app.config.settings import get_settings
# from app.models.subscription import Subscription, Plan
# from sqlalchemy.orm import Session
# from datetime import datetime
# from utils.logger import logger

# settings = get_settings()

# # Configure Stripe
# stripe.api_key = settings.STRIPE_SECRET_KEY


# class StripeService:
#     @staticmethod
#     async def create_customer(email: str, name: str) -> str:
#         """Create a Stripe customer"""
#         try:
#             customer = stripe.Customer.create(email=email, name=name)
#             return customer.id
#         except stripe.error.StripeError as e:
#             logger.error(f"Error creating Stripe customer: {str(e)}")
#             raise

#     @staticmethod
#     async def create_subscription(
#         db: Session, customer_id: str, price_id: str, user_id: str, plan_id: str
#     ) -> Subscription:
#         """Create a Stripe subscription"""
#         try:
#             # Create the subscription in Stripe
#             subscription = stripe.Subscription.create(
#                 customer=customer_id,
#                 items=[{"price": price_id}],
#                 payment_behavior="default_incomplete",
#                 expand=["latest_invoice.payment_intent"],
#             )

#             # Create subscription record in database
#             db_subscription = Subscription(
#                 user_id=user_id,
#                 plan_id=plan_id,
#                 stripe_subscription_id=subscription.id,
#                 stripe_customer_id=customer_id,
#                 current_period_start=datetime.fromtimestamp(
#                     subscription.current_period_start
#                 ),
#                 current_period_end=datetime.fromtimestamp(
#                     subscription.current_period_end
#                 ),
#             )

#             db.add(db_subscription)
#             db.commit()
#             db.refresh(db_subscription)

#             return db_subscription

#         except stripe.error.StripeError as e:
#             logger.error(f"Error creating Stripe subscription: {str(e)}")
#             raise

#     @staticmethod
#     async def cancel_subscription(subscription_id: str) -> bool:
#         """Cancel a Stripe subscription"""
#         try:
#             subscription = stripe.Subscription.modify(
#                 subscription_id, cancel_at_period_end=True
#             )
#             return True
#         except stripe.error.StripeError as e:
#             logger.error(f"Error canceling Stripe subscription: {str(e)}")
#             raise

#     @staticmethod
#     async def handle_webhook(payload: dict, sig_header: str) -> dict:
#         """Handle Stripe webhook events"""
#         try:
#             event = stripe.Webhook.construct_event(
#                 payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
#             )

#             # Handle the event
#             if event.type == "customer.subscription.created":
#                 # Handle subscription created
#                 pass
#             elif event.type == "customer.subscription.updated":
#                 # Handle subscription updated
#                 pass
#             elif event.type == "customer.subscription.deleted":
#                 # Handle subscription canceled
#                 pass
#             elif event.type == "invoice.paid":
#                 # Handle successful payment
#                 pass
#             elif event.type == "invoice.payment_failed":
#                 # Handle failed payment
#                 pass

#             return {"status": "success"}

#         except stripe.error.SignatureVerificationError as e:
#             logger.error(f"Invalid signature: {str(e)}")
#             raise
#         except Exception as e:
#             logger.error(f"Error handling webhook: {str(e)}")
#             raise

#     @staticmethod
#     async def create_payment_intent(amount: int, currency: str = "usd") -> dict:
#         """Create a payment intent"""
#         try:
#             intent = stripe.PaymentIntent.create(amount=amount, currency=currency)
#             return {"client_secret": intent.client_secret}
#         except stripe.error.StripeError as e:
#             logger.error(f"Error creating payment intent: {str(e)}")
#             raise

#     @staticmethod
#     async def update_subscription(subscription_id: str, price_id: str) -> dict:
#         """Update subscription price/plan"""
#         try:
#             subscription = stripe.Subscription.retrieve(subscription_id)

#             # Update the subscription item with the new price
#             updated_subscription = stripe.Subscription.modify(
#                 subscription_id,
#                 items=[
#                     {
#                         "id": subscription["items"]["data"][0].id,
#                         "price": price_id,
#                     }
#                 ],
#             )

#             return updated_subscription
#         except stripe.error.StripeError as e:
#             logger.error(f"Error updating subscription: {str(e)}")
#             raise
