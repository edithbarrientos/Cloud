import hashlib
import json
import logging
from datetime import datetime
from typing import Dict, Any, Tuple

logger = logging.getLogger("ai_agentic_core.lineage")

class CognitiveLineageEngine:
    """
    ⛓️ LINEAGE ENGINE: CRYPTOGRAPHIC BLOCKCHAIN LEDGER
    Calcula el linaje procedimental inmutable O(1) acoplando hashes encadenados
    para auditar la trazabilidad de los datos según DAMA-DMBOK.
    """
    def __init__(self) -> None:
        pass

    def compute_immutable_lineage(self, raw_data: Dict[str, Any], previous_hash: str, step_sequence: int, framework: str) -> Tuple[str, bool]:
        """
        🧮 ALGORITMO DE TRAZABILIDAD
        Genera una firma SHA-256 encadenada al bloque anterior para asegurar el no-repudio.
        """
        # Estructurar la semilla del bloque de linaje
        lineage_block = {
            "data_fingerprint": hashlib.sha256(json.dumps(raw_data, sort_keys=True).encode('utf-8')).hexdigest(),
            "previous_hash": previous_hash,
            "step_sequence": step_sequence,
            "regulatory_framework": framework
        }
        
        # Calcular el hash actual del eslabón de linaje
        block_serialized = json.dumps(lineage_block, sort_keys=True).encode('utf-8')
        current_hash = hashlib.sha256(block_serialized).hexdigest()
        
        # Verificar ruptura del linaje (Si el hash anterior es nulo o por defecto y no es el paso 1)
        is_lineage_broken = False
        if step_sequence > 1 and (previous_hash == "0000000000000000000000000000" or not previous_hash):
            is_lineage_broken = True
            logger.critical(f"🚨 [LINEAGE_RUPTURE] ¡Se detectó un quiebre en el linaje de datos en la Secuencia {step_sequence}!")

        return current_hash, is_lineage_broken
