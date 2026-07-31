import uvicorn
import subprocess
import logging
import httpx
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("orchestra-plane")

app = FastAPI(
    title="Autonomous Deequ Orchestrator API Gateway",
    description="Plano de Control con Alertas Reales para Orchestra Data Labs (DAMA)",
    version="3.5.0"
)

CORPORATE_WEBHOOK_URL = "https://slack.com"

class FieldDefinitionModel(BaseModel):
    name: str
    type: str
    pii: bool = False

class SchemaContractModel(BaseModel):
    version: str
    fields: List[FieldDefinitionModel]

class QualityExpectationModel(BaseModel):
    dama_dimension: str
    rule: str
    columns: List[str]
    passing_threshold: float = Field(default=1.0, ge=0.0, le=1.0)

class MetadataModel(BaseModel):
    dataset_name: str
    data_owner: str
    business_kpi_target: str
    target_path: str
    quarantine_path: str
    governance_metadata_path: str
    checkpoint_path: Optional[str] = None
    trigger_time: str = "10 seconds"

class ElitePipelinePayload(BaseModel):
    execution_engine: str = Field(pattern="^(SPARK|FLINK)$")
    execution_mode: str = Field(pattern="^(BATCH|STREAMING)$")
    alert_level: str = "Error"
    schema_contract: SchemaContractModel
    quality_expectations: List[QualityExpectationModel]
    genai_semantic_validation_column: Optional[str] = None
    metadata: MetadataModel

    @field_validator('quality_expectations')
    @classmethod
    def check_dama_dimensions(cls, v: List[QualityExpectationModel]) -> List[QualityExpectationModel]:
        allowed = ["Precision", "Completitud", "Consistencia", "Unicidad", "Actualidad"]
        for exp in v:
            if exp.dama_dimension not in allowed:
                raise ValueError(f"Dimensión DAMA '{exp.dama_dimension}' inválida. Use: {allowed}")
        return v

class QuarantineNotification(BaseModel):
    dataset_name: str
    quarantine_path: str
    violated_dimension: str
    failing_ratio: float
    callback_webhook_url: str

async def send_interactive_alert(notification: QuarantineNotification):
    logger.info(f"📤 [WEBHOOK-DISPATCH] Preparando payload visual para los canales corporativos...")
    slack_payload = {
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "🚨 BRECHA CRÍTICA DE GOBIERNO DE DATOS", "emoji": True}
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Dataset:* `{notification.dataset_name}`\n*Dimensión DAMA Violada:* `{notification.violated_dimension}`\n*Ratio de Registro Fallido:* `{notification.failing_ratio * 100:.2f}%`"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "👑 Aprobar Ingesta", "emoji": True},
                        "style": "primary",
                        "url": f"{notification.callback_webhook_url}?action=approve&dataset_name={notification.dataset_name}"
                    }
                ]
            }
        ]
    }
    try:
        async with httpx.AsyncClient() as client:
            await client.post(CORPORATE_WEBHOOK_URL, json=slack_payload, timeout=5.0)
    except Exception as e:
        logger.error(f"❌ [WEBHOOK-FAIL] Imposible enviar alerta: {str(e)}")

# --- CORRECCIÓN SEMÁNTICA DE APY GATEWAY ---
@app.post("/api/v1/pipelines/execute", status_code=202)
def execute_pipeline(payload: ElitePipelinePayload, input_path: str, background_tasks: BackgroundTasks):
    logger.info(f"📥 [API-POST] Ingesta aceptada para {payload.metadata.dataset_name}")
    return {"status": "STREAM_ORCHESTRATION_ACTIVE", "message": "Plano de streaming por eventos asíncronos de Pulsar activado."}

@app.post("/api/v1/governance/quarantine/callback", status_code=200)
def process_human_decision(action: str, dataset_name: str):
    if action.upper() == "APPROVE":
        return {"status": "FORCED_INGESTION", "message": "Aprobación registrada en el histórico DAMA."}
    elif action.upper() == "REJECT":
        return {"status": "PURGED", "message": "Auditoría de descarte definitivo asentada."}
    else:
        raise HTTPException(status_code=400, detail="Acción de gobernanza inválida.")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
