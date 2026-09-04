import logging
from infrastructure.abstract_model_repository import AbstractModelRepository

logger = logging.getLogger("ai_agentic_core.infrastructure")

class AzureBlobRepository(AbstractModelRepository):
    """🔌 INTERFAZ ASÍNCRONA PARA AZURE BLOB STORAGE (ADLS GEN2)"""
    async def load_model_binary(self, remote_path: str) -> bytes:
        return b""

    async def save_model_binary(self, remote_path: str, data: bytes) -> bool:
        return True
