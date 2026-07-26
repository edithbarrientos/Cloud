# src/app/plugins/__init__.py
"""Módulo de inicialización de la capa de plugins del Agente GenAI.

Centraliza, expone y gobierna las herramientas acoplables (Plugins) y estrategias 
de negocio para la orquestación asíncrona del ciclo de vida del Kernel.
"""

# Metadatos de Gobierno Corporativo y Control de Cambios
__author__ = "Edith BG"
__date__ = "2026-07-24"
__version__ = "1.0.0"
__status__ = "PoC / Enterprise Ready"

# Importación explícita apuntando al archivo real de tu árbol: strategies.py
from src.app.plugins.strategies import ERPInventoryStrategy

# Definición del contrato público del paquete para una exposición limpia hacia api.py
__all__ = ["ERPInventoryStrategy"]
