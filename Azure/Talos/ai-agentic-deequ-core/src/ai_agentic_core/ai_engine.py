import logging
import math
from typing import List, Tuple

logger = logging.getLogger("ai_agentic_core.analytics")

class StochasticAnomaliesEngine:
    """
    🧠 ENGINE IA: REAL-TIME STOCHASTIC DRIFT DETECTOR
    Algoritmo predictivo adaptativo basado en Ventanas Deslizantes y Z-Score
    para la detección de mutaciones y anomalías sintácticas en microsegundos.
    """
    def __init__(self, window_size: int = 50, threshold: float = 3.0) -> None:
        self.window_size = window_size
        self.threshold = threshold
        # Estado intrínseco de memoria (Ventana Histórica de Inferencia)
        self._sliding_window: List[float] = [0.85, 0.89, 0.91, 0.88, 0.93, 0.90, 0.87, 0.92]

    def evaluate_metric_drift(self, current_value: float) -> Tuple[bool, float, str]:
        """
        🧮 ALGORITMO ADAPTATIVO
        Calcula la media y la desviación estándar móvil para proyectar el Z-Score del dato.
        """
        if len(self._sliding_window) >= self.window_size:
            self._sliding_window.pop(0)

        n = len(self._sliding_window)
        if n < 2:
            self._sliding_window.append(current_value)
            return False, 0.0, "INITIALIZING_MODEL"

        # 1. Calcular Media Móvil Real
        mean = sum(self._sliding_window) / n
        
        # 2. Calcular Desviación Estándar Real
        variance = sum((x - mean) ** 2 for x in self._sliding_window) / n
        std_dev = math.sqrt(variance)

        if std_dev == 0:
            std_dev = 0.0001

        # 3. Proyectar Z-Score Dinámico
        z_score = abs(current_value - mean) / std_dev
        is_anomaly = z_score > self.threshold

        self._sliding_window.append(current_value)

        if is_anomaly:
            verdict = "CRITICAL_ANOMALY_DETECTED"
            logger.warning(f"🚨 [AI_ENGINE] Anomalía estocástica detectada! Z-Score: {z_score:.4f} > Límite: {self.threshold}")
        else:
            verdict = "NOMINAL_DATA_DISTRIBUTION"

        return is_anomaly, z_score, verdict
