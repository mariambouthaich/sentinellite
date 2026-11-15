from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_USER: str = "sentinel"
    POSTGRES_PASSWORD: str = "change_me"
    POSTGRES_DB: str = "sentinellite"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    # Optionnel : si défini dans .env, remplace l'URL PostgreSQL
    # (ex: sqlite:///./dev.db pour travailler sans Docker)
    DATABASE_URL: str | None = None

    # Sécurité / JWT
    SECRET_KEY: str = "dev-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")

    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()