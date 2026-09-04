import logging
from src.infraestructura.adapters.providers.baseProvider import BaseCloudProviderDAO
from typing import Dict, Any

logger = logging.getLogger("talos_chatbot_backend")

class AzureProviderDAO(BaseCloudProviderDAO):
    def __init__(self) -> None:
        self.endpoint = "https://azure.com"
    async def persist_nosql_document(self, collection_name: str, document_id: str, payload: Dict[str, Any]) -> bool:
        logger.info(f"💾 [AZURE_COSMOS] Documento guardado en Cosmos DB | ID: {document_id}")
        return True
    async def upload_media_stream(self, bucket_name: str, media_id: str, binary_data: bytes) -> str:
        return f"https://windows.net{bucket_name}/{media_id}.ogg"
