# -*- coding: utf-8 -*-
"""
Autor: EdithBG <edithbg@corporativo.internal>
Componente: Centralizador de Configuración y Tipado de Entorno (env_config)
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Localizar de forma dinámica la raíz del repositorio para cargar el .env|
base_dir = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(dotenv_path=base_dir / ".env")


class EnvConfig:
    """
    Centraliza, tipa y valida la configuración operativa extraída del entorno.
    Evita el uso directo de os.getenv por el código fuente para prevenir errores de tipado.
    """

    # Entorno operativo
    ENVIRONMENT: str = os.getenv("NODE_ENV", "development")
    PORT: int = int(os.getenv("PORT", "8000"))

    # Parámetros de Ciberseguridad e IA (Abstracción Temporal)
    TIMEOUT_IA_SEGUNDOS: float = float(os.getenv("TALOS_TIMEOUT_IA_MILISEGUNDOS", "4000")) / 1000.0
    UMBRAL_FRUSTRACION_MAX: int = int(os.getenv("TALOS_UMBRAL_FRUSTRACION", "85"))

    # Modelos del Prompt Router Asignados
    MODELO_ECONOMICO: str = os.getenv("OPENAI_MODELO_ECONOMICO", "gpt-4o-mini")
    MODELO_AVANZADO: str = os.getenv("OPENAI_MODELO_AVANZADO", "gpt-4")

    # Endpoints Físicos de la Capa de Datos (Malla Vectorial)
    AI_SEARCH_ENDPOINT: str = os.getenv("AZURE_AI_SEARCH_ENDPOINT", "https://localhost")

    @classmethod
    def validar_entorno_critico(cls) -> None:
        """
        Valida en el arranque del contenedor que las variables vitales de Azure no vengan vacías.
        Si falta alguna, detiene el microservicio de inmediato para evitar fallos en producción.
        """
        if cls.ENVIRONMENT != "offline_testing":
            variables_criticas = [
                ("AZURE_AI_SEARCH_ENDPOINT", os.getenv("AZURE_AI_SEARCH_ENDPOINT"))
            ]
            for nombre, valor in variables_criticas:
                if not valor:
                    raise ValueError(
                        f"🚨 ERROR CRÍTICO DE INFRAESTRUCTURA: Falta configurar la variable {nombre}."
                    )


# Ejecutar la validación al importar el módulo de forma automatizada
EnvConfig.validar_entorno_critico()
