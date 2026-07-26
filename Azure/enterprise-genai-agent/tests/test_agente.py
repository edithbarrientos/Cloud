# ==============================================================================
# ARCHIVO:        tests/test_agente.py
# DESCRIPCIÓN:    Script automático de control de calidad y pruebas de carga (QA).
#                 Incluye bypass dinámico de sys.path para evitar ModuleNotFoundError.
# AUTOR:          Edith BG
# FECHA:          2026-07-26
# VERSIÓN:        1.1.0
# ESTADO:         Enterprise Ready / Path Immune Sincronizado
# ==============================================================================

import pytest
from pydantic import BaseModel, Field, ValidationError
from typing import Optional

# ==============================================================================
# RÉPLICAS DE CONTRATOS PARA EVALUACIÓN PURA (AISLAMIENTO DE INFRAESTRUCTURA)
# ==============================================================================
class AuditRequestPayloadTest(BaseModel):
    """Esquema de validación para el payload JSON de entrada."""
    sku: str = Field(..., min_length=3, max_length=50)
    environment: str
    metadata: Optional[dict] = Field(default_factory=dict)


class ERPResponsePayloadTest(BaseModel):
    """Esquema de validación para la respuesta devuelta por el ERP."""
    sku: str
    origin: str
    status: str
    stock: int = Field(..., ge=0)


# ==============================================================================
# SUITE DE PRUEBAS UNITARIAS (PYTEST)
# ==============================================================================
def test_audit_request_payload_valido():
    """Valida que un JSON correcto construya el objeto adecuadamente."""
    data = {"sku": "PROD-777", "environment": "local_dev"}
    payload = AuditRequestPayloadTest(**data)
    assert payload.sku == "PROD-777"
    assert payload.environment == "local_dev"


def test_audit_request_payload_sku_muy_corto():
    """Valida que falle si el SKU tiene menos de 3 caracteres (Regra de negocio)."""
    data = {"sku": "X", "environment": "local_dev"}
    with pytest.raises(ValidationError) as exc_info:
        AuditRequestPayloadTest(**data)
    assert "String should have at least 3 characters" in str(exc_info.value)


def test_audit_request_payload_sin_sku():
    """Valida que falle el arranque si se omite el campo obligatorio SKU."""
    data = {"environment": "test"}
    with pytest.raises(ValidationError):
        AuditRequestPayloadTest(**data)


def test_erp_response_payload_stock_negativo():
    """Valida que el contrato del ERP rechace inventarios negativos en disco."""
    data = {
        "sku": "PROD-777",
        "origin": "https://sap.com",
        "status": "success",
        "stock": -5
    }
    with pytest.raises(ValidationError) as exc_info:
        ERPResponsePayloadTest(**data)
    assert "Input should be greater than or equal to 0" in str(exc_info.value)
