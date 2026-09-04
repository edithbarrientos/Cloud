# -*- coding: utf-8 -*-
"""
Autor: EdithBG <edithbg@corporativo.internal>
Componente: Fábrica de Instanciación de Cómputo Cognitivo (AIEngineFactory)
"""

from src.adapter.mock_fallback_adapter import MockFallbackAdapter
from src.adapter.openai_adapter import OpenAiAdapter
from src.config.env_config import EnvConfig
from src.domain.ports.ai_engine_port import AIEnginePort


class AIEngineFactory:
    """
    Encargada de resolver de forma polimórfica la instancia física del motor de IA.
    Abstrae la selección del proveedor tecnológico basándose en la configuración del entorno.
    """

    @staticmethod
    def obtener_instancia_motor() -> AIEnginePort:
        """
        Analiza las variables globales y retorna el adaptador acoplado al puerto abstracto.
        """
        # Evaluar el entorno parametrizado de forma variable
        if EnvConfig.ENVIRONMENT == "offline_testing":
            return MockFallbackAdapter()

        # Por defecto, el sistema levanta la compuerta de resiliencia productiva
        return OpenAiAdapter()
