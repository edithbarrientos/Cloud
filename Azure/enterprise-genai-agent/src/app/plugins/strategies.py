# src/app/plugins/strategies.py
"""Módulo de estrategias de negocio y conectores de infraestructura ERP.

Define las herramientas acoplables (Plugins) bajo el estándar de Semantic Kernel v1+,
dotándolas de telemetría explícitamente, sanitización contra inyecciones de prompt y políticas
de reintento con backoff exponencial.
"""

# Metadatos de Gobierno Corporativo y Control de Cambios
__author__ = "Edith BG"
__date__ = "2026-07-24"
__version__ = "1.0.0"
__status__ = "PoC / Enterprise Ready"

import asyncio
import logging
import random
import re
from abc import ABC, abstractmethod
from typing import Any

from opentelemetry import trace
from pydantic import BaseModel, Field, ValidationError
from semantic_kernel.functions import kernel_function
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class ERPConnectionError(Exception):
    """Excepción de infraestructura lanzada por intermitencias de red con el ERP corporativo."""


class InventoryQueryModel(BaseModel):
    """Modelo de datos encargado de la validación sintáctica de los parámetros calculados por la IA."""

    sku_producto: str = Field(
        ..., 
        description="Código único del producto. Formato estricto: 'PROD-' seguido de 3 o 4 dígitos."
    )


class BusinessToolStrategy(ABC):
    """Interfaz abstracta que gobierna el contrato de diseño de herramientas de agentes."""

    @abstractmethod
    async def ejecutar(self, sku_producto: str) -> dict[str, Any]:
        """Ejecuta de forma asíncrona la acción de la herramienta de negocio."""


class ERPInventoryStrategy(BusinessToolStrategy):
    """Estrategia de negocio que conecta de forma segura a los agentes con el stock físico.

    Encapsula endpoints del ERP e instrumenta validación defensiva en profundidad para
    evitar el procesamiento de datos erróneos provenientes de alucinaciones del modelo.
    """
    
    def __init__(self, erp_url: str) -> None:
        """Inicializa la estrategia inyectando la dependencia de red necesaria.

        Args:
            erp_url (str): Dirección URL base validada del sistema SAP/ERP corporativo.
        """
        self._erp_url = erp_url

    @kernel_function(
        name="consultar_inventario",
        description="Consulta las existencias actuales de un artículo en el ERP usando su código SKU."
    )
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(ERPConnectionError),
        before_sleep=lambda retry_state: logger.warning(
            f"⚠️ Conexión SAP/ERP lenta. Reintentando de forma automática... Intento: {retry_state.attempt_number}"
        ),
        reraise=True
    )
    async def ejecutar(self, sku_producto: str) -> dict[str, Any]:
        """Busca el inventario actual de un producto en el ERP de forma asíncrona."""
        with tracer.start_as_current_span("plugin.erp.consultar_inventario") as span:
            span.set_attribute("component", "agent_plugin")
            
            try:
                # 1. Validación estructural con Pydantic
                logger.info(f"🔍 [Plugin ERP] Analizando y validando sintaxis del SKU recibido: '{sku_producto}'...")
                validated = InventoryQueryModel(sku_producto=sku_producto)
                clean_sku = validated.sku_producto

                # 2. Defensa en profundidad (Regex contra inyección de prompts)
                logger.info(f"🛡️ [Plugin ERP] Pasando SKU '{clean_sku}' por el cortafuegos de expresiones regulares...")
                if not re.match(r"^PROD-\d{3,4}$", clean_sku):
                    logger.error(f"🚨 Alerta de Seguridad: Intento de elusión con SKU no válido: {sku_producto}")
                    span.set_attribute("security.alert", "Estructura de SKU inválida detectada")
                    span.set_status(trace.Status(trace.StatusCode.ERROR, "Security Block"))
                    return {"error": "Acceso denegado: Formato de SKU inválido.", "status": "security_block"}

                # --- SIMULACIÓN DE TRABAJO ASÍNCRONO EN VIVO ---
                logger.info(f"⏳ [Plugin ERP] Conectando de forma asíncrona con el servidor central SAP en {self._erp_url}...")
                await asyncio.sleep(2.0)  # Pausa de 2 segundos visible en terminal
                
                logger.info("📦 [Plugin ERP] Conexión establecida. Extrayendo balances de stock del maestro de materiales...")
                await asyncio.sleep(1.5)  # Pausa de 1.5 segundos simulando descarga de datos
                # -----------------------------------------------

                # Simulación de fallas intermitentes del ERP (20% de probabilidad)
                if random.random() < 0.2:
                    raise ERPConnectionError("Timeout de red al conectar con el maestro de materiales de SAP.")

                logger.info(f"✅ [Plugin ERP] ¡Éxito! Stock localizado para {clean_sku}. Guardando trazas en OpenTelemetry.")
                span.set_attribute("business.sku", clean_sku)
                span.set_attribute("business.erp_endpoint", self._erp_url)
                
                return {
                    "sku": clean_sku, 
                    "stock": 85, 
                    "origin": self._erp_url, 
                    "status": "success"
                }

            except ValidationError as ve:
                span.record_exception(ve)
                span.set_status(trace.Status(trace.StatusCode.ERROR, "Validation Error"))
                return {"error": f"La IA generó parámetros erróneos: {ve.errors()}", "status": "failed"}
            except ERPConnectionError as e:
                span.record_exception(e)
                raise
            except Exception as ex:  # noqa: BLE001
                span.record_exception(ex)
                span.set_status(trace.Status(trace.StatusCode.ERROR, "Uncaught Exception"))
                return {"error": "Fallo interno no controlado en el conector corporativo.", "status": "failed"}
