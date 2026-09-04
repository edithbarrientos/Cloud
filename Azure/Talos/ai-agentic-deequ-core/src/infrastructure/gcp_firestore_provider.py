import os
import logging
from typing import Dict, Any, List
from infrastructure.abstract_ledger_dao import AbstractLedgerDAO

logger = logging.getLogger("ai_agentic_core.infrastructure")

class GcpFirestoreProvider(AbstractLedgerDAO):
    def __init__(self) -> None:
        self.project_id = os.getenv("GCP_PROJECT_ID", "talos-ai-core")
    async def initialize(self) -> None: logger.warning("[GCP_FIRESTORE] ⚠️ Modo Offline Seguro activo.")
    async def save_ledger_node(self, l_data: Dict[str, Any], a_data: Dict[str, Any]) -> bool: return True
    async def fetch_full_graph(self, trace_id: str) -> List[Dict[str, Any]]: return []
    async def disconnect(self) -> None: pass
