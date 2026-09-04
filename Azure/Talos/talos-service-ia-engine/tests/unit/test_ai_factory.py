# -*- coding: utf-8 -*-
"""
Suite de Pruebas Unitarias - Validación del Patrón Factory
"""

from src.config.env_config import EnvConfig
from src.factory.ai_factory import AIEngineFactory
from src.adapter.mock_fallback_adapter import MockFallbackAdapter
from src.adapter.openai_adapter import OpenAiAdapter


def test_fabrica_debe_retornar_mock_en_entorno_offline():
    """Certifica la conmutación al adaptador de contingencia local."""
    EnvConfig.ENVIRONMENT = "offline_testing"
    instancia = AIEngineFactory.obtener_instancia_motor()
    assert isinstance(instancia, MockFallbackAdapter)


def test_fabrica_debe_retornar_openai_en_entorno_produccion():
    """
    [NUEVO] Certifica que si el entorno es production, la fábrica entrega 
    el conector elástico de OpenAI, cubriendo la línea faltante del archivo.
    """
    EnvConfig.ENVIRONMENT = "production"
    instancia = AIEngineFactory.obtener_instancia_motor()
    assert isinstance(instancia, OpenAiAdapter)