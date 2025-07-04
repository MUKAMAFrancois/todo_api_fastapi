from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from core.config import settings
from pathlib import Path

# Mail configuration
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent.parent.parent / 'templates'
)

async def send_reset_password_email(email_to: str, token: str):
    """
    Sends a password reset email to the user.
    """
    reset_url = f"{settings.CLIENT_URL}/reset-password?token={token}"
    message = MessageSchema(
        subject="Password Reset Request",
        recipients=[email_to],
        template_body={"reset_url": reset_url},
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message, template_name="email.html") 