import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List

logger = logging.getLogger("ai_agentic_core.infrastructure")

class AbstractLedgerDAO(ABC):
    @abstractmethod
    async def initialize(self) -> None: pass
    @abstractmethod
    async def save_ledger_node(self, ledger_data: Dict[str, Any], attributes_data: Dict[str, Any]) -> bool: pass
    @abstractmethod
    async def fetch_full_graph(self, trace_id: str) -> List[Dict[str, Any]]: pass
    @abstractmethod
    async def disconnect(self) -> None: pass
