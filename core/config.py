from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
class Settings(BaseSettings):
    database_host: str
    database_port: int
    database_name: str
    database_user: str
    database_password: str

    jwt_secret_key: str
    jwt_algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int

    upload_dir: str = str(BASE_DIR / "uploads")
    repos_dir: str = str(BASE_DIR / "repos")
    max_zip_size_mb: int = 50
    max_file_size_mb: int = 10

    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.6-flash"

    # ---- Email / SMTP ----
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = "lam20052802@gmail.com"
    smtp_password: str = ""
    smtp_from_name: str = "ReviewCodeWeb"
    smtp_from_email: str = "lam20052802@gmail.com"
    email_enabled: bool = False

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra="ignore",
    )
settings = Settings()


