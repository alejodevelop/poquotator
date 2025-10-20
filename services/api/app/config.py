from pydantic_settings import BaseSettings


class Settings(BaseSettings):
app_env: str = "local"
app_host: str = "0.0.0.0"
app_port: int = 8000
redis_url: str
mailhog_api: str
erp_base_url: str
erp_api_key: str


class Config:
env_file = ".env"


settings = Settings()