import os
import logging
from typing import Dict, Any
from infrastructure.abstract_ledger_dao import AbstractLedgerDAO
from infrastructure.azure_cosmos_provider import AzureCosmosProvider
from infrastructure.aws_dynamodb_provider import AwsDynamoDBProvider
from infrastructure.gcp_firestore_provider import GcpFirestoreProvider

logger = logging.getLogger("ai_agentic_core.infrastructure")

class LedgerDAOFactory:
    _cached_instances: Dict[str, AbstractLedgerDAO] = {}

    @staticmethod
    def get_ledger_dao() -> AbstractLedgerDAO:
        provider_env = os.getenv("ACTIVE_CLOUD_PROVIDER", "azure").lower().strip()
        if provider_env not in LedgerDAOFactory._cached_instances:
            if provider_env in ["azure", "local"]:
                logger.info("[FACTORY] 🪄 Inyectando: AzureCosmosProvider")
                LedgerDAOFactory._cached_instances[provider_env] = AzureCosmosProvider()
            elif provider_env == "aws":
                logger.info("[FACTORY] 🪄 Inyectando: AwsDynamoDBProvider")
                LedgerDAOFactory._cached_instances[provider_env] = AwsDynamoDBProvider()
            elif provider_env == "gcp":
                logger.info("[FACTORY] 🪄 Inyectando: GcpFirestoreProvider")
                LedgerDAOFactory._cached_instances[provider_env] = GcpFirestoreProvider()
        return LedgerDAOFactory._cached_instances.get(provider_env, AzureCosmosProvider())
