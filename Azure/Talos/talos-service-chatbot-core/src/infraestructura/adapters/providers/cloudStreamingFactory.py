import logging

logger = logging.getLogger("talos_chatbot_backend")

class AWSKinesisMock:
    async def publish_telemetry_event(self, payload: dict) -> bool:
        logger.info(f"📡 [MOCKED_AWS_KINESIS] Streaming en AWS Kinesis | ID: {payload.get('correlationId')}")
        return True

class GCPPubSubMock:
    async def publish_telemetry_event(self, payload: dict) -> bool:
        logger.info(f"📡 [MOCKED_GCP_PUBSUB] Publicando en GCP Pub/Sub | ID: {payload.get('correlationId')}")
        return True
