from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str
    telegram_bot_token: str = ""
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-5-5"
    allowed_origin: str = "*"
    skip_tg_auth: bool = False
    radius_m: int = 3000

settings = Settings()
