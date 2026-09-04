from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path
from typing import List
import logging

class Settings(BaseSettings):
    """
    🪐 CONFIGURACIÓN GLOBAL TIPIFICADA DE LA IA (PYDANTIC V2)
    Administra, valida e inyecta de forma automatizada las variables 
    de entorno del sistema operativo dentro del contenedor de Kubernetes.
    """
    # ==============================================================================
    # 📋 1. METADATA Y CONFIGURACIÓN DEL CONTENEDOR
    # ==============================================================================
    APP_NAME: str = "AI-NLP-Brain-Engine"
    APP_ENV: str = "production"
    DEBUG: bool = False
    
    # Parámetros del Servidor Web Asíncrono ASGI (Uvicorn)
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 🛡️ Orígenes Permitidos (CORS) para restringir el acceso perimetral de red
    ALLOWED_HOSTS: List[str] = ["*"]

    # ==============================================================================
    # 🧠 2. INFRAESTRUCTURA DE MODELOS DE INTELIGENCIA ARTIFICIAL
    # ==============================================================================
    # Modelo NLP base preentrenado de spaCy en español (CNN + Vectores estáticos)
    DEFAULT_NLP_MODEL: str = "es_core_news_sm"
    
    # Umbral mínimo de confianza probabilística tolerado para clasificar intenciones (60%)
    INTENT_CONFIDENCE_THRESHOLD: float = 0.60
    
    # 🛠️ CÓMPUTO SEGURO DE RUTAS: Ruta absoluta del almacén de artefactos por cliente
    # Resuelve dinámicamente la ubicación física del disco duro del Pod
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    MODELS_STORE_PATH: Path = BASE_DIR / "models_store"

    # ==============================================================================
    # ⚙️ 3. MÁQUINA DE CONFIGURACIÓN DEL ENTORNO
    # ==============================================================================
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        frozen=True,
        case_sensitive=True
    )

@lru_cache()
def get_settings() -> Settings:
    """
    Patrón Singleton con Caché (LRU): Garantiza que el archivo de propiedades
    se lea del disco una sola vez. Incorpora logs de inicialización perimetral.
    """
    # Inicialización local de bootstrap para auditoría de arranque
    bootstrap_logger = logging.getLogger("AI-Settings-Bootstrap")
    
    # Instanciación y validación de tipos estricta por Pydantic v2
    config_instance = Settings()
    
    # 📡 [LOG DE ARRANQUE INMUNE]: Confirma la integridad de las rutas computadas en K8s
    bootstrap_logger.info(
        f"⚙️  [Settings] Propiedades cargadas. Ambiente: [{config_instance.APP_ENV}]. "
        f"Ruta de artefactos IA validada en: [{config_instance.MODELS_STORE_PATH}]"
    )
    
    return config_instance

# Instancia global inyectable lista para el ecosistema de IA
settings = get_settings()
