import os
import logging
import redis.asyncio as aioredis
import orjson

logger = logging.getLogger("nexus-repository")

class NexusRepository:
    def __init__(self):
        # ⚡ ENLACE DINÁMICO SRE: Lee el DNS distributed de Kubernetes, bypass a 127.0.0.1
        self.redis_url = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
        self.pool = None

    def start(self):
        if not self.pool:
            logger.info(f"🟢 Inicializando Pool de Conexiones de alta densidad hacia: {self.redis_url}")
            self.pool = aioredis.ConnectionPool.from_url(
                self.redis_url, 
                decode_responses=False, # Procesamiento de bytes puros a velocidad C
                max_connections=100
            )

    async def obtener_ventana_historial(self, customer_id: str, limite: int = 5) -> list[dict]:
        try:
            client = aioredis.Redis(connection_pool=self.pool)
            clave = f"chat:historial:{customer_id}"
            raw_data = await client.lrange(clave, -limite, -1)
            return [orjson.loads(msg) for msg in raw_data if msg]
        except Exception as e:
            logger.error(f"💥 Fallo al leer historial en Redis: {str(e)}")
            return []

    async def agregar_mensaje(self, customer_id: str, role: str, content: str):
        try:
            client = aioredis.Redis(connection_pool=self.pool)
            clave = f"chat:historial:{customer_id}"
            payload = orjson.dumps({"role": role, "content": content})
            async with client.pipeline(transaction=False) as pipe:
                pipe.rpush(clave, payload)
                pipe.ltrim(clave, -20, -1) # Mantener ventana deslizante
                await pipe.execute()
        except Exception as e:
            logger.error(f"💥 Fallo al escribir mensaje en Redis: {str(e)}")

    async def registrar_telemetria_sre(self, customer_id: str, metrics: dict):
        try:
            client = aioredis.Redis(connection_pool=self.pool)
            clave = f"telemetria:sre:{customer_id}"
            await client.xadd(clave, {"data": orjson.dumps(metrics)}, maxlen=100)
        except Exception: pass

    async def registrar_error(self, customer_id: str, mensaje: str):
        try:
            client = aioredis.Redis(connection_pool=self.pool)
            clave = f"incidentes:errores:{customer_id}"
            await client.lpush(clave, orjson.dumps({"ts": os.time() if hasattr(os, "time") else 0, "err": mensaje}))
            logger.warning(f"🚨 [INCIDENTE REPORTADO] Error registrado en caché para {customer_id}: {mensaje}")
        except Exception: pass

repository = NexusRepository()
