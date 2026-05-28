from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PSQL_HOST: str
    PSQL_DB: str
    PSQL_USER: str
    PSQL_PASSWORD: str
    PSQL_PORT: int
    PIPEFY_PIPE_ID: str = "PIPE_ID_SIMULADO"
    PIPEFY_FIELD_CLIENTE_NOME: str = "cliente_nome"
    PIPEFY_FIELD_CLIENTE_EMAIL: str = "cliente_email"
    PIPEFY_FIELD_VALOR_PATRIMONIO: str = "valor_patrimonio"
    PIPEFY_FIELD_STATUS: str = "status"
    PIPEFY_FIELD_PRIORIDADE: str = "prioridade"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.PSQL_USER}:{self.PSQL_PASSWORD}"
            f"@{self.PSQL_HOST}:{self.PSQL_PORT}/{self.PSQL_DB}"
        )

settings = Settings()
