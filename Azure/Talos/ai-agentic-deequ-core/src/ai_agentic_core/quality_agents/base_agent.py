# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator
import logging

class AgentMetrics(BaseModel):
    """📊 CONTRATO INMUTABLE DE TELEMETRÍA AGÉNTICA (DAMA Quality Metrics)"""
    agent_name: str = Field(..., description="Nombre tecnico del subagente especialista")
    dimension: str = Field(..., description="Dimension DAMA bajo auditoria")
    is_valid: bool = Field(..., description="Veredicto de conformidad estructural")
    score: float = Field(..., description="Rango probabilistico de confianza entre 0.0 y 1.0")
    execution_time_ms: float = Field(..., description="Latencia cognitiva consumida")
    remediation_applied: bool = Field(..., description="Indica si se gatillo un bucle de autocuracion")
    root_cause_analysis: Dict[str, Any] = Field(default_factory=dict, description="Mapeo detallado de anomalías")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata contextual de inferencia")

    @field_validator("score")
    @classmethod
    def validate_score_boundaries(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError(f"Score out of bounds: {v}")
        return v

class BaseQualityAgent(ABC):
    """🛡️ STRATEGY / PLUGIN PATTERN (Nivel 6)"""
    def __init__(self, agent_config: Dict[str, Any]):
        self.config = agent_config
        self.agent_name = self.__class__.__name__
        logger_name = f"ai_agentic_core.quality_agents.{self.agent_name.lower()}"
        self.logger = logging.getLogger(logger_name)

    @abstractmethod
    async def execute_audit(self, tenant_id: str, kpi_target: str, data: Dict[str, Any]) -> AgentMetrics:
        pass
