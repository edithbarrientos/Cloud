import logging
from src.infraestructura.adapters.providers.baseProvider import BaseCloudProviderDAO
from typing import Dict, Any

logger = logging.getLogger("talos_chatbot_backend")

class GCPProviderDAO(BaseCloudProviderDAO):
    def __init__(self) -> None:
        self.project_id = "talos-gcp-analytics"
    async def persist_nosql_document(self, collection_name: str, document_id: str, payload: Dict[str, Any]) -> bool:
        logger.info(f"💾 [GCP_FIRESTORE] Guardando en Firestore Coleccion '{collection_name}' | ID: {document_id}")
        return True
    async def upload_media_stream(self, bucket_name: str, media_id: str, binary_data: bytes) -> str:
        return f"https://googleapis.com{bucket_name}/{media_id}.ogg"
