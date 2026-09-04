from typing import Dict, Any

class TestDataFactory:
    @staticmethod
    def simular_respuesta_create(cliente_id: str) -> Dict[str, Any]:
        return {"clienteId": cliente_id, "operacion": "WORKER_INSERT", "confirmado": True}

    @staticmethod
    def simular_respuesta_read(cliente_id: str) -> Dict[str, Any]:
        return {"clienteId": cliente_id, "segmentoCorporativo": "VIP", "fuenteOrigenCertificada": "WORKER_MOCK_ANALYTICS"}
