from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_kubernetes_health_probe():
    """🎯 Valida que la sonda de salud (Liveness Probe) retorne estado saludable."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "HEALTHY"

def test_endpoints_rejects_empty_protobuf_buffer():
    """🔌 Verifica que la compuerta de red rechace peticiones sin bytes con código 400."""
    headers = {"X-Tenant-ID": "test-tenant-invalid"}
    response = client.post("/v1/analyze", content=b"", headers=headers)
    
    assert response.status_code == 400
    assert response.json()["status"] == "ERROR"
    assert "bytes legibles" in response.json()["reason"]
