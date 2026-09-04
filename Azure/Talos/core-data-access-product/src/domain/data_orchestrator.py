"""
Autor: EdithBG <edithbg@corporativo.internal>
Organización: Gobierno de Datos - Plataforma Transversal Core
Componente: Orquestador Central SRE con Cache-Aside Redis Certificado (DataOrchestrator)
"""
import json
import redis.asyncio as redis
from src.infrastructure.factories.strategy_factory import StrategyFactory
from src.config.env_config import env_config
from typing import Dict, Any, Optional

class DataOrchestrator:
    def __init__(self, target_engine: str):
        # Inversión de Dependencias: El orquestador interactúa de forma abstracta
        self.strategy = StrategyFactory.obtener_estrategia_activa(target_engine)
        
        # 🪐 SOLUCIÓN DE TIPADO: Se declara explícitamente el tipo del cliente para mitigar reportOptionalMemberAccess
        self.redis_client: Any = None
        self.is_redis_active: bool = False

    async def inicializar_infraestructura(self) -> None:
        """Abre las autopistas de red de la estrategia y de la caché Redis simultáneamente"""
        await self.strategy.conectar()
        try:
            self.redis_client = redis.from_url(
                env_config.DATABASE_URL.replace("postgresql", "redis") if "postgresql" in env_config.DATABASE_URL else "redis://localhost:6379"
            )
            await self.redis_client.ping()
            self.is_redis_active = True
            print("🏆 [CORE-DATA-ORCHESTRATOR]: Conexión en verde con clúster Redis Cache Aside.")
        except Exception as err:
            self.is_redis_active = False
            print(f"⚠️ [CORE-DATA-ORCHESTRATOR-WARN]: Caché RAM no disponible: {err}")

    # ==============================================================================
    # 🪐 OPERACIONES CRUD DEL DOMINIO CON BLINDAJE DE TIPADO
    # ==============================================================================

    async def ejecutar_create(self, llave_id: str, datos: Dict[str, Any]) -> bool:
        """[C - CREATE]: Inserta el registro e invalida la caché vieja de forma segura"""
        exito = await self.strategy.crear_registro(llave_id, datos)
        
        # 🪐 VERIFICACIÓN ESTRICTA: Se evalúa de forma rígida la presencia física del socket
        if exito and self.is_redis_active and self.redis_client is not None:
            try:
                await self.redis_client.delete(f"core:data:customer:{llave_id}")
            except Exception:
                pass
        return exito

    async def procesar_petición_inteligente(self, cliente_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        """[R - READ]: Orquesta de forma SRE el ciclo de vida de la consulta con Cache-Aside"""
        redis_key = f"core:data:customer:{cliente_id}"

        if self.is_redis_active and self.redis_client is not None:
            try:
                cached_data = await self.redis_client.get(redis_key)
                if cached_data:
                    print(f"🗄️ [DATA-PRODUCT-HIT]: Registro recuperado de Redis para: [{tenant_id}]")
                    return json.loads(cached_data)
            except Exception:
                pass

        print(f"📡 [DATA-PRODUCT-MISS]: Extrayendo información directo del motor físico...")
        perfil_unificado = await self.strategy.consultar_registro(cliente_id)

        if perfil_unificado and self.is_redis_active and self.redis_client is not None:
            try:
                await self.redis_client.set(redis_key, json.dumps(perfil_unificado), ex=1800)
                print(f"🏆 [DATA-PRODUCT-CACHE-SET]: RAM actualizada para: {cliente_id}")
            except Exception:
                pass

        return perfil_unificado

    async def ejecutar_update(self, llave_id: str, datos_nuevos: Dict[str, Any]) -> bool:
        """[U - UPDATE]: Actualiza el motor físico e invalida la caché RAM de forma inmediata"""
        exito = await self.strategy.actualizar_registro(llave_id, datos_nuevos)
        
        if exito and self.is_redis_active and self.redis_client is not None:
            try:
                await self.redis_client.delete(f"core:data:customer:{llave_id}")
                print(f"🗄️ [CACHE-EVICT]: Memoria RAM purgada para: {llave_id}")
            except Exception:
                pass
        return exito

    async def ejecutar_delete(self, llave_id: str) -> bool:
        """[D - DELETE]: Remueve el registro del disco físico y purga la RAM de Redis"""
        exito = await self.strategy.borrar_registro(llave_id)
        
        if exito and self.is_redis_active and self.redis_client is not None:
            try:
                await self.redis_client.delete(f"core:data:customer:{llave_id}")
                print(f"🗄️ [CACHE-PURGE]: Registro eliminado completamente de la memoria RAM.")
            except Exception:
                pass
        return exito

    async def liberar_infraestructura(self) -> None:
        """Cierra de forma hermética todos los pools, hilos y sockets de red abiertos"""
        await self.strategy.desconectar()
        if self.redis_client is not None:
            await self.redis_client.close()
            print("📡 [CORE-DATA-ORCHESTRATOR]: Autopistas de red e infraestructura analítica liberadas.")
