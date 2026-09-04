# -*- coding: utf-8 -*-
import time
from ai_agentic_core.interceptors.base_interceptor import BaseCognitiveInterceptor
from typing import Dict, Any

class TelemetryInterceptor(BaseCognitiveInterceptor):
    """Plugin de Observabilidad encargado de auditar latencias y telemetría de CPU."""
    def __init__(self):
        super().__init__()
        self._timers: Dict[str, float] = {}

    async def _execute_pre(self, tenant_id: str, json_payload: Dict[str, Any]) -> Dict[str, Any]:
        self._timers[tenant_id] = time.perf_counter()
        return json_payload

    async def _execute_post(self, tenant_id: str, report_data: Dict[str, Any]) -> Dict[str, Any]:
        start = self._timers.pop(tenant_id, time.perf_counter())
        elapsed = (time.perf_counter() - start) * 1000
        report_data["execution_time_ms"] = round(elapsed, 2)
        if self.consecutive_failures > 0: self.reset_circuit()
        return report_data
