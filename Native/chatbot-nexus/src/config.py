import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # 🔌 TOPOLOGÍA DE RED CENTRALIZADA: Lee de las variables de entorno inyectadas
    redis_url: str = Field(default="redis://127.0.0.1:6379/0", validation_alias="REDIS_URL")
    ollama_api_url: str = Field(default="http://127.0.0.1:11434", validation_alias="OLLAMA_API_URL")
    qdrant_url: str = Field(default="http://127.0.0.1:6333", validation_alias="QDRANT_URL")
    
    # Parámetros algorítmicos globales del modelo
    model_name: str = "qwen2.5:0.5b"
    circuit_failure_threshold: int = 3
    circuit_recovery_time: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
