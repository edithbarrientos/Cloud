import os
import sys

# ⚡ CORE FIX ANTI-FRICCIÓN: Forzamos a Python a buscar primero en las librerías globales limpias del contenedor
# Esto evita que el volumen compartido de la Mac ensucie el entorno de Protobuf
global_packages = "/usr/local/lib/python3.10/dist-packages"
if global_packages in sys.path:
    sys.path.remove(global_packages)
sys.path.insert(0, global_packages)

# Forzamos la resolución DNS nativa del sistema operativo
os.environ["GRPC_DNS_RESOLVER"] = "native"

import random
import time
from typing import Any, Dict, Optional
from fastapi import Header, HTTPException, status, FastAPI
from pydantic import BaseModel
import grpc

# Acople milimétrico de la subcarpeta física de tus stubs locales
STUBS_PATH = "/app/gateway-api/src/ai_runtime_adapters"
if STUBS_PATH not in sys.path:
    sys.path.append(STUBS_PATH)

import fraud_pb2
import fraud_pb2_grpc

app = FastAPI()

class DataIngestRequest(BaseModel):
    kpi_target: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]

@app.post("/api/v1/ingest", status_code=status.HTTP_202_ACCEPTED)
def ingest_payload(request: DataIngestRequest, x_tenant_id: Optional[str] = Header(None)):
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="Falta X-Tenant-ID corporativo.")
    
    payload_dict = request.model_dump()
    data_block = payload_dict.get("data", {})
    
    grpc_options = [
        ('grpc.keepalive_time_ms', 5000),
        ('grpc.keepalive_timeout_ms', 5000),
        ('grpc.connect_timeout_ms', 10000),
        ('grpc.max_receive_message_length', 100 * 1024 * 1024)
    ]
    
    # Conexión local interna de memoria para acoplar tus scripts asíncronos
    with grpc.insecure_channel('127.0.0.1:50051', options=grpc_options) as channel:
        stub = fraud_pb2_grpc.FraudAuditorServiceStub(channel)
        
        grpc_req = fraud_pb2.FraudRequest(
            id=str(data_block.get("id", f"MSG-{int(time.time() * 1000)}")),
            raw_prompt=str(data_block.get("raw_prompt", "Auditoría perimetral de flujo")),
            kpi_target=str(payload_dict.get("kpi_target")),
            user_auditor=str(data_block.get("user", "auditor_sre")),
            client_timestamp=time.time()
        )
        
        try:
            response = stub.ValidateFraud(grpc_req, timeout=5.0)
            flink_status = str(response.status)
        except Exception as e:
            flink_status = f"FAIL_GRPC_ROUTING: {str(e)}"
    
    return {
        "status": "PROCESSED",
        "tenant_id": x_tenant_id,
        "telemetry": {"flink_delivery": flink_status}
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("start_ingress:app", host="0.0.0.0", port=8000)
