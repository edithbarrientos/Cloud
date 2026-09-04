from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseCloudProviderDAO(ABC):
    @abstractmethod
    async def persist_nosql_document(self, collection_name: str, document_id: str, payload: Dict[str, Any]) -> bool:
        pass
    @abstractmethod
    async def upload_media_stream(self, bucket_name: str, media_id: str, binary_data: bytes) -> str:
        pass
