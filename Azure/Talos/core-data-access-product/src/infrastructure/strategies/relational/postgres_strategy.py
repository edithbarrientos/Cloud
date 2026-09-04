"""
Autor: EdithBG <edithbg@corporativo.internal>
Organización: Gobierno de Datos - Plataforma Transversal Core
Componente: Estrategia de Conexión Relacional PostgreSQL (PostgresStrategy)
"""
import asyncpg
from src.infrastructure.strategies.base_strategy import BaseDataStrategy
from src.config.env_config import env_config
from typing import Dict, Any, Optional

class PostgresStrategy(BaseDataStrategy):
    def __init__(self):
        self.pool = None
        self.connection_string = env_config.DATABASE_URL

    async def conectar(self) -> None:
        self.pool = await asyncpg.create_pool(
            dsn=self.connection_string,
            min_size=env_config.DB_POOL_MIN_CONNECTIONS,
            max_size=env_config.DB_POOL_MAX_CONNECTIONS
        )

    async def crear_registro(self, llave_id: str, datos: Dict[str, Any]) -> bool:
        if not self.pool: return False
        async with self.pool.acquire() as conexion:
            query = "INSERT INTO core_bancario (client_id, txt_name, num_balance) VALUES ($1, $2, $3);"
            await conexion.execute(query, llave_id, datos.get("nombre", "Usuario Nuevo"), datos.get("saldoPendiente", 0.0))
            return True

    async def consultar_registro(self, llave_id: str) -> Optional[Dict[str, Any]]:
        if not self.pool: return None
        async with self.pool.acquire() as conexion:
            query = "SELECT client_id, txt_name, num_balance FROM core_bancario WHERE client_id = $1 LIMIT 1;"
            registro = await conexion.fetchrow(query, llave_id)
            if not registro: return None
            return {
                "clienteId": registro["client_id"],
                "nombre": registro["txt_name"],
                "saldoPendiente": float(registro["num_balance"]),
                "fuenteOrigenCertificada": "POSTGRESQL_CRUD_ENGINE"
            }

    async def actualizar_registro(self, llave_id: str, datos_nuevos: Dict[str, Any]) -> bool:
        if not self.pool: return False
        async with self.pool.acquire() as conexion:
            query = "UPDATE core_bancario SET num_balance = $1 WHERE client_id = $2;"
            await conexion.execute(query, datos_nuevos.get("saldoPendiente", 0.0), llave_id)
            return True

    async def borrar_registro(self, llave_id: str) -> bool:
        if not self.pool: return False
        async with self.pool.acquire() as conexion:
            query = "DELETE FROM core_bancario WHERE client_id = $1;"
            await conexion.execute(query, llave_id)
            return True

    async def desconectar(self) -> None:
        if self.pool: await self.pool.close()