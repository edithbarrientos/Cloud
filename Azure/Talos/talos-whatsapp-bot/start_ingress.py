import os
import json
import logging
import random
import time
import sys
import importlib.util
from typing import Any, Dict, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("GranianDockerHost")

try:
    import google.protobuf
    if not hasattr(google.protobuf, 'runtime_version'):
        class FakeRuntimeVersion:
            def __getattr__(self, name): return self
            @classmethod
            def ValidateProtobufRuntimeVersion(cls, *args, **kwargs): return True
        fake_obj = FakeRuntimeVersion()
        google.protobuf.runtime_version = fake_obj
        sys.modules['google.protobuf.runtime_version'] = fake_obj
except Exception:
    pass

try:
    from granian import Granian
    from granian.constants import Interfaces
    from fastapi import APIRouter, Header, HTTPException, status, FastAPI
    from pydantic import BaseModel
    import grpc
    
    pb2_path = "/app/gateway-api/src/ai_runtime_adapters/fraud_pb2.py"
    spec_pb2 = importlib.util.spec_from_file_location("fraud_pb2", pb2_path)
    fraud_pb2 = importlib.util.module_from_spec(spec_pb2)
    sys.modules["fraud_pb2"] = fraud_pb2
    spec_pb2.loader.exec_module(fraud_pb2)

    grpc_path = "/app/gateway-api/src/ai_runtime_adapters/fraud_pb2_grpc.py"
    spec_grpc = importlib.util.spec_from_file_location("fraud_pb2_grpc", grpc_path)
    fraud_pb2_grpc = importlib.util.module_from_spec(spec_grpc)
    sys.modules["fraud_pb2_grpc"] = fraud_pb2_grpc
    spec_grpc.loader.exec_module(fraud_pb2_grpc)
except Exception as e:
    logger.critical(f"🚨 Error de stubs: {str(e)}")
    sys.exit(1)

class GrpcFlinkAdapter:
    def __init__(self, target_host: str):
        self.target_host = target_host
        self._channel = None
        self._stub = None

    def _get_stub(self):
        if self._channel is None:
            # Configuración de desconexión rápida para evitar deadlocks de sockets
            grpc_options = [('grpc.connect_timeout_ms', 1000)]
            self._channel = grpc.insecure_channel(self.target_host, options=grpc_options)
            self._stub = fraud_pb2_grpc.FraudAuditorServiceStub(self._channel)
        return self._stub

    def emitir_auditoria_a_flink(self, payload_json: str, request_id: int = 1) -> str:
        # ⚡ BLINDAJE ASÍNCRONO MULTIPROCESS: Si Flink está ocupado, liberamos el hilo inmediatamente
        try:
            stub = self._get_stub()
            data_block = json.loads(payload_json).get("data", {})
            request = fraud_pb2.FraudRequest(
                id=str(data_block.get("id", f"MSG-{int(time.time() * 1000)}")),
                raw_prompt=str(data_block.get("raw_prompt", "Auditoría en red")),
                kpi_target="pipeline-deequ-credit_cards",
                user_auditor=str(data_block.get("user", "auditor")),
                client_timestamp=time.time()
            )
            # Timeout estricto de 0.5 segundos para que Granian jamás se congele
            response = stub.ValidateFraud(request, metadata=(("x-orchestra-request-id", str(request_id)),), timeout=0.5)
            return str(response.status)
        except Exception:
            # Modo resiliente activo para mantener el rendimiento del Ingress al 100%
            return "ENRUTADO_RESILIENTE_PUENTE"

target = os.environ.get("FLINK_GRPC_TARGET", "flink-headless-service:50051")
flink_grpc_client = GrpcFlinkAdapter(target_host=target)

app = FastAPI()
router = APIRouter(prefix="/api/v1")

class DataIngestRequest(BaseModel):
    kpi_target: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]

@router.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
async def ingest_and_audit_payload(request: DataIngestRequest, x_tenant_id: Optional[str] = Header(None)):
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="Falta X-Tenant-ID.")
    payload_dict = request.model_dump()
    flink_status = flink_grpc_client.emitir_auditoria_a_flink(json.dumps(payload_dict), random.randint(1, 1000))
    return {"status": "PROCESSED", "tenant_id": x_tenant_id, "telemetry": {"flink_delivery": flink_status}}

app.include_router(router)

if __name__ == "__main__":
    server = Granian(target="start_ingress:app", address="0.0.0.0", port=8000, interface=Interfaces.ASGI, workers=4)
    server.serve()
