from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "IntelliPlant AI"
    app_version: str = "1.0.0"
    debug: bool = True
    secret_key: str = "intelliplant-secret-key-change-in-production"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    database_url: str = "sqlite:///./app/db/intelliplant.db"
    postgres_url: str = "postgresql+asyncpg://user:password@localhost:5432/intelliplant"

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""

    redis_url: str = "redis://localhost:6379"

    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "intelliplant-docs"

    llm_provider: str = "openai"
    openai_api_key: str = ""
    gemini_api_key: str = ""
    groq_api_key: str = ""

    embedding_model: str = "BAAI/bge-large-en-v1.5"
    llm_model: str = "gpt-4o"
    chunk_size: int = 1024
    chunk_overlap: int = 200
    max_upload_size: int = 52428800
    cors_origins: str = "*"
    auth_enabled: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
