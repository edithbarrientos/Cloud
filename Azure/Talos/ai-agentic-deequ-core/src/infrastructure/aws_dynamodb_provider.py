import os
import logging
from typing import Dict, Any, List
from infrastructure.abstract_ledger_dao import AbstractLedgerDAO

logger = logging.getLogger("ai_agentic_core.infrastructure")

class AwsDynamoDBProvider(AbstractLedgerDAO):
    def __init__(self) -> None:
        self.table_name = os.getenv("AWS_DYNAMODB_TABLE", "AiAgenticDeequLedger")
    async def initialize(self) -> None: logger.warning("[AWS_DYNAMODB] ⚠️ Modo Offline Seguro activo.")
    async def save_ledger_node(self, l_data: Dict[str, Any], a_data: Dict[str, Any]) -> bool: return True
    async def fetch_full_graph(self, trace_id: str) -> List[Dict[str, Any]]: return []
    async def disconnect(self) -> None: pass
