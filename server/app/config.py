from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite+pysqlite:///./dev.db"
    jwt_secret: str = "dev-secret"
    jwt_expire_minutes: int = 10080
    admin_username: str = "admin"
    admin_password: str = "admin123456"
    llm_enabled: bool = False
    llm_base_url: str = ""
    llm_api_key: str = ""
    llm_model: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
