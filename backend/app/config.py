from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://recoverai:recoverai@postgres:5432/recoverai"
    REDIS_URL: str = "redis://redis:6379/0"

    RAZORPAY_KEY_ID: str = "rzp_test_dummy"
    RAZORPAY_KEY_SECRET: str = "dummy_secret"
    RAZORPAY_WEBHOOK_SECRET: str = "test_webhook_secret_123"
    RAZORPAY_MODE: str = "test"

    LLM_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
