import asyncio
import logging
import random
import time
from typing import Callable, Any

logger = logging.getLogger("ai_agentic_core.cloud_patterns")

class CloudCircuitBreaker:
    """🛡️ PATRÓN DISYUNTOR (CIRCUIT BREAKER) - Evita asfixiar el Event Loop si Azure cae."""
    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 5.0) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = "CLOSED"
        self._failure_count = 0
        self._last_state_change = time.time()

    def record_success(self) -> None:
        self._failure_count = 0
        self.state = "CLOSED"

    def record_failure(self) -> None:
        self._failure_count += 1
        if self._failure_count >= self.failure_threshold:
            self.state = "OPEN"
            self._last_state_change = time.time()
            logger.critical(f"🚨 [CIRCUIT_BREAKER] 🛑 ¡Disyuntor ABIERTO! Tráfico NoSQL desviado temporalmente a RAM.")

    def allow_execution(self) -> bool:
        if self.state == "OPEN":
            if time.time() - self._last_state_change > self.recovery_timeout:
                self.state = "HALF_OPEN"
                logger.warning("⚡ [CIRCUIT_BREAKER] 🟡 Probando canal de red...")
                return True
            return False
        return True

class CloudExponentialRetry:
    """🔄 PATRÓN RETRY WITH BACKOFF & JITTER - Reintentos exponenciales elásticos."""
    def __init__(self, max_retries: int = 3, base_delay: float = 0.1) -> None:
        self.max_retries = max_retries
        self.base_delay = base_delay

    async def execute(self, async_func: Callable[[], Any], circuit_breaker: CloudCircuitBreaker, *args, **kwargs) -> Any:
        if not circuit_breaker.allow_execution():
            raise ConnectionRuntimeError("Disyuntor abierto: Tráfico suspendido.")

        attempt = 0
        while attempt < self.max_retries:
            try:
                result = await async_func(*args, **kwargs)
                circuit_breaker.record_success()
                return result
            except Exception as e:
                attempt += 1
                if attempt >= self.max_retries:
                    circuit_breaker.record_failure()
                    raise e
                delay = (self.base_delay * (2 ** attempt)) + random.uniform(0, 0.05)
                logger.warning(f"⚠️ [CLOUD_RETRY] Reintento {attempt}/{self.max_retries} en {delay:.4f}s.")
                await asyncio.sleep(delay)

class ConnectionRuntimeError(RuntimeError):
    pass
