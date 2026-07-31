import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

# Cabecera mandatoria requerida por el perímetro de aislamiento DAMA en app.py
HEADERS_VALIDOS = {"X-Tenant-ID": "tenant-talos-poc-01"}

@pytest.fixture
def valid_payload():
    """Genera un payload base estructurado que cumple exactamente con el contrato de datos."""
    return {
        "execution_engine": "SPARK",
        "execution_mode": "BATCH",
        "alert_level": "Error",
        "schema_contract": {
            "version": "1.0.0",
            "fields": [{"name": "transaction_id", "type": "string", "pii": False}]
        },
        "quality_expectations": [
            {
                "dama_dimension": "Completitud",
                "rule": "isComplete",
                "columns": ["transaction_id"],
                "passing_threshold": 1.0
            }
        ],
        "metadata": {
            "cloud_provider": "AZURE",
            "storage_path": "abfss://raw@datalake.dfs.core.windows.net/"
        }
    }

def test_execute_pipeline_success(valid_payload):
    """Caso 1: El contrato es válido y lleva el Tenant-ID. Debe responder 202."""
    response = client.post(
        "/api/v1/pipelines/execute",
        json=valid_payload,
        params={"input_path": "gs://source/batch.parquet"},
        headers=HEADERS_VALIDOS
    )
    assert response.status_code == 202

def test_execute_pipeline_invalid_dama_dimension(valid_payload):
    """Caso 2: Inyección de un umbral fuera de rango. Pydantic intercepta y responde 422."""
    # Modificamos un parámetro numérico con restricción ge=0.0 y le=1.0 para forzar el quiebre de Pydantic
    valid_payload["quality_expectations"][0]["passing_threshold"] = 5.5

    response = client.post(
        "/api/v1/pipelines/execute",
        json=valid_payload,
        params={"input_path": "gs://source/batch.parquet"},
        headers=HEADERS_VALIDOS
    )
    assert response.status_code == 422

def test_governance_callback_approve():
    """Caso 3: Simulación del clic de aprobación del Data Owner con cabecera perimetral. Responde 200 OK."""
    response = client.post(
        "/api/v1/governance/quarantine/callback",
        params={"action": "approve", "dataset_name": "Core_Transactions"},
        headers=HEADERS_VALIDOS
    )
    assert response.status_code == 200
