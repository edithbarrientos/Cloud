import os
import hmac
import hashlib
import json
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger("ai_agentic_core.security")

class AiSecurityGuardMaster:
    """
    🛡️ NIVEL 6: AI-SECURITY-GUARD-MASTER
    Filtro de Veto PII e Integridad Criptográfica Chained Hash SHA-256.
    """
    def __init__(self) -> None:
        self._hmac_key: bytes = os.getenv("SECRET_CRYPTO_SIGN_KEY", "default_secure_salt_123!").encode('utf-8')
        self._pii_keywords: list = ["email", "password", "token", "ssn", "credit_card"]

    def audit_and_sign_context(self, raw_payload: Dict[str, Any], previous_hash: str) -> Tuple[Dict[str, Any], bool]:
        pii_detected = False
        payload_str = json.dumps(raw_payload).lower()
        
        for keyword in self._pii_keywords:
            if keyword in payload_str:
                logger.warning(f"[SECURITY_GUARD] 🚨 Veto de Privacidad: PII detectada ('{keyword}').")
                pii_detected = True
                break

        security_level = "CRITICAL" if pii_detected else "STANDARD"

        try:
            payload_bytes = json.dumps(raw_payload, sort_keys=True).encode('utf-8')
            hasher = hmac.new(self._hmac_key, previous_hash.encode('utf-8'), hashlib.sha256)
            hasher.update(payload_bytes)
            current_hash = hasher.hexdigest()
        except Exception:
            current_hash = "SHA256_STUB_VALUE"

        security_context = {
            "level": security_level,
            "pii_detected": pii_detected,
            "last_hash": previous_hash,
            "current_hash": current_hash,
            "compliance_checked_at": True
        }

        return security_context, pii_detected
