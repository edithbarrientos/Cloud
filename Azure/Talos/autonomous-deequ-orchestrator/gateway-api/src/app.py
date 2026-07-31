import os
import logging
import asyncio
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from fastapi import FastAPI, Header, HTTPException, status, Query

# Configuración estricta del Logger Corporativo
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("ADO-GatewayAPI-Tier1")

BUS_PROVIDER = os.getenv("EVENT_BUS_PROVIDER", "PULSAR").upper()

# Clientes globales compartidos inicializados por el ciclo lifespan
pulsar_client = None
pulsar_producer = None
azure_producer_client = None

class FieldDefinition(BaseModel):
    name: str = Field(..., min_length=1)
    type: str = Field(...)
    pii: bool = Field(default=False)

class SchemaContract(BaseModel):
    version: str = Field(...)
    fields: List[FieldDefinition]

class QualityExpectation(BaseModel):
    damaDimension: str = Field(...)
    rule: str = Field(...)
    columns: List[str]
    passingThreshold: float = Field(default=1.0, ge=0.0, le=1.0)

class AdaptiveMetadata(BaseModel):
    datasetName: str
    dataOwner: str
    businessKpiTarget: str
    targetPath: str
    quarantinePath: str
    governanceMetadataPath: str
    checkpointPath: Optional[str] = None
    triggerTime: str = "10 seconds"
    estimatedBatchSizeBytes: int = Field(default=0, ge=0)
    # ⚡ EXTENSIÓN TIER-1: Correo dinámico validado por Pydantic
    notificationEmailTo: EmailStr = Field(default="data_governance@orchestralabs.io", description="Destinatario del log consolidado")
    tenantId: str = "shared"
    executionId: str = ""

class ElitePipelinePayload(BaseModel):
    executionEngine: str = Field(default="SPARK")
    executionMode: str = Field(default="BATCH")
    alertLevel: str = "Error"
    schemaContract: SchemaContract
    qualityExpectations: List[QualityExpectation]
    genaiSemanticValidationColumn: Optional[str] = None
    metadata: AdaptiveMetadata

@asynccontextmanager
async def application_lifespan(app: FastAPI):
    global pulsar_client, pulsar_producer, azure_producer_client
    logger.info(f"🎻 [STARTUP-LIFESPAN] Inicializando conectores de red para el bus: {BUS_PROVIDER}")
    
    if BUS_PROVIDER == "AZURE":
        try:
            from azure.eventhub.aio import EventHubProducerClient
            conn_str = os.getenv("AZURE_EVENTHUB_CONNECTION_STRING", "Endpoint=sb://mock.servicebus.windows.net/;SharedAccessKeyName=mock;SharedAccessKey=mock")
            eh_name = os.getenv("AZURE_EVENTHUB_NAME", "ado-pipeline-execution-v1")
            azure_producer_client = EventHubProducerClient.from_connection_string(conn_str=conn_str, eventhub_name=eh_name)
            logger.info("🔌 [LIFESPAN-AZURE] Pool de conexiones AMQP establecido exitosamente.")
        except Exception as e:
            logger.error(f"❌ [LIFESPAN-AZURE-FAIL] Imposible inicializar Event Hubs: {str(e)}")

    elif BUS_PROVIDER == "PULSAR":
        try:
            import pulsar
            service_url = os.getenv("PULSAR_SERVICE_URL", "pulsar://localhost:6650")
            topic_name = os.getenv("PULSAR_TOPIC", "persistent://public/default/ado-pipeline-execution-v1")
            pulsar_client = pulsar.Client(service_url)
            pulsar_producer = pulsar_client.create_producer(topic_name, block_if_queue_full=True, max_pending_messages=2000)
            logger.info("🔌 [LIFESPAN-PULSAR] Productor asíncrono soberano de Apache Pulsar conectado.")
        except Exception as e:
            logger.error(f"❌ [LIFESPAN-PULSAR-FAIL] Imposible conectar al clúster de Pulsar: {str(e)}")

    yield
    
    logger.info("🛑 [SHUTDOWN-LIFESPAN] Cerrando de forma segura sockets e hilos asíncronos...")
    if azure_producer_client:
        await azure_producer_client.close()
    if pulsar_producer:
        pulsar_producer.close()
    if pulsar_client:
        pulsar_client.close()
    logger.info("✅ [SHUTDOWN-COMPLETE] Desconexión limpia ejecutada.")

app = FastAPI(title="Orchestra ADO Control Plane Gateway", version="4.0.0", lifespan=application_lifespan)

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "HEALTHY", "bus_active": BUS_PROVIDER}

@app.post("/api/v1/pipelines/execute", status_code=status.HTTP_202_ACCEPTED)
@app.post("/api/v1/pipeline/execute", status_code=status.HTTP_202_ACCEPTED)
async def execute_pipeline(
    payload: ElitePipelinePayload,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID", description="Clave mandatoria de aislamiento DAMA")
):
    logger.info(f"📥 [API-REQUEST] Recibiendo contrato. Target: {x_tenant_id} | Notificar a: {payload.metadata.notificationEmailTo}")
    
    import uuid
    execution_id = str(uuid.uuid4())
    payload.metadata.tenantId = x_tenant_id
    payload.metadata.executionId = execution_id
    
    json_string_payload = payload.model_dump_json()

    if BUS_PROVIDER == "AZURE":
        if not azure_producer_client: raise HTTPException(status_code=503, detail="AMQP Azure no disponible")
        try:
            from azure.eventhub import EventData
            event_batch = await azure_producer_client.create_batch(partition_key=x_tenant_id)
            event_batch.add(EventData(json_string_payload))
            await azure_producer_client.send_batch(event_batch)
            logger.info(f"🚀 [DESPACHO-AZURE] Manifiesto enviado con exito. ID: {execution_id}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    elif BUS_PROVIDER == "PULSAR":
        if not pulsar_producer: raise HTTPException(status_code=503, detail="Pulsar no inicializado")
        try:
            pulsar_producer.send(json_string_payload.encode('utf-8'), partition_key=x_tenant_id)
            logger.info(f"🚀 [DESPACHO-PULSAR] Manifiesto inyectado asíncronamente en Pulsar. ID: {execution_id}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return {"status": "ACCEPTED", "execution_id": execution_id, "tenant_id": x_tenant_id, "assigned_bus": BUS_PROVIDER}
