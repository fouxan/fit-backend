# """
# Stripe product and price configuration.
# Update these values with your actual Stripe product and price IDs.
# """

# from app.models.subscription import PlanType, PLAN_FEATURES

# STRIPE_PRODUCTS = {
#     PlanType.FREE: {
#         "name": "Free Plan",
#         "description": "Basic fitness tracking features",
#         "price": 0,
#         "stripe_price_id": None,  # Free plan doesn't need a price ID
#         "features": PLAN_FEATURES[PlanType.FREE]
#     },
#     PlanType.PLUS: {
#         "name": "Plus Plan",
#         "description": "Advanced features with more workout storage",
#         "price": 999,  # $9.99
#         "stripe_price_id": "your_plus_plan_price_id_here",  # Update this
#         "features": PLAN_FEATURES[PlanType.PLUS]
#     },
#     PlanType.PRO: {
#         "name": "Pro Plan",
#         "description": "Unlimited features with priority support",
#         "price": 1999,  # $19.99
#         "stripe_price_id": "your_pro_plan_price_id_here",  # Update this
#         "features": PLAN_FEATURES[PlanType.PRO]
#     }
# }

# # Webhook events to monitor
# MONITORED_STRIPE_EVENTS = [
#     'customer.subscription.created',
#     'customer.subscription.updated',
#     'customer.subscription.deleted',
#     'invoice.paid',
#     'invoice.payment_failed',
#     'customer.created',
#     'payment_intent.succeeded',
#     'payment_intent.payment_failed'
# ]
