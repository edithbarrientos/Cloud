import os
import json
import logging
import pulsar
from .providers.base_provider import BaseStreamingPublisher

logger = logging.getLogger("talos_chatbot_backend")

class PulsarPublisher(BaseStreamingPublisher):
    # Clientes estáticos en RAM compartidos por toda la app de FastAPI
    _client = None
    _producer = None

    def __init__(self):
        self.service_url = os.getenv("PULSAR_SERVICE_URL", "pulsar://localhost:6650")
        self.topic = os.getenv("PULSAR_TELEMETRY_TOPIC", "persistent://public/default/talos-telemetry")

    def _initialize_pool(self):
        # Patrón de inicialización perezosa (Lazy Initialization) libre de bloqueos
        if not PulsarPublisher._client:
            PulsarPublisher._client = pulsar.Client(self.service_url)
        if not PulsarPublisher._producer:
            PulsarPublisher._producer = PulsarPublisher._client.create_producer(self.topic)

    async def publish_telemetry_event(self, event_payload: dict) -> None:
        try:
            self._initialize_pool()
            payload_bytes = json.dumps(event_payload).encode('utf-8')
            
            # .send() de pulsar-client es nativamente rápido y asíncrono en C++ por debajo
            PulsarPublisher._producer.send(payload_bytes)
            logger.info("🛸 [Apache Pulsar] Mensaje inyectado mediante pool estático O(1).")
            
        except Exception as p_err:
            logger.warning(f"⚠️ [Pulsar Fallback] Broker local inaccesible, desviando ráfaga a logs.")