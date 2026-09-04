# -*- coding: utf-8 -*-
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseCognitiveInterceptor(ABC):
    """
    🏛️ RESILIENT INTERCEPTOR STRATEGY CONTRACT
    Interfaz inmutable que implementa el patron Circuit Breaker de forma nativa por plugin.
    Aísla las fallas operacionales protegiendo el flujo principal del enjambre.
    """
    def __init__(self):
        self.is_circuit_open = False
        self.consecutive_failures = 0
        self.failure_threshold = 3
        self.logger = logging.getLogger(self.__class__.__name__)

    def handle_failure(self):
        self.consecutive_failures += 1
        if self.consecutive_failures >= self.failure_threshold and not self.is_circuit_open:
            self.is_circuit_open = True
            self.logger.critical(f"[CIRCUIT_OPEN_TRIGGERED] El disyuntor de {self.__class__.__name__} se ha abierto debido a {self.consecutive_failures} fallas consecutivas. Entrando en modo BYPASS.")

    def reset_circuit(self):
        self.is_circuit_open = False
        self.consecutive_failures = 0
        self.logger.info(f"[CIRCUIT_RESET] El disyuntor de {self.__class__.__name__} se ha restablecido a modo CLOSED.")

    @abstractmethod
    async def _execute_pre(self, tenant_id: str, json_payload: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def _execute_post(self, tenant_id: str, report_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    async def pre_process(self, tenant_id: str, json_payload: Dict[str, Any]) -> Dict[str, Any]:
        if self.is_circuit_open:
            return json_payload
        try:
            return await self._execute_pre(tenant_id, json_payload)
        except Exception as error:
            self.logger.error(f"[INTERCEPTOR_PRE_FAIL] Error atrapado en pre_process de {self.__class__.__name__}: {str(error)}")
            self.handle_failure()
            return json_payload

    async def post_process(self, tenant_id: str, report_data: Dict[str, Any]) -> Dict[str, Any]:
        if self.is_circuit_open:
            return report_data
        try:
            return await self._execute_post(tenant_id, report_data)
        except Exception as error:
            self.logger.error(f"[INTERCEPTOR_POST_FAIL] Error atrapado en post_process de {self.__class__.__name__}: {str(error)}")
            self.handle_failure()
            return report_data
