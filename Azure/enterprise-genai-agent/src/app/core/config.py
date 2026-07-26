# src/app/core/config.py
"""Módulo de configuración centralizada del ecosistema de IA Generativa.

Carga, parsea y valida de forma estricta las variables de entorno del sistema
utilizando Pydantic Settings V2 antes de permitir el inicio de la aplicación.
"""

__author__ = "Edith BG"
__date__ = "2026-07-26"
__version__ = "1.2.0"
__status__ = "Production Ready"

import logging
from pydantic import HttpUrl, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("EnterpriseGenAI.Config")


class AppConfig(BaseSettings):
    """Contrato de configuración inmutable para el entorno de producción."""

    # ==============================================================================
    # 1. VARIABLES DE GOBERNANZA Y ENTORNO
    # ==============================================================================
    ambiente: str = "dev"  # Opciones válidas habituales: dev, qa, prod

    # ==============================================================================
    # 2. CONEXIÓN AL BACKEND DE INTELIGENCIA ARTIFICIAL (AZURE OPENAI)
    # ==============================================================================
    azure_openai_endpoint: HttpUrl
    
    # Se usa SecretStr para evitar que la API Key se imprima accidentalmente en los logs
    azure_openai_api_key: SecretStr
    
    # Nombre físico del despliegue en Azure OpenAI (ej: gpt-5-nano-deployment, gpt-4o-mini)
    azure_openai_deployment_name: str = "gpt-4o-mini"
    
    # Versión de la API de inferencia de Microsoft Azure
    azure_openai_api_version: str = "2024-08-01-preview"

    # ==============================================================================
    # 3. CONEXIÓN PERIMETRAL AL ERP CORPORATIVO
    # ==============================================================================
    erp_api_url: HttpUrl

    # ==============================================================================
    # 4. CONFIGURACIÓN DEL MOTOR DE ENTORNO (PROVEEDOR DE PYDANTIC)
    # ==============================================================================
    model_config = SettingsConfigDict(
        # Busca un archivo .env local, ideal para desarrollo sin tocar variables globales
        env_file=".env",
        env_file_encoding="utf-8",
        # Si en Azure se inyectan variables extras, no rompe la inicialización de la app
        extra="ignore",
        # Permite coincidencia de nombres sin importar si están en minúsculas o mayúsculas
        case_sensitive=False
    )

    # ==============================================================================
    # 5. VALIDACIONES ESTRICTAS DE SEGURIDAD (CUSTOM VALIDATORS)
    # ==============================================================================
    @field_validator("azure_openai_api_key")
    @classmethod
    def validar_api_key_no_vacia(cls, v: SecretStr) -> SecretStr:
        """Asegura que la clave secreta contenga caracteres reales antes del arranque."""
        if not v.get_secret_value().strip():
            raise ValueError("La variable AZURE_OPENAI_API_KEY no puede estar vacía o contener solo espacios.")
        return v


# Instancia de inicialización rápida para validar la salud del módulo al importarse
if __name__ == "__main__":
    import sys
    # Configuración de logs básica para depuración de este script aislado
    logging.basicConfig(level=logging.INFO)
    try:
        logger.info("Probando inicialización estricta de variables...")
        config = AppConfig()
        logger.info(f"✅ Configuración cargada con éxito. Ambiente detectado: {config.ambiente}")
    except Exception as err:
        logger.critical(f"❌ Fallo crítico de validación en variables obligatorias: {err}")
        sys.exit(1)