from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str
    JWT_SECRET: str
    GROQ_API_KEY: str
    REDIS_HOST: str
    REDIS_PASSWORD: str

    model_config = {"env_file": ".env", "extra": "allow"}


settings = Settings()
