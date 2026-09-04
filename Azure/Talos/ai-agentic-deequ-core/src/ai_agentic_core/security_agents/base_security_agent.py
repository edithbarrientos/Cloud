# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator
import logging

class SecurityReport(BaseModel):
    """🛡️ CONTRATO INMUTABLE DE EVALUACIÓN DE RIESGOS (Security & Privacy Report)"""
    agent_name: str = Field(..., description="Nombre tecnico del subagente especialista de seguridad")
    pilar: str = Field(..., description="Pilar de seguridad bajo escaneo")
    is_safe: bool = Field(..., description="Determina si el payload cumple con las politicas")
    veto_triggered: bool = Field(..., description="Bandera de aislamiento: Forza el desvio inmediato a cuarentena")
    risk_level: str = Field(default="LOW", description="Nivel de severidad tecnica: CRITICAL, HIGH, MEDIUM, LOW")
    risk_score: float = Field(..., description="Indice probabilistico de riesgo contextual entre 0.0 y 1.0")
    anomalies_detected: int = Field(default=0, description="Conteo de entidades maliciosas")
    root_cause_analysis: Dict[str, Any] = Field(default_factory=dict, description="Analisis de causa raiz")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata tecnica de telemetria")

    @field_validator("risk_score")
    @classmethod
    def validate_risk_boundaries(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError(f"Risk score out of bounds: {v}")
        return v

    @field_validator("risk_level")
    @classmethod
    def validate_severity_levels(cls, v: str) -> str:
        allowed_levels = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
        if v.upper() not in allowed_levels:
            raise ValueError(f"Invalid risk_level: {v}")
        return v.upper()

class BaseSecurityAgent(ABC):
    """
    🛡️ STRATEGY / PLUGIN PATTERN (Nivel 6)
    Contrato abstracto inmutable para el enjambre de los 4 pilares de seguridad y privacidad.
    """
    def __init__(self, security_config: Dict[str, Any]):
        self.config = security_config
        self.agent_name = self.__class__.__name__
        logger_name = f"ai_agentic_core.security_agents.{self.agent_name.lower()}"
        self.logger = logging.getLogger(logger_name)

    @abstractmethod
    async def verify_pilar(self, tenant_id: str, payload: Dict[str, Any]) -> SecurityReport:
        """Punto de entrada analitico inmutable del subagente de seguridad."""
        pass
