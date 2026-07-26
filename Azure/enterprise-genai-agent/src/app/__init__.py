# src/app/core/__init__.py
"""Subpaquete de utilidades core y configuraciones estáticas del sistema.

Este archivo se mantiene vacío de forma intencional para garantizar el aislamiento
y evitar importaciones circulares durante el arranque (bootstrap) de las variables de entorno.
"""

# Metadatos de Gobierno Corporativo y Control de Cambios
__author__ = "Edith BG"
__date__ = "2026-07-24"
__version__ = "1.0.0"
__status__ = "PoC"


import logging

# Configuración del formato de logs unificado para el monitoreo del negocio
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("EnterpriseGenAI")
logger.info("📦 Inicializando el ecosistema modular de IA de la empresa...")
