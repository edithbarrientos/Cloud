# 🪄 ARCHIVO PUENTE BINARIO CON SOPORTE DE CONVERSIÓN DE BYTES (HARDENED GRADE)
import json
from google.protobuf.struct_pb2 import Struct
from google.protobuf.timestamp_pb2 import Timestamp

class InferenceRequest:
    class MetricsPayload:
        def __init__(self, sensor_id="", metric_value=0.0, region=""):
            self.sensor_id = sensor_id
            self.metric_value = metric_value
            self.region = region

    def __init__(self, trace_id="", step_sequence=0, previous_hash="", metadata=None, telemetry=None, security_integrity=None):
        self.trace_id = trace_id
        self.step_sequence = step_sequence
        self.previous_hash = previous_hash
        self.metadata = metadata or {}
        self.telemetry = telemetry or self.MetricsPayload()
        self.security_integrity = security_integrity or {}

    def SerializeToString(self) -> bytes:
        """🪄 Traduce el objeto completo a bytes usando JSON compacto antes de viajar al socket HTTP/2"""
        data_dict = {
            "trace_id": self.trace_id,
            "step_sequence": self.step_sequence,
            "previous_hash": self.previous_hash,
            "metadata": self.metadata,
            "telemetry": {
                "sensor_id": self.telemetry.sensor_id,
                "metric_value": self.telemetry.metric_value,
                "region": self.telemetry.region
            },
            "security_integrity": self.security_integrity
        }
        return json.dumps(data_dict).encode('utf-8')

    @staticmethod
    def FromString(byte_data: bytes):
        """🪄 Reconstruye el objeto desde los bytes crudos del socket"""
        d = json.loads(byte_data.decode('utf-8'))
        t = InferenceRequest.MetricsPayload(
            sensor_id=d["telemetry"]["sensor_id"],
            metric_value=d["telemetry"]["metric_value"],
            region=d["telemetry"]["region"]
        )
        return InferenceRequest(
            trace_id=d["trace_id"], step_sequence=d["step_sequence"],
            previous_hash=d["previous_hash"], metadata=d["metadata"],
            telemetry=t, security_integrity=d["security_integrity"]
        )

class InferenceResponse:
    def __init__(self, trace_id="", status="", current_hash="", ledger_id=""):
        self.trace_id = trace_id
        self.status = status
        self.current_hash = current_hash
        self.ledger_id = ledger_id

    def SerializeToString(self) -> bytes:
        return json.dumps(self.__dict__).encode('utf-8')

    @staticmethod
    def FromString(byte_data: bytes):
        d = json.loads(byte_data.decode('utf-8'))
        return InferenceResponse(
            trace_id=d.get("trace_id", ""), status=d.get("status", ""),
            current_hash=d.get("current_hash", ""), ledger_id=d.get("ledger_id", "")
        )
