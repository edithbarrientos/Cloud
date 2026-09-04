import pytest
from ai_agentic_core.supervisor import QualityDataSupervisor

@pytest.mark.asyncio
async def test_stress_integrity_handshake():
    supervisor = QualityDataSupervisor()
    payload = {
        "sensor_id": "STRESS-NODE",
        "metric_value": 0.55,
        "region": "us-west-1"
    }
    response = await supervisor.process_inference_ingestion(
        raw_data=payload,
        previous_hash="72285bcd8a0f024a740c0cfebb0d4563bde4305fa2d622880d119367e57a7888",
        step_sequence=2
    )
    assert response["status"] == "SUCCESS"
    assert response["orchestration_details"]["execution_status"] == "CONSOLIDATED"
