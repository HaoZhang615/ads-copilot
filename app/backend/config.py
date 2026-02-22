from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    azure_voicelive_endpoint: str = ""
    azure_voicelive_api_version: str = "2025-10-01"
    azure_voicelive_model: str = "gpt-4o"
    github_token: str = ""
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    cors_origins: str = "http://localhost:3000"
    session_ttl_seconds: int = 3600
    max_sessions_per_user: int = 5


settings = Settings()
