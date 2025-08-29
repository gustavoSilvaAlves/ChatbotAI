from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


    OPENAI_API_KEY: str
    QDRANT_HOST: str
    QDRANT_PORT: int
    QDRANT_COLLECTION_NAME: str
    SF_INSTANCE_URL: str
    SF_ACCESS_TOKEN: str

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    KEYCLOAK_BASE_URL: str
    KEYCLOAK_REALM: str
    KEYCLOAK_CLIENT_ID: str


settings = Settings()