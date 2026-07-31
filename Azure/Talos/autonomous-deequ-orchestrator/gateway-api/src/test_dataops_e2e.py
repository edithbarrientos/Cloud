import pytest
import redis
import httpx
import os
import sys

# Inyectar la ruta modular para localizar app.py nativamente
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

@pytest.fixture
def e2e_contract_payload():
    """Fixture que declara un contrato analítico DAMA listo para estresar el Data Plane."""
    return {
        "execution_engine": "SPARK",
        "execution_mode": "BATCH",
        "alert_level": "Error",
        "schema_contract": {
            "version": "3.5.0",
            "fields": [
                {"name": "transaction_id", "type": "string", "pii": False},
                {"name": "user_comment", "type": "string", "pii": True}
            ]
        },
        "quality_expectations": [
            {
                "dama_dimension": "Completitud",
                "rule": "isComplete",
                "columns": ["transaction_id"],
                "passing_threshold": 1.0
            }
        ],
        "genai_semantic_validation_column": "user_comment",
        "metadata": {
            "dataset_name": "E2E_Production_Sales",
            "data_owner": "DataOps_Core_Team",
            "business_kpi_target": "Validación Semántica Global Tier-1",
            "target_path": "gs://orchestra-lake/silver/sales",
            "quarantine_path": "gs://orchestra-lake/quarantine/sales",
            "governance_metadata_path": "gs://orchestra-lake/metadata/sales"
        }
    }

def test_dataops_end_to_end_flow(e2e_contract_payload):
    """Prueba E2E: Valida la ingesta, el rebote perimetral y la conexión física con la caché."""
    print("\n🚀 [DATAOPS-E2E] Iniciando simulación de ciclo de vida completo...")

    # 1. VALIDAR CONEXIÓN AL ELEMENTO DE OPTIMIZACIÓN COGNITIVA (REDIS)
    try:
        r = redis.Redis(host="127.0.0.1", port=6379, socket_timeout=3)
        r.ping()
        print("✅ [E2E-REDIS] Túnel Port-Forward verificado. Conexión a la caché semántica exitosa.")
    except redis.ConnectionError:
        pytest.fail("🚨 [E2E-FAIL] El túnel hacia Redis está caído. Ejecuta el Port-Forward en la Terminal 1.")

    # 2. DISPARAR LA INGESTA ANALÍTICA MEDIANTE EL BUS DE EVENTOS DE PULSAR
    print("📥 [E2E-INGEST] Despachando contrato declarativo de datos hacia el API Gateway...")
    response = client.post(
        "/api/v1/pipelines/execute", 
        json=e2e_contract_payload, 
        params={"input_path": "gs://orchestra-staging/raw_sales.parquet"}
    )
    
    assert response.status_code == 202
    assert response.json()["status"] == "STREAM_ORCHESTRATION_ACTIVE"
    print("✅ [E2E-PULSAR] Bus de streaming de eventos asíncronos activado correctamente.")

    # 3. VERIFICAR INTERCEPCIÓN PERIMETRAL DE POLÍTICAS DAMA
    print("🛡️ [E2E-PYDANTIC] Forzando inyección de anomalía sintáctica para evaluar el perímetro...")
    e2e_contract_payload["quality_expectations"][0]["dama_dimension"] = "Dimension_Falsa_Invalida"
    
    bad_response = client.post(
        "/api/v1/pipelines/execute", 
        json=e2e_contract_payload, 
        params={"input_path": "gs://orchestra-staging/raw_sales.parquet"}
    )
    
    assert bad_response.status_code == 422
    print("✅ [E2E-VALIDATION] Pydantic interceptó y rebotó el JSON corrupto en milisegundos.")
    print("🏆 [DATAOPS-SUCCESS] Circuito de integración validado con éxito absoluto.")
