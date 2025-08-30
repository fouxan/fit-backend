# from fastapi import Request, HTTPException
# from fastapi_limiter import FastAPILimiter
# from fastapi_limiter.depends import RateLimiter
# from app.models.subscription import PLAN_FEATURES, PlanType
# from app.services.user import UserService
# import redis.asyncio as redis
# from app.config.settings import get_settings
# from utils.logger import logger

# settings = get_settings()

# # Initialize Redis connection
# redis_instance = None


# async def init_redis():
#     """Initialize Redis connection"""
#     global redis_instance
#     redis_instance = await redis.from_url(
#         settings.REDIS_URL,
#         encoding="utf-8",
#         decode_responses=True
#     )
#     await FastAPILimiter.init(redis_instance)


# def get_user_rate_limit(request: Request) -> int:
#     """Get rate limit based on user's subscription plan"""
#     try:
#         user = request.state.user
#         if not user:
#             return PLAN_FEATURES[PlanType.FREE]["api_rate_limit"]
        
#         # Get user's active subscription
#         active_subscription = UserService.get_active_subscription(user.id)
#         if not active_subscription:
#             return PLAN_FEATURES[PlanType.FREE]["api_rate_limit"]
        
#         return PLAN_FEATURES[active_subscription.plan.type]["api_rate_limit"]
#     except Exception as e:
#         logger.error(f"Error determining rate limit: {str(e)}")
#         return PLAN_FEATURES[PlanType.FREE]["api_rate_limit"]


# class DynamicRateLimiter(RateLimiter):
#     """Rate limiter with dynamic limits based on subscription"""
    
#     async def __call__(self, request: Request):
#         if not redis_instance:
#             await init_redis()
        
#         # Get rate limit for the user
#         rate_limit = get_user_rate_limit(request)
        
#         # Create identifier (e.g., IP + user_id if authenticated)
#         identifier = f"rate_limit:{request.client.host}"
#         if hasattr(request.state, "user") and request.state.user:
#             identifier = f"{identifier}:{request.state.user.id}"
        
#         # Check rate limit
#         current = await redis_instance.get(identifier)
#         if current is not None and int(current) >= rate_limit:
#             raise HTTPException(
#                 status_code=429,
#                 detail="Too many requests"
#             )
        
#         # Update counter
#         pipeline = redis_instance.pipeline()
#         pipeline.incr(identifier)
#         pipeline.expire(identifier, 3600)  # Reset after 1 hour
#         await pipeline.execute()


# rate_limiter = DynamicRateLimiter()
