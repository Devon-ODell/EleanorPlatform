from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    alpaca_key_id: str
    alpaca_secret_key: str
    alpaca_base_url: str = "https://paper-api.alpaca.markets"
    tz: str = "America/Kentucky/Louisville"
    db_url: str = "sqlite:////workspace/data/eleanor.db"
    class Config: env_file = "./compose/.env"
SET = Settings()
