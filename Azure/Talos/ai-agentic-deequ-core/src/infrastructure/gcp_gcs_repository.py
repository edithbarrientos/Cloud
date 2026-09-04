import logging
from infrastructure.abstract_model_repository import AbstractModelRepository

logger = logging.getLogger("ai_agentic_core.infrastructure")

class GcpGcsRepository(AbstractModelRepository):
    """🔌 INTERFAZ ASÍNCRONA PARA GOOGLE CLOUD STORAGE (GCS)"""
    async def load_model_binary(self, remote_path: str) -> bytes:
        return b""

    async def save_model_binary(self, remote_path: str, data: bytes) -> bool:
        return True
