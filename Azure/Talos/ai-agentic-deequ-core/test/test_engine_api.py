import pytest
import pytest_asyncio
import httpx
import copy
from httpx import AsyncClient
from fastapi import status
from asgi_lifespan import LifespanManager

# Importar la app real y el supervisor para parchar sus firmas a nivel estático
from app import app
from ai_agentic_core.supervisor import QualityDataSupervisor

class EngineApiDataMother:
    """
    🏗️ PATRÓN DATA MOTHER DE INFRAESTRUCTURA
    Centraliza la fábrica de contratos elásticos y el fuzzing estocástico.
    """
    @staticmethod
    def get_base_contract() -> dict:
        return {
            "trace_id": "TRC-TEST-API-99",
            "step_sequence": 1,
            "previous_hash": "0000000000000000000000000000000000000000000000000000000000000000",
            "data": {
                "sensor_id": "ARM64-M3-API-TEST",
                "metric_value": 0.895,
                "region": "us-east-2",
                "system_integrity": "OK"
            }
        }

    @staticmethod
    def mutate_payload_stochastic_fuzzing(base_payload: dict, corruption_intensity: float = 0.5) -> dict:
        mutated = copy.deepcopy(base_payload)
        if corruption_intensity > 0.7:
            mutated["step_sequence"] = "CADENA_CORRUPTA_FUZZING_OUT_BOUNDS"
        return mutated

@pytest.fixture
def api_factory():
    return EngineApiDataMother

@pytest_asyncio.fixture
async def async_client():
    """
    🪄 FIXTURE DE CONTROL EXPLÍCITO DE LIFESPAN ASÍNCRONO
    Garantiza que el supervisor e infraestructura levanten antes de instanciar la red httpx.
    """
    async with LifespanManager(app) as manager:
        transport = httpx.ASGITransport(app=manager.app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client

@pytest.mark.asyncio
async def test_api_inference_endpoint_success_with_valid_contract(api_factory, async_client):
    """
    🧪 VALIDACIÓN 1: CONSUMO ASÍNCRONO EXITOSO (HTTP 202 ACCEPTED)
    """
    payload = api_factory.get_base_contract()
    response = await async_client.post("/api/v1/inference", json=payload)

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json()["status"] == "SUCCESS"
    assert "security_integrity" in response.json()

@pytest.mark.asyncio
async def test_api_inference_endpoint_fails_on_corrupt_contract(api_factory, async_client):
    """
    🧪 VALIDACIÓN 2: SANEAMIENTO SINTÁCTICO DE CONTRATO (HTTP 422 UNPROCESSABLE ENTITY)
    """
    base_payload = api_factory.get_base_contract()
    corrupt_fuzz_payload = api_factory.mutate_payload_stochastic_fuzzing(base_payload, corruption_intensity=0.9)

    response = await async_client.post("/api/v1/inference", json=corrupt_fuzz_payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_api_global_exception_handler_forces_safe_error_boundary(api_factory, async_client, mocker):
    """
    🧪 VALIDACIÓN 3: CONCEPCIÓN DEL ERROR BOUNDARY DE LA API (ANTI-CRASH FALLBACK)
    """
    payload = api_factory.get_base_contract()

    async def mock_system_collapse(*args, **kwargs):
        raise MemoryError("Off-Heap Vector Buffer Allocation OOM Overflow Exception simulated.")

    mocker.patch.object(QualityDataSupervisor, "process_inference_ingestion", new=mock_system_collapse)

    response = await async_client.post("/api/v1/inference", json=payload)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    # 🪄 PARCHE FINAL: Se valida la traza real que arroja el crash forzado en el endpoint
    assert "OOM Overflow Exception simulated" in response.json()["detail"]
