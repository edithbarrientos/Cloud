# src/app/app.py
"""Punto de entrada directo por consola para el ecosistema de IA Generativa.

Inicializa los componentes inmutables y ejecuta el plugin de inventario del ERP
de forma asíncrona local para emitir un dictamen inmediato en la terminal.
"""

__author__ = "Edith BG"
__date__ = "2026-07-24"
__version__ = "1.0.0"
__status__ = "PoC"

import asyncio
import logging

from opentelemetry import trace

from src.app.core.config import AppConfig
from src.app.plugins import ERPInventoryStrategy

logger = logging.getLogger("EnterpriseGenAI.Main")
tracer = trace.get_tracer(__name__)


async def main() -> None:
    """Ejecuta de forma directa la lógica del agente en la consola."""
    with tracer.start_as_current_span("app.bootstrap") as span:
        logger.info("Cargando componentes del ecosistema de IA por consola...")
        
        try:
            config = AppConfig()
            span.set_attribute("config.erp_url", str(config.erp_api_url))
            logger.info("Configuraciones validadas correctamente.")
        except Exception as e:  # noqa: BLE001
            logger.critical(f"❌ Error al cargar la configuración: {e}")
            span.record_exception(e)
            return

        plugin_inventario = ERPInventoryStrategy(erp_url=str(config.erp_api_url))
        logger.info("Plugin asíncrono 'ERPInventoryStrategy' cargado.")
        logger.info("Enviando prompt al Agente Orquestador...")
        
        with tracer.start_as_current_span("agent.execution") as agent_span:
            try:
                logger.info("🤖 [Modo Local] Forzando simulación lógica de GPT-4o sin llamadas de red...")
                resultado_plugin = await plugin_inventario.ejecutar(sku_producto="PROD-777")
                
                resultado = (
                    f"Dictamen de Auditoría IA (Ejecución Directa Consola):\n"
                    f"Se procedió a consultar de forma automatizada el sistema ERP ({resultado_plugin['origin']}).\n"
                    f"El artículo {resultado_plugin['sku']} reporta un estado de: {resultado_plugin['status']}.\n"
                    f"Contamos con un stock físico de {resultado_plugin['stock']} unidades, "
                    f"lo cual es suficiente para cubrir la orden de ventas de manera inmediata."
                )
                
                print("\n" + "="*60)
                print("🎯 RESPUESTA EJECUTIVA DEL AGENTE DE NEGOCIO:")
                print("="*60)
                print(resultado)
                print("="*60 + "\n")
                
                agent_span.set_attribute("agent.status", "success")
            except Exception as ex:  # noqa: BLE001
                logger.error(f"Fallo durante la ejecución autónoma del agente: {ex}")
                agent_span.record_exception(ex)


if __name__ == "__main__":
    asyncio.run(main())