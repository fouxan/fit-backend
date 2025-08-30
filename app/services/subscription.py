# from typing import Optional
# from sqlalchemy.orm import Session
# from datetime import datetime, timedelta
# from app.models.subscription import Subscription, Plan, PlanType
# from app.models.user import User
# from app.services.stripe import StripeService
# from app.config.stripe_config import STRIPE_PRODUCTS
# from app.services.email import EmailService
# from utils.logger import logger


# class SubscriptionService:
#     def __init__(self):
#         self.stripe_service = StripeService()
#         self.email_service = EmailService()

#     async def create_initial_subscription(
#         self,
#         db: Session,
#         user: User,
#         plan_type: PlanType,
#         payment_method_id: Optional[str] = None
#     ) -> Subscription:
#         """
#         Create initial subscription for a new user
#         """
#         try:
#             # Get or create plan in database
#             plan = self._get_or_create_plan(db, plan_type)
            
#             # For free plan, just create the subscription record
#             if plan_type == PlanType.FREE:
#                 return await self._create_free_subscription(db, user, plan)
            
#             # For paid plans, handle payment and create Stripe subscription
#             if not payment_method_id:
#                 raise ValueError("Payment method required for paid plans")
            
#             # Create or get Stripe customer
#             stripe_customer_id = await self.stripe_service.create_customer(
#                 email=user.email,
#                 name=user.full_name or user.username
#             )
            
#             # Create Stripe subscription
#             stripe_subscription = await self.stripe_service.create_subscription(
#                 db=db,
#                 customer_id=stripe_customer_id,
#                 price_id=STRIPE_PRODUCTS[plan_type]["stripe_price_id"],
#                 user_id=str(user.id),
#                 plan_id=str(plan.id)
#             )
            
#             # Send confirmation email
#             await self.email_service.send_subscription_confirmation(
#                 email=user.email,
#                 plan_name=plan.name,
#                 amount=plan.price / 100,  # Convert cents to dollars
#                 next_billing_date=stripe_subscription.current_period_end.strftime("%Y-%m-%d")
#             )
            
#             return stripe_subscription

#         except Exception as e:
#             logger.error(f"Error creating subscription: {str(e)}")
#             # If paid plan fails, create free plan subscription as fallback
#             if plan_type != PlanType.FREE:
#                 logger.info("Falling back to free plan")
#                 return await self._create_free_subscription(
#                     db,
#                     user,
#                     self._get_or_create_plan(db, PlanType.FREE)
#                 )
#             raise

#     async def _create_free_subscription(
#         self,
#         db: Session,
#         user: User,
#         plan: Plan
#     ) -> Subscription:
#         """Create a free subscription"""
#         subscription = Subscription(
#             user_id=user.id,
#             plan_id=plan.id,
#             is_active=True,
#             current_period_start=datetime.utcnow(),
#             current_period_end=datetime.utcnow() + timedelta(days=36500)  # 100 years
#         )
#         db.add(subscription)
#         db.commit()
#         db.refresh(subscription)
#         return subscription

#     def _get_or_create_plan(self, db: Session, plan_type: PlanType) -> Plan:
#         """Get or create a plan in the database"""
#         plan = db.query(Plan).filter(Plan.type == plan_type).first()
#         if not plan:
#             plan = Plan(
#                 name=STRIPE_PRODUCTS[plan_type]["name"],
#                 type=plan_type,
#                 description=STRIPE_PRODUCTS[plan_type]["description"],
#                 price=STRIPE_PRODUCTS[plan_type]["price"],
#                 stripe_price_id=STRIPE_PRODUCTS[plan_type]["stripe_price_id"],
#                 features=STRIPE_PRODUCTS[plan_type]["features"]
#             )
#             db.add(plan)
#             db.commit()
#             db.refresh(plan)
#         return plan

#     async def handle_webhook_event(self, event_type: str, event_data: dict, db: Session):
#         """Handle Stripe webhook events"""
#         handlers = {
#             'customer.subscription.created': self._handle_subscription_created,
#             'customer.subscription.updated': self._handle_subscription_updated,
#             'customer.subscription.deleted': self._handle_subscription_deleted,
#             'invoice.paid': self._handle_invoice_paid,
#             'invoice.payment_failed': self._handle_payment_failed
#         }
        
#         handler = handlers.get(event_type)
#         if handler:
#             await handler(event_data, db)

#     async def _handle_subscription_created(self, event_data: dict, db: Session):
#         """Handle subscription created event"""
#         subscription_id = event_data['id']
#         customer_id = event_data['customer']
        
#         # Update subscription status
#         db_subscription = db.query(Subscription).filter(
#             Subscription.stripe_subscription_id == subscription_id
#         ).first()
        
#         if db_subscription:
#             db_subscription.is_active = True
#             db_subscription.current_period_start = datetime.fromtimestamp(
#                 event_data['current_period_start']
#             )
#             db_subscription.current_period_end = datetime.fromtimestamp(
#                 event_data['current_period_end']
#             )
#             db.commit()

#     async def _handle_subscription_updated(self, event_data: dict, db: Session):
#         """Handle subscription updated event"""
#         subscription_id = event_data['id']
        
#         db_subscription = db.query(Subscription).filter(
#             Subscription.stripe_subscription_id == subscription_id
#         ).first()
        
#         if db_subscription:
#             db_subscription.current_period_end = datetime.fromtimestamp(
#                 event_data['current_period_end']
#             )
#             db_subscription.cancel_at_period_end = event_data.get(
#                 'cancel_at_period_end', False
#             )
#             db.commit()

#     async def _handle_subscription_deleted(self, event_data: dict, db: Session):
#         """Handle subscription deleted event"""
#         subscription_id = event_data['id']
        
#         db_subscription = db.query(Subscription).filter(
#             Subscription.stripe_subscription_id == subscription_id
#         ).first()
        
#         if db_subscription:
#             # Create new free plan subscription
#             free_plan = self._get_or_create_plan(db, PlanType.FREE)
#             await self._create_free_subscription(
#                 db,
#                 db_subscription.user,
#                 free_plan
#             )
            
#             # Deactivate old subscription
#             db_subscription.is_active = False
#             db.commit()

#     async def _handle_invoice_paid(self, event_data: dict, db: Session):
#         """Handle successful payment"""
#         subscription_id = event_data['subscription']
        
#         if subscription_id:
#             db_subscription = db.query(Subscription).filter(
#                 Subscription.stripe_subscription_id == subscription_id
#             ).first()
            
#             if db_subscription:
#                 # Update subscription status and dates
#                 db_subscription.is_active = True
#                 db_subscription.current_period_end = datetime.fromtimestamp(
#                     event_data['lines']['data'][0]['period']['end']
#                 )
#                 db.commit()
                
#                 # Send success email
#                 await self.email_service.send_subscription_confirmation(
#                     email=db_subscription.user.email,
#                     plan_name=db_subscription.plan.name,
#                     amount=event_data['amount_paid'] / 100,
#                     next_billing_date=db_subscription.current_period_end.strftime("%Y-%m-%d")
#                 )

#     async def _handle_payment_failed(self, event_data: dict, db: Session):
#         """Handle failed payment"""
#         subscription_id = event_data['subscription']
        
#         if subscription_id:
#             db_subscription = db.query(Subscription).filter(
#                 Subscription.stripe_subscription_id == subscription_id
#             ).first()
            
#             if db_subscription:
#                 # Send failure notification
#                 # You might want to implement a payment_failed email template
#                 pass
