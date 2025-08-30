# app/services/email.py
from __future__ import annotations
from typing import Any, Dict, Iterable, Optional, TypedDict
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from fastapi_mail.errors import ConnectionErrors
from jinja2 import Environment, select_autoescape, PackageLoader, FileSystemLoader
from app.config.settings import get_settings
from pydantic import EmailStr
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
settings = get_settings()

# Choose a loader that works both packaged & local
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates" / "email"
if TEMPLATES_DIR.exists():
    loader = FileSystemLoader(str(TEMPLATES_DIR))
else:
    loader = PackageLoader("app", "templates/email")

templates = Environment(
    loader=loader,
    autoescape=select_autoescape(["html", "xml"]),
)

class EmailContext(TypedDict, total=False):
    subject: str

class EmailService:
    _instance: "EmailService" | None = None

    def __new__(cls) -> "EmailService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # singleton
        self.conf = ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>",
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_STARTTLS=bool(settings.MAIL_STARTTLS),
            MAIL_SSL_TLS=bool(settings.MAIL_SSL_TLS),
            USE_CREDENTIALS=bool(settings.MAIL_USE_CREDENTIALS),
            MAIL_DEBUG=False,
        )
        self.fast_mail = FastMail(self.conf)

    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        # Inject common variables available to all templates
        context = {"subject": context.get("subject"), **context}
        template = templates.get_template(f"{template_name}.html")
        return template.render(**context)

    async def send(  # single generic entrypoint
        self,
        *,
        subject: str,
        recipients: Iterable[EmailStr],
        template: str,
        context: Dict[str, Any],
        text_body: Optional[str] = None,
        reply_to: Optional[str] = None,
        cc: Optional[Iterable[EmailStr]] = None,
        bcc: Optional[Iterable[EmailStr]] = None,
    ) -> None:
        html = self.render(template, {**context, "subject": subject})
        message = MessageSchema(
            subject=subject,
            recipients=list(recipients),
            cc=list(cc) if cc else [],
            bcc=list(bcc) if bcc else [],
            # reply_to=reply_to,
            body=text_body,       # plain-text alternative (optional)
            html=html,            # html body
            subtype="html",
        )
        try:
            await self.fast_mail.send_message(message)
            logger.info("Email sent: template=%s recipients=%s", template, recipients)
        except ConnectionErrors as e:
            logger.exception("Email send failed: %s", e)
            raise

    async def send_welcome_email(self, email: EmailStr, username: str) -> None:
        await self.send(
            subject="Welcome to Fitness Tracker!",
            recipients=[email],
            template="welcome",
            context={"username": username},
            text_body=f"Welcome, {username}! We're excited to have you.",
        )

    async def send_password_reset(self, email: EmailStr, reset_token: str) -> None:
        await self.send(
            subject="Reset Your Password",
            recipients=[email],
            template="password_reset",
            context={"reset_token": str(reset_token)},
            text_body=f"Open this link to reset your password: {str(reset_token)}",
        )

    async def send_subscription_confirmation(
        self, email: EmailStr, plan_name: str, amount: float, next_billing_date: str
    ) -> None:
        await self.send(
            subject="Subscription Confirmation",
            recipients=[email],
            template="subscription_confirmation",
            context={
                "plan_name": plan_name,
                "amount": amount,
                "next_billing_date": next_billing_date,
            },
            text_body=(
                f"Your subscription to {plan_name} is confirmed. "
                f"Amount: {amount}. Next billing: {next_billing_date}."
            ),
        )
