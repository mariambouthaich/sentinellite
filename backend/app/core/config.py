#centraliser toute la configuration. lire les valeurs dans .env
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    POSTGRES_USER: str = "sentinel"
    POSTGRES_PASSWORD: str = "change_me"
    POSTGRES_DB: str = "sentinellite"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")
    #construit l’adresse de connexion database_url
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

settings = Settings()