import re
import logging
from typing import Dict, Any, Tuple

# Forzar la configuración de alertas limpias en la pantalla del servidor
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] grpc.server: %(message)s")
logger = logging.getLogger("ai_agentic_core.privacy")

class CognitivePrivacyEngine:
    """
    🛡️ PRIVACY ENGINE V2: REGULATORY COMPLIANCE GATEKEEPER
    Algoritmo heurístico adaptativo multijurisdiccional basado en DAMA International.
    """
    def __init__(self) -> None:
        self.email_regex = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
        self.jwt_token_regex = re.compile(r"eyJhbGciOi[a-zA-Z0-9-_=]+\.[a-zA-Z0-9-_=]+\.?[a-zA-Z0-9-_=]*")
        self.generic_cc_regex = re.compile(r"\b(?:\d[ -]*?){13,16}\b")
        
        # 🪄 DICCIONARIO DE JURISDICCIONES LEGALES DE DAMA
        self.REGULATORY_POLICIES = {
            "gdpr": {"strict_pii": True, "allow_cc": False, "max_severity": "CRITICAL_GDPR_VIOLATION"},
            "lgpd": {"strict_pii": True, "allow_cc": True, "max_severity": "HIGH_LGPD_ALERT"},
            "lfpdppp": {"strict_pii": True, "allow_cc": True, "max_severity": "HIGH_MEX_COMPLIANCE_ALERT"},
            "internal_governance": {"strict_pii": False, "allow_cc": True, "max_severity": "LOW_INTERNAL_AUDIT"}
        }

    def _validate_luhn_algorithm(self, card_number: str) -> bool:
        digits = [int(d) for d in re.sub(r"\D", "", card_number)]
        if not digits or len(digits) < 13: return False
        checksum = digits[-1]
        payload = digits[:-1]
        payload.reverse()
        total = 0
        for i, digit in enumerate(payload):
            if i % 2 == 0:
                digit *= 2
                if digit > 9: digit -= 9
            total += digit
        return (total + checksum) % 10 == 0

    def audit_regulatory_data_leak(self, payload: Dict[str, Any], metadata: Dict[str, Any]) -> Tuple[bool, str, str]:
        """
        🔍 EVALUACIÓN LEGAL DAMA-DMBOK
        Analiza la confidencialidad e integridad del dato basándose en el marco legal de entrada.
        """
        # Extraer dinámicamente el marco legal enviado por el cliente (Fallback a gobernanza interna)
        legal_framework = str(metadata.get("regulatory_framework", "internal_governance")).lower().strip()
        policy = self.REGULATORY_POLICIES.get(legal_framework, self.REGULATORY_POLICIES["internal_governance"])
        
        payload_str = str(payload)
        is_pii_exposed = False
        violation_reason = "CLEAN_COMPLIANCE_PASS"
        severity_level = "NOMINAL"

        # 1. Auditoría de Confidencialidad: Escaneo de Tokens y Credenciales
        if self.jwt_token_regex.search(payload_str):
            is_pii_exposed = True
            violation_reason = "EXPOSED_JWT_SECRET_TOKEN"
            severity_level = "CRITICAL"

        # 2. Auditoría y Clasificación Adaptativa de Correos Electrónicos (PII)
        if self.email_regex.search(payload_str) and policy["strict_pii"]:
            is_pii_exposed = True
            violation_reason = f"EXPOSED_EMAIL_PII_UNDER_{legal_framework.upper()}"
            severity_level = "CRITICAL" if legal_framework == "gdpr" else "HIGH"

        # 3. Auditoría de Integridad: Validación Criptográfica de Tarjetas de Crédito
        potential_cards = self.generic_cc_regex.findall(payload_str)
        for card in potential_cards:
            if self._validate_luhn_algorithm(card):
                if not policy["allow_cc"] or legal_framework == "gdpr":
                    is_pii_exposed = True
                    violation_reason = f"ILLEGAL_CREDIT_CARD_STORAGE_VIOLATION ({legal_framework.upper()})"
                    severity_level = "CRITICAL"

        if is_pii_exposed:
            logger.critical(f"🚨 [DAMA_COMPLIANCE_VIOLATION] Marco: {legal_framework.upper()} | Motivo: {violation_reason} | Severidad: {severity_level}")

        return is_pii_exposed, violation_reason, severity_level
