from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.config.settings import settings
from pathlib import Path
from jinja2 import Environment, select_autoescape, PackageLoader
from typing import List, Dict, Any

# Email templates directory
templates = Environment(
    loader=PackageLoader('app', 'templates/email'),
    autoescape=select_autoescape(['html', 'xml'])
)

class EmailService:
    def __init__(self):
        self.conf = ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True
        )
        self.fast_mail = FastMail(self.conf)

    async def send_email(
        self,
        subject: str,
        recipients: List[str],
        template_name: str,
        context: Dict[str, Any]
    ) -> None:
        """Send email using template"""
        template = templates.get_template(f"{template_name}.html")
        html = template.render(**context)
        
        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            html=html,
            subtype="html"
        )
        
        await self.fast_mail.send_message(message)

    async def send_welcome_email(self, email: str, username: str) -> None:
        """Send welcome email to new users"""
        await self.send_email(
            subject="Welcome to Fitness Tracker!",
            recipients=[email],
            template_name="welcome",
            context={
                "username": username
            }
        )

    async def send_password_reset(self, email: str, reset_token: str) -> None:
        """Send password reset email"""
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        await self.send_email(
            subject="Reset Your Password",
            recipients=[email],
            template_name="password_reset",
            context={
                "reset_url": reset_url
            }
        )

    async def send_subscription_confirmation(
        self,
        email: str,
        plan_name: str,
        amount: float,
        next_billing_date: str
    ) -> None:
        """Send subscription confirmation email"""
        await self.send_email(
            subject="Subscription Confirmation",
            recipients=[email],
            template_name="subscription_confirmation",
            context={
                "plan_name": plan_name,
                "amount": amount,
                "next_billing_date": next_billing_date
            }
        )
