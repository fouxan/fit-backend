from math import e
from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.subscription import SubscriptionService
from app.config.settings import settings
import stripe
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
subscription_service = SubscriptionService()


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Stripe webhook events"""
    try:
        # Get the webhook signature
        sig_header = request.headers.get("stripe-signature")
        if not sig_header:
            raise HTTPException(status_code=400, detail="No signature header")
        
        # Get the webhook body
        payload = await request.body()
        
        # Verify the event
        try:
            event = stripe.Webhook.construct_event(
                payload,
                sig_header,
                settings.STRIPE_WEBHOOK_SECRET
            )
        except stripe.error.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        # Handle the event
        await subscription_service.handle_webhook_event(
            event_type=event.type,
            event_data=event.data.object,
            db=db
        )
        
        return {"status": "success"}
    except HTTPException as e:
        logger.error(f"HTTPException: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
