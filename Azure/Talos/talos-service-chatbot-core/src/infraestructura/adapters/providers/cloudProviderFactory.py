import os
import logging
from typing import Dict, Type
from src.infrastructure.adapters.providers.baseProvider import BaseCloudProviderDAO
from src.infrastructure.adapters.providers.azureProvider import AzureProviderDAO
from src.infrastructure.adapters.providers.awsProvider import AWSProviderDAO
from src.infrastructure.adapters.providers.gcpProvider import GCPProviderDAO

logger = logging.getLogger("talos_chatbot_backend")

class CloudProviderFactory:
    """
    🏭 ABSTRACT FACTORY MASTER (Registry Pattern Standard):
    Aísla las conexiones multinube y resuelve el polimorfismo en tiempo constante O(1).
    Cumple estrictamente con el principio Abierto/Cerrado (SOLID) al eliminar condicionales.
    """
    _cached_dao: BaseCloudProviderDAO = None

    # 🪄 REGISTRY PATTERN: Mapeo dinámico indexado en la RAM
    _provider_registry: Dict[str, Type[BaseCloudProviderDAO]] = {
        "azure": AzureProviderDAO,
        "aws":   AWSProviderDAO,
        "gcp":   GCPProviderDAO
    }

    @classmethod
    def get_provider_dao(cls) -> BaseCloudProviderDAO:
        """Resuelve e instancia la estrategia cloud en caliente de forma Singleton."""
        # 1. Reutilizar la referencia en memoria si ya fue instanciada (Singleton provision)
        if cls._cached_dao is not None:
            return cls._cached_dao

        # 2. Interrogar la variable de entorno activa inyectada en el runtime de la Mac
        provider_env = os.getenv("ACTIVE_CLOUD_PROVIDER", "azure").lower().strip()
        logger.info(f"🏭 [CLOUD_REGISTRY_FACTORY] Escaneando entorno. ACTIVE_CLOUD_PROVIDER activo: '{provider_env.upper()}'")

        # 3. O(1) REGISTRY MATCH: Obtener la clase del constructor directo desde el diccionario de RAM
        provider_class = cls._provider_registry.get(provider_env)

        if provider_class is not None:
            # Instanciación dinámica polimórfica en caliente sin condicionales if/else
            cls._cached_dao = provider_class()
        else:
            # SafeGuard / Fallback reactivo ante variables de entorno malformadas
            logger.warning(f"⚠️ [FACTORY_FALLBACK] Proveedor '{provider_env}' fuera de especificación. Conmutando a AZURE Failover.")
            cls._cached_dao = AzureProviderDAO()

        return cls._cached_dao
