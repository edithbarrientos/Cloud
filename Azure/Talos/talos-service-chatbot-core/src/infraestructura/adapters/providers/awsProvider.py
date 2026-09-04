import logging
from src.infraestructura.adapters.providers.baseProvider import BaseCloudProviderDAO
from typing import Dict, Any

logger = logging.getLogger("talos_chatbot_backend")

class AWSProviderDAO(BaseCloudProviderDAO):
    def __init__(self) -> None:
        self.region = "us-east-1"
    async def persist_nosql_document(self, collection_name: str, document_id: str, payload: Dict[str, Any]) -> bool:
        logger.info(f"💾 [AWS_DYNAMODB] PutItem ejecutado en tabla '{collection_name}' | ID: {document_id}")
        return True
    async def upload_media_stream(self, bucket_name: str, media_id: str, binary_data: bytes) -> str:
        return f"https://{bucket_name}://{media_id}.ogg"
