import time
import logging
from typing import Dict

logger = logging.getLogger("talos_chatbot_backend")

class TokenBucketLimiter:
    """
    🧮 ALGORITMO TOKEN BUCKET (O(1) Space/Time Complexity):
    Controla el flujo perimetral por cliente en caliente sin usar bases de datos pesadas.
    Evita la contención de hilos y protege la RAM de la Mac contra estrés masivo.
    """
    def __init__(self, capacity: int = 10, refill_rate: float = 2.0) -> None:
        self.capacity = capacity
        self.refill_rate = refill_rate  # Tokens agregados por segundo
        self.buckets: Dict[str, Dict[str, float]] = {}

    def is_request_allowed(self, client_id: str) -> bool:
        """Calcula de forma matematica el derecho de paso en tiempo constante."""
        current_time = time.time()
        
        if client_id not in self.buckets:
            self.buckets[client_id] = {"tokens": float(self.capacity), "last_update": current_time}
            return True

        bucket = self.buckets[client_id]
        elapsed = current_time - bucket["last_update"]
        
        # 🪄 REFILL EQUATION: Recuperación matemática elástica basada en delta de tiempo
        refilled_tokens = bucket["tokens"] + (elapsed * self.refill_rate)
        bucket["tokens"] = min(float(self.capacity), refilled_tokens)
        bucket["last_update"] = current_time

        if bucket["tokens"] >= 1.0:
            bucket["tokens"] -= 1.0
            return True

        logger.warning(f"🚨 [RATE_LIMITER_BLOCKED] Trafico abusivo detectado para el cliente: {client_id}")
        return False
