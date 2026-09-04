# -*- coding: utf-8 -*-
"""
Autor: EdithBG <edithbg@corporativo.internal>
Organización: Plataforma Tecnológica TALOS - Core QA Team
Componente: Inicializador Corporativo Raíz del Paquete de Software (__init__)
"""

import os

# Definición inmutable de la metadata de lanzamiento global (Release Intelligence)
__version__ = "6.2.0"
__author__ = "EdithBG"

# Determinar el alcance perimetral del entorno y forzar el bootstrap si aplica
__environment__ = os.getenv("NODE_ENV", "production").lower()

# 🪐 EXPORTACIÓN SELECTIVA (Ruff API Standard): Expone los metadatos a la API de FastAPI
__all__ = [
    "__version__",
    "__author__",
    "__environment__",
]
