from pydantic import BaseSettings

class EmailSettings(BaseSettings):
    # Email Server Settings
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 587  # For TLS
    MAIL_USE_TLS: bool = True
    MAIL_USE_SSL: bool = False
    
    # Email Login Credentials
    MAIL_USERNAME: str = "your-email@gmail.com"  # Replace with your Gmail
    MAIL_PASSWORD: str = "your-app-password"      # Use Gmail App Password, not your regular password
    
    # Default sender
    MAIL_DEFAULT_SENDER: str = "your-email@gmail.com"
    
    class Config:
        env_file = ".env"

email_settings = EmailSettings()
