import os
import logging
from typing import Dict, Type, Tuple
# Importar interfaces y adaptadores físicos en español
from src.infraestructura.adapters.providers.baseProvider import BaseCloudProviderDAO
from src.infraestructura.adapters.providers.azureProvider import AzureProviderDAO
from src.infraestructura.adapters.providers.awsProvider import AWSProviderDAO
from src.infraestructura.adapters.providers.gcpProvider import GCPProviderDAO
from src.infraestructura.adapters.pulsarPublisher import PulsarPublisher
from src.infraestructura.adapters.eventHubPublisher import EventHubPublisher

logger = logging.getLogger("talos_chatbot_backend")

class PlatformSuiteContainer:
    """📦 HARDENED SUITE CONTAINER: Contenedor inmutable del Hot Path NoSQL y el doble Cold Path de Streaming."""
    def __init__(self, db_dao: BaseCloudProviderDAO, internal_broker: PulsarPublisher, analytics_hub: EventHubPublisher) -> None:
        self.db_dao = db_dao
        self.internal_broker = internal_broker  # Autopista K8s de Apache Pulsar
        self.analytics_hub = analytics_hub      # Autopista Corporativa de Azure Event Hubs

class MultiCloudPlatformFactory:
    """
    🏭 MASTER ABSTRACT FACTORY (Registry Pattern FAANG spec):
    Resuelve el entorno Multi-Broker Híbrido de forma polimórfica en O(1) en la memoria RAM.
    Elimina por completo las sentencias condicionales if/else cumpliendo con SOLID.
    """
    _cached_suite: PlatformSuiteContainer = None

    # 🪄 DYNAMIC TRIPLE REGISTRY MAP: Inicializa de forma perezosa los Singletons de red en la RAM
    _platform_registry: Dict[str, Tuple[Type[BaseCloudProviderDAO], Type[PulsarPublisher], Type[EventHubPublisher]]] = {
        "azure": (AzureProviderDAO, PulsarPublisher, EventHubPublisher),
        "aws":   (AWSProviderDAO,   PulsarPublisher, EventHubPublisher),
        "gcp":   (GCPProviderDAO,   PulsarPublisher, EventHubPublisher)
    }

    @classmethod
    def get_platform_suite(cls) -> PlatformSuiteContainer:
        """Resuelve e instancia la Suite híbrida multinube como un Singleton en RAM."""
        if cls._cached_suite is not None:
            return cls._cached_suite

        provider_env = os.getenv("ACTIVE_CLOUD_PROVIDER", "azure").lower().strip()
        logger.info(f"🏭 [DYNAMIC_HYBRID_FACTORY] Interrogando catálogo global O(1) Match | ACTIVE_CLOUD_PROVIDER: '{provider_env.upper()}'")

        # Extracción en tiempo constante O(1) de las tres clases constructoras desde el mapa de la RAM
        suite_tuple = cls._platform_registry.get(provider_env)

        if suite_tuple is not None:
            db_class, pulsar_class, eventhub_class = suite_tuple
            # Instanciación polimórfica atómica directa en caliente de la suite completa sin if/else
            cls._cached_suite = PlatformSuiteContainer(
                db_dao=db_class(),
                internal_broker=pulsar_class(),
                analytics_hub=eventhub_class()
            )
        else:
            logger.warning(f"⚠️ [DYNAMIC_FACTORY_FALLBACK] Nube '{provider_env}' fuera de catálogo. Conmutando a AZURE Suite.")
            cls._cached_suite = PlatformSuiteContainer(AzureProviderDAO(), PulsarPublisher(), EventHubPublisher())

        logger.info(f"✅ [DYNAMIC_FACTORY_SUCCESS] Ecosistema Multi-Broker '{provider_env.upper()}' registrado nominalmente en RAM.")
        return cls._cached_suite
