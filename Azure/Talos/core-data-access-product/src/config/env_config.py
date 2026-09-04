"""
Autor: EdithBG <edithbg@corporativo.internal>
Organización: Gobierno de Datos - Plataforma Transversal Core
Componente: Validador de Entorno y Credenciales Multi-Engine (EnvConfig)
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class EnvConfig(BaseSettings):
    # Control de Enrutamiento de Big Data
    TARGET_ENGINE: str = Field(default="postgres", alias="TARGET_ENGINE")
    ENVIRONMENT: str = Field(default="production", alias="ENVIRONMENT")
    
    # 🗄️ Parámetros Relacionales (Postgres)
    DATABASE_URL: str = Field(default="postgresql://localhost:5432/talos_db", alias="DATABASE_URL")
    DB_POOL_MIN_CONNECTIONS: int = Field(default=5, alias="DB_POOL_MIN_CONNECTIONS")
    DB_POOL_MAX_CONNECTIONS: int = Field(default=20, alias="DB_POOL_MAX_CONNECTIONS")
    
    # 📦 Parámetros Documentales (MongoDB)
    MONGO_CONNECTION_URI: str = Field(default="mongodb://localhost:27017/talos", alias="MONGO_CONNECTION_URI")
    
    # ❄️ Parámetros Cloud Data Warehouse (Snowflake)
    SNOWFLAKE_ACCOUNT: str = Field(default="talos-dw", alias="SNOWFLAKE_ACCOUNT")
    SNOWFLAKE_USER: str = Field(default="talos_analytics", alias="SNOWFLAKE_USER")
    SNOWFLAKE_WAREHOUSE: str = Field(default="COMPUTE_WH", alias="SNOWFLAKE_WAREHOUSE")
    
    # 🪣 Parámetros Object Storage Multi-Cloud (AWS S3 / Azure Blob)
    AWS_STORAGE_BUCKET_NAME: str = Field(default="talos-datalake-s3", alias="AWS_STORAGE_BUCKET_NAME")
    AZURE_STORAGE_CONNECTION_STRING: str = Field(default="", alias="AZURE_STORAGE_CONNECTION_STRING")
    AZURE_STORAGE_CONTAINER_NAME: str = Field(default="talos-datalake-blob", alias="AZURE_STORAGE_CONTAINER_NAME")

    # Mapeo inmutable del archivo físico local .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

env_config = EnvConfig()