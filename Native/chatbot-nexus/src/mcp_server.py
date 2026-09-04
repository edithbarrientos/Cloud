import os
import time
import json
import logging
from uuid import uuid4
from mcp.server.fastmcp import FastMCP
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    BinaryQuantization, BinaryQuantizationConfig,
    Filter, FieldCondition, MatchValue, HnswConfigDiff
)
from src.utils import medir_telemetria_async

logger = logging.getLogger("nexus-mcp-qdrant")

QDRANT_HOST = os.getenv("QDRANT_HOST", "127.0.0.1")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
COLECCION_CHAT = "chat_history"

class QdrantConnectionManager:
    _instance = None
    _client = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(QdrantConnectionManager, cls).__new__(cls)
        return cls._instance

    def obtener_cliente(self) -> QdrantClient:
        if self._client is None:
            self._client = self._conectar_con_backoff()
        return self._client

    def _conectar_con_backoff(self, max_retries: int = 5, initial_delay: float = 1.0) -> QdrantClient:
        delay = initial_delay
        for i in range(max_retries):
            try:
                client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, timeout=2.0, prefer_grpc=True)
                client.get_collections()
                logger.info("Conexión exitosa con el Connection Pool de Qdrant.")
                return client
            except Exception:
                logger.warning(f"Intento {i+1}/{max_retries} fallido. Reintentando en {delay}s...")
                time.sleep(delay)
                delay *= 2
        logger.critical("Imposible conectar con Qdrant.")
        return None

connection_manager = QdrantConnectionManager()

def inicializar_base_vectorial():
    client = connection_manager.obtener_cliente()
    if not client: return
    try:
        if not client.collection_exists(collection_name=COLECCION_CHAT):
            client.create_collection(
                collection_name=COLECCION_CHAT,
                vectors_config=VectorParams(size=1024, distance=Distance.COSINE, on_disk=True),
                hnsw_config=HnswConfigDiff(on_disk=True, payload_m=16),
                quantization_config=BinaryQuantization(binary=BinaryQuantizationConfig(always_ram=True))
            )
            client.create_payload_index(collection_name=COLECCION_CHAT, field_name="customer_id", field_schema="keyword")
    except Exception as e:
        logger.critical(f"Fallo de inicialización en base vectorial: {str(e)}")

# --- NUEVA INSTANCIACIÓN DEFINITIVA CON FASTMCP ---
mcp = FastMCP("mcp-qdrant-service")

# --- REGISTRO DE HERRAMIENTAS CON FASTMCP ---
@mcp.tool(name="buscar_contexto_similares", description="Busca las conversaciones pasadas más parecidas del usuario actual.")
@medir_telemetria_async("NODE_03_MCP_SERVER")
async def buscar_contexto_similares(customer_id: str, vector_embedding: list[float], limit: int = 2) -> str:
    client = connection_manager.obtener_cliente()
    if not client: return "Error: Qdrant offline"
    try:
        filtro_usuario = Filter(must=[FieldCondition(key="customer_id", match=MatchValue(value=customer_id))])
        search_result = client.search(
            collection_name=COLECCION_CHAT,
            query_vector=vector_embedding,
            query_filter=filtro_usuario,
            limit=limit
        )
        res = [
            {"score": hit.score, "ticket_id": hit.payload.get("ticket_id"), "issue_category": hit.payload.get("issue_category"), "summary": hit.payload.get("summary")}
            for hit in search_result
        ]
        return json.dumps(res)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

@mcp.tool(name="almacenar_historial_vector", description="Guarda el mensaje procesado por el chatbot, su metadata semántica y su embedding.")
@medir_telemetria_async("NODE_03_MCP_SERVER")
async def almacenar_historial_vector(ticket_id: str, customer_id: str, issue_category: str, summary: str, raw_message: str, confidence: float, source: str, vector_embedding: list[float]) -> str:
    client = connection_manager.obtener_cliente()
    if not client: return "Error: Qdrant offline"
    try:
        embedding_id = str(uuid4())
        point = PointStruct(
            id=embedding_id, vector=vector_embedding,
            payload={
                "ticket_id": ticket_id, "customer_id": customer_id,
                "issue_category": issue_category, "summary": summary,
                "raw_message": raw_message, "confidence": confidence, "source": source
            }
        )
        client.upsert(collection_name=COLECCION_CHAT, points=[point], wait=False)
        return json.dumps({"status": "success", "embedding_id": embedding_id})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

if __name__ == "__main__":
    inicializar_base_vectorial()
    # Arranca automáticamente el servidor stdio nativo de forma síncrona/asíncrona integrada
    mcp.run()
