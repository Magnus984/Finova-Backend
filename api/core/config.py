from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DEBUG: bool = True
    PROJECT_TITLE: str = "finova-backend"
    API_V1_STR: str = "/api/v1"
    DB_NAME: str
    DB_URI: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()