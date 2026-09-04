import spacy
import logging
from pathlib import Path
from typing import Dict
from src.config.settings import settings

logger = logging.getLogger("AI-Tenant-Router")

class TenantRouter:
    """
    🧮 ENRUTADOR DINÁMICO MULTICLIENTE DE MODELOS (AI DESIGN PATTERN)
    Administra la carga perezosa (Lazy Loading) y el aislamiento en memoria RAM
    de los artefactos y tuberías lingüísticas de spaCy indexadas por cada Tenant.
    """
    def __init__(self):
        # Almacén centralizado de hilos de inferencia cargados en memoria RAM
        self._loaded_models: Dict[str, spacy.language.Language] = {}
        
        # Inicialización y validación del pipeline genérico de resguardo
        self._default_model_name = settings.DEFAULT_NLP_MODEL
        self._models_store = settings.MODELS_STORE_PATH
        
        logger.info(f"🔀 [TenantRouter] Inicializado. Almacén de artefactos: [{self._models_store}]")

    def get_pipeline(self, tenant_id: str) -> spacy.language.Language:
        """
        Intercepta el tenantId y recupera de forma segura su tubería de IA aislada.
        Si el modelo no reside en la caché de la RAM, ejecuta una carga en caliente desde el disco.
        
        @param tenant_id Identificador único del inquilino proveniente de Flink.
        @return Instancia activa del modelo lingüístico de spaCy listo para inferencia.
        """
        # Saneamiento perimetral del identificador de entrada
        clean_tenant = tenant_id.strip()
        
        # CASO 1: Éxito en Caché (Mínima latencia de lectura)
        if clean_tenant in self._loaded_models:
            return self._loaded_models[clean_tenant]
            
        # CASO 2: Carga en Caliente (Lazy Loading) desde el repositorio físico models_store
        tenant_model_path = self._models_store / clean_tenant
        
        # Validamos si el cliente tiene un cerebro de Machine Learning personalizado en disco
        if tenant_model_path.exists() and tenant_model_path.is_dir():
            try:
                logger.info(f"🔀 [TenantRouter] Modelo personalizado detectado para Tenant: [{clean_tenant}]. Cargando en RAM...")
                # Carga de pesos binarios y meta-datos del cliente desde su directorio absoluto
                nlp_instance = spacy.load(tenant_model_path)
                
                # Registramos en la caché para las siguientes ráfagas de streaming de Flink
                self._loaded_models[clean_tenant] = nlp_instance
                return nlp_instance
            except Exception as e:
                logger.error(f"💥 [TenantRouter] Error cargando modelo personalizado para [{clean_tenant}]: {str(e)}")
                # Si los binarios del cliente están corruptos, aplica el Patrón de Resguardo Predictivo
                return self._get_default_fallback_pipeline(clean_tenant)
        else:
            # CASO 3: El cliente no requiere IA personalizada; se le asigna el modelo base global
            return self._get_default_fallback_pipeline(clean_tenant)

    def _get_default_fallback_pipeline(self, tenant_id: str) -> spacy.language.Language:
        """Entrega el pipeline base del sistema operativo registrándolo de forma segura."""
        if self._default_model_name not in self._loaded_models:
            logger.info(f"🪐 [TenantRouter] Cargando por primera vez el modelo base global: [{self._default_model_name}]")
            try:
                self._loaded_models[self._default_model_name] = spacy.load(self._default_model_name)
            except Exception as e:
                logger.critical(f"🚨 [TenantRouter] Fallo catastrófico. No se localizó spaCy base en el contenedor: {str(e)}")
                raise RuntimeError(f"Fallo de inicialización de spaCy base: {str(e)}")
                
        # Vinculamos temporalmente la caché para no re-procesar el disco en la siguiente llamada
        return self._loaded_models[self._default_model_name]

# Instancia global del enrutador elástico inyectable en controladores
tenant_router = TenantRouter()
