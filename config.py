"""Configuration management for Grillo Telegram Bot."""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for the bot."""

    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    # Grillo API Configuration
    GRILLO_API_URL = os.getenv("GRILLO_API_URL", "https://grillo.weeeopen.it/api/v1")
    GRILLO_API_TOKEN = os.getenv("GRILLO_API_TOKEN")

    @classmethod
    def validate(cls):
        """Validate that all required configuration is present."""
        if not cls.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

        if not cls.GRILLO_API_TOKEN:
            raise ValueError("GRILLO_API_TOKEN environment variable is required (get it from grillo web UI)")

        return True


# Export config instance
config = Config()
