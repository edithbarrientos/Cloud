import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorClient
from infrastructure.abstract_ledger_dao import AbstractLedgerDAO

logger = logging.getLogger("ai_agentic_core.infrastructure")

class AzureCosmosProvider(AbstractLedgerDAO):
    _client_shared: Optional[AsyncIOMotorClient] = None
    _db_shared = None
    _ledger_col_shared = None
    _is_db_healthy: bool = False

    def __init__(self) -> None:
        self.connection_string: str = os.getenv("COSMOS_CONNECTION_STRING", "mongodb://localhost:27017")
        self.db_name: str = os.getenv("COSMOS_DB_NAME", "deequ_cosmos_ledger")

    async def initialize(self) -> None:
        if AzureCosmosProvider._client_shared is not None: return
        try:
            AzureCosmosProvider._client_shared = AsyncIOMotorClient(
                self.connection_string, serverSelectionTimeoutMS=200, connectTimeoutMS=200
            )
            await AzureCosmosProvider._client_shared.admin.command('ping')
            AzureCosmosProvider._db_shared = AzureCosmosProvider._client_shared[self.db_name]
            AzureCosmosProvider._ledger_col_shared = AzureCosmosProvider._db_shared["agent_cognitive_ledger"]
            AzureCosmosProvider._is_db_healthy = True
            logger.info("[AZURE_COSMOS] ⚡ Pool NoSQL unificado en RAM.")
        except Exception:
            AzureCosmosProvider._is_db_healthy = False
            AzureCosmosProvider._ledger_col_shared = None
            logger.warning("[AZURE_COSMOS] ⚠️ Instancia ausente. Contingencia L1 activa.")

    async def save_ledger_node(self, ledger_data: Dict[str, Any], attributes_data: Dict[str, Any]) -> bool:
        if not AzureCosmosProvider._is_db_healthy or AzureCosmosProvider._ledger_col_shared is None: return True
        try:
            await AzureCosmosProvider._ledger_col_shared.insert_one({
                "ledger": ledger_data, "metrics": attributes_data, "cloud": "AZURE", "timestamp": datetime.utcnow().isoformat()
            })
            return True
        except Exception: return False
    async def fetch_full_graph(self, trace_id: str) -> List[Dict[str, Any]]: return []
    async def disconnect(self) -> None:
        if AzureCosmosProvider._client_shared:
            AzureCosmosProvider._client_shared.close()
            AzureCosmosProvider._client_shared = None
            AzureCosmosProvider._is_db_healthy = False
