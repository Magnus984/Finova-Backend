from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DEBUG: bool = True
    PROJECT_TITLE: str = "finova-backend"
    API_V1_STR: str = "/api/v1"
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()