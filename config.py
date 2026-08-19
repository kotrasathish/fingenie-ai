import os

from dotenv import load_dotenv

load_dotenv()


class Settings:

    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./fingenie.db"
    )

    ENVIRONMENT: str = os.getenv(
        "ENVIRONMENT",
        "development"
    )

    DEBUG: bool = os.getenv(
        "DEBUG",
        "false"
    ).lower() == "true"


settings = Settings()