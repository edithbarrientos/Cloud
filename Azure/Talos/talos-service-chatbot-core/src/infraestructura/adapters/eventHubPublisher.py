import os
import json
import logging
from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub import EventData
from .providers.base_provider import BaseStreamingPublisher

logger = logging.getLogger("talos_chatbot_backend")

class EventHubPublisher(BaseStreamingPublisher):
    _client: Optional[EventHubProducerClient] = None

    def __init__(self):
        self.conn_str = os.getenv("AZURE_EVENTHUB_CONNECTION_STRING", "Endpoint=sb://mock...")
        self.eventhub_name = os.getenv("AZURE_EVENTHUB_NAME", "talos-analytics-hub")

    def _get_client(self) -> EventHubProducerClient:
        # Reutiliza el cliente productor a través de múltiples hilos y requests
        if not EventHubPublisher._client:
            EventHubPublisher._client = EventHubProducerClient.from_connection_string(
                self.conn_str, 
                event_hub_name=self.eventhub_name
            )
        return EventHubPublisher._client

    async def publish_telemetry_event(self, event_payload: dict) -> None:
        if "mock" in self.conn_str:
            logger.info("⚡ [EventHub MOCK] Evento analítico amortiguado en memoria.")
            return

        try:
            producer = self._get_client()
            # Optimizamos creando un lote atómico directo
            async with producer:
                event_data_batch = await producer.create_batch()
                event_data_batch.add(EventData(json.dumps(event_payload)))
                await producer.send_batch(event_data_batch)
        except Exception as e:
            logger.error(f"🔴 [EventHub Error] Fallo crítico de red en streaming: {str(e)}")
            raise e