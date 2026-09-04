import pytest
from ai_agentic_core.supervisor import QualityDataSupervisor

@pytest.mark.asyncio
async def test_supervisor_inference_flow():
    supervisor = QualityDataSupervisor()
    payload = {
        "sensor_id": "ARM64-M3-TEST",
        "metric_value": 0.92,
        "region": "us-east-2"
    }
    response = await supervisor.process_inference_ingestion(
        raw_data=payload,
        previous_hash="0000000000000000000000000000",
        step_sequence=1
    )
    assert response["status"] == "SUCCESS"
    assert "security_integrity" in response
    assert response["orchestration_details"]["execution_status"] == "CONSOLIDATED"
