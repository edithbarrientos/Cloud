# -*- coding: utf-8 -*-
"""
Autor: EdithBG <edithbg@corporativo.internal>
Organización: Plataforma Tecnológica TALOS - Core QA Team
Nivel: Nivel de Configuración e Infraestructura (Bus de Datos)
Componente: Inicializador e Indexador de Entidades de Configuración (__init__)
"""

from src.config.celery_app import celery_orchestrator

# 🪐 EXPORTACIÓN SELECTIVA (Ruff API Standard): Expone el bus de Celery de forma encapsulada
__all__ = [
    "celery_orchestrator",
]
