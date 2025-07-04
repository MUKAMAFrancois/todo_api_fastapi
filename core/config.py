from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # This model_config tells pydantic-settings to:
    # 1. Load variables from a file named ".env".
    # 2. Use UTF-8 encoding for the file.
    # 3. Treat environment variable names as case-insensitive.
    model_config = SettingsConfigDict(
        env_file="../.env", 
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Database settings
    MONGODB_URI: str
    DATABASE_NAME: str

    # App name
    APP_NAME: str = "TodoApp"

    # JWT settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Email settings
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False

    # Client URL for frontend links
    CLIENT_URL: str = "http://localhost:3000"

# Create a single instance of the settings to be used throughout the application
settings = Settings() 