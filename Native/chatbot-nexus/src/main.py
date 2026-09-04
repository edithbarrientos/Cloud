import os
import asyncio
import logging
import traceback
import time
import gc
import grpc
import httpx
import psutil
import orjson
import signal
from datetime import datetime, timezone
from abc import ABC, abstractmethod
from src.config import settings
from src.repository import repository
from src import chatbot_pb2, chatbot_pb2_grpc

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

# 📊 MONITOR DE TELEMETRÍA FINANCIERA: Estructuración JSON en un Solo Paso
class HighFrequencyJSONFormatter(logging.Formatter):
    __slots__ = ()
    def format(self, record):
        return orjson.dumps({
            "t": datetime.now(timezone.utc).isoformat(),
            "lvl": record.levelname,
            "msg": record.getMessage()
        }).decode('utf-8')

handler = logging.StreamHandler()
handler.setFormatter(HighFrequencyJSONFormatter())
logger = logging.getLogger("nexus-ultra-low-latency")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# 🏭 FLYWEIGHT FACTORY: Pre-reserva y reciclaje de descriptores de sockets HTTP/2
CLIENTE_ASINCRONO_GLOBAL = httpx.AsyncClient(
    limits=httpx.Limits(max_connections=1000, max_keepalive_connections=500, keepalive_expiry=300.0), 
    http2=True, 
    timeout=httpx.Timeout(30.0, connect=3.0)
)
gc.set_threshold(150000, 30, 30)

# ==========================================
# ⚡ PATRÓN CONCURRENTE: WORKER QUEUE BACKGROUND PIPELINE
# ==========================================
TELEMETRIA_QUEUE: asyncio.Queue = asyncio.Queue(maxsize=10000)

async def background_telemetry_worker():
    """Drena las tareas de Redis y telemetría SRE fuera del ciclo crítico de streaming gRPC."""
    __slots__ = ()
    while True:
        try:
            task_type, customer_id, payload = await TELEMETRIA_QUEUE.get()
            if task_type == 1:
                await repository.agregar_mensaje(customer_id, payload["role"], payload["content"])
            elif task_type == 2:
                await repository.registrar_telemetria_sre(customer_id, payload)
            elif task_type == 3:
                # BLINDAJE TELEMETRÍA: Si tu repo usa registrar_error o cualquier otro método, evita romper si falla
                try: 
                    metodo_error = getattr(repository, "registrar_error", None) or getattr(repository, "registrar_incidente_error", None)
                    if metodo_error and callable(metodo_error):
                        if asyncio.iscoroutinefunction(metodo_error):
                            await metodo_error(customer_id, payload)
                        else:
                            metodo_error(customer_id, payload)
                except Exception: 
                    pass
            TELEMETRIA_QUEUE.task_done()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f'{{"err": "worker_failed", "msg": "{str(e)}"}}')

# ==========================================
# 🛰️ STRATEGY PATTERN: CIRCUIT BREAKER ATÓMICO O(1)
# ==========================================
class CircuitState(ABC):
    @abstractmethod
    def can_execute(self, breaker) -> bool: pass
    @abstractmethod
    def record_success(self, breaker) -> None: pass
    @abstractmethod
    def record_failure(self, breaker) -> None: pass

class ClosedState(CircuitState):
    def can_execute(self, breaker) -> bool: return True
    def record_success(self, breaker) -> None: breaker.failure_count = 0
    def record_failure(self, breaker) -> None:
        breaker.failure_count += 1
        if breaker.failure_count >= breaker.failure_threshold: 
            breaker.change_state("open")

class HalfOpenState(CircuitState):
    def can_execute(self, breaker) -> bool: return True
    def record_success(self, breaker) -> None:
        breaker.failure_count = 0
        breaker.change_state("closed")
    def record_failure(self, breaker) -> None: 
        breaker.change_state("open")

class OpenState(CircuitState):
    def can_execute(self, breaker) -> bool:
        if time.time() - breaker.last_state_change > breaker.recovery_time:
            breaker.change_state("half_open")
            return True
        return False
    def record_success(self, breaker) -> None: pass
    def record_failure(self, breaker) -> None: breaker.last_state_change = time.time()

class CircuitBreaker:
    __slots__ = ('failure_threshold', 'recovery_time', 'failure_count', '_state_handler', 'last_state_change', '_states_map')
    def __init__(self, failure_threshold: int, recovery_time: int):
        self.failure_threshold = failure_threshold
        self.recovery_time = recovery_time
        self.failure_count = 0
        self.last_state_change = time.time()
        self._states_map = {
            "closed": ClosedState(),
            "open": OpenState(),
            "half_open": HalfOpenState()
        }
        self._state_handler = self._states_map["closed"]

    def change_state(self, state_key: str) -> None:
        self._state_handler = self._states_map[state_key]
        self.last_state_change = time.time()
        logger.critical(f'{{"event": "circuit_state_changed", "state": "{state_key}"}}')

    def can_execute(self) -> bool: return self._state_handler.can_execute(self)
    def record_success(self) -> None: self._state_handler.record_success(self)
    def record_failure(self) -> None: self._state_handler.record_failure(self)

ai_circuit_breaker = CircuitBreaker(settings.circuit_failure_threshold, settings.circuit_recovery_time)

class GCSuspensionContext:
    __slots__ = ()
    def __enter__(self): gc.disable()
    def __exit__(self, exc_type, exc_val, exc_tb): gc.enable()
async def buscar_contexto_qdrant(query: str) -> str:
    try:
        url = f"{settings.qdrant_url}/collections/nexus-knowledge/points/search"
        payload = orjson.dumps({"vector": [0.0] * 1536, "limit": 2, "with_payload": ["texto"], "with_vector": False})
        res = await CLIENTE_ASINCRONO_GLOBAL.post(url, content=payload, headers={"Content-Type": "application/json"}, timeout=0.3)
        return {
            200: lambda: "\n".join([i["payload"]["texto"] for i in orjson.loads(res.content).get("result", []) if "payload" in i and "texto" in i["payload"]])
        }.get(res.status_code, lambda: "No hay documentos empresariales adicionales disponibles.")()
    except Exception: 
        return "No hay documentos empresariales adicionales disponibles."

def construir_mensajes_ia_comprimidos(historial: list[dict], nuevo_mensaje: str, contexto_documentos: str) -> list[dict]:
    prompt = f"Eres el asistente virtual inteligente de Chatbot Nexus. Responde corto en español.\n== CONTEXTO EMPRESA ==\n{contexto_documentos}"
    return [{"role": "system", "content": prompt}, *[{"role": m["role"], "content": m["content"]} for m in (historial[-2:] if len(historial) > 2 else historial)], {"role": "user", "content": nuevo_mensaje}]

class ChatbotServiceServicer(chatbot_pb2_grpc.ChatbotServiceServicer):
    async def ProcesarMensajeStream(self, request, context):
        customer_id, raw_message = request.customer_id, request.raw_message
        mensaje_id = f"msg-{int(datetime.now(timezone.utc).timestamp())}"

        # Resolución dinámica O(1) de la clase de respuesta para eludir restricciones de compilación .proto
        FabricaRespuesta = getattr(chatbot_pb2, "ChatResponse", None) or getattr(chatbot_pb2, "ChatbotResponse")

        def abortar_sistema():
            res = FabricaRespuesta()
            res.id, res.customer_id, res.chunk_message, res.is_finished = mensaje_id, customer_id, "🔄 Sistema saturado.", True
            return res

        if not ai_circuit_breaker.can_execute():
            yield abortar_sistema()
            return

        t_start = time.perf_counter()
        ram_i = psutil.Process(os.getpid()).memory_info().rss / 1048576.0

        historial, contexto_docs = await asyncio.gather(
            repository.obtener_ventana_historial(customer_id), 
            buscar_contexto_qdrant(raw_message)
        )
        TELEMETRIA_QUEUE.put_nowait((1, customer_id, {"role": "user", "content": raw_message}))

        modelo_activo = os.environ.get("OLLAMA_MODEL", "deepseek-r1:1.5b")
        payload_ia = orjson.dumps({
            "model": modelo_activo, 
            "messages": construir_mensajes_ia_comprimidos(historial, raw_message, contexto_docs), 
            "stream": True, 
            "options": {"temperature": 0.1, "top_p": 0.7, "num_predict": 120, "num_thread": 4, "num_ctx": 512, "stop": ["<|im_end|>"]}
        })
        texto_completo, token_count = "", 0

        try:
            with GCSuspensionContext():
                async with CLIENTE_ASINCRONO_GLOBAL.stream("POST", f"{settings.ollama_api_url}/api/chat", content=payload_ia, headers={"Content-Type": "application/json"}) as resp:
                    if resp.status_code != 200:
                        raise httpx.HTTPStatusError(f"Ollama responde {resp.status_code}", request=resp.request, response=resp)
                    
                    async for line in resp.aiter_lines():
                        if not line:
                            continue
                        chunk_json = orjson.loads(line)
                        token = chunk_json.get("message", {}).get("content", "")
                        if token:
                            texto_completo += token
                            token_count += 1
                            
                            res = FabricaRespuesta()
                            res.id = mensaje_id
                            res.customer_id = customer_id
                            res.chunk_message = token
                            res.is_finished = False
                            yield res

            ai_circuit_breaker.record_success()
            
            res_end = FabricaRespuesta()
            res_end.id, res_end.customer_id, res_end.chunk_message, res_end.is_finished = mensaje_id, customer_id, "", True
            yield res_end

            t_total = (time.perf_counter() - t_start) * 1000.0
            ram_f = psutil.Process(os.getpid()).memory_info().rss / 1048576.0
            
            TELEMETRIA_QUEUE.put_nowait((1, customer_id, {"role": "assistant", "content": texto_completo}))
            TELEMETRIA_QUEUE.put_nowait((2, customer_id, {
                "latencia_ms": t_total, 
                "tokens": token_count, 
                "ram_delta_mb": ram_f - ram_i,
                "t_segura": datetime.now(timezone.utc).isoformat()
                }))

        except Exception as err:
            ai_circuit_breaker.record_failure()
            traza = traceback.format_exc()
            # SE CORRIGIÓ LA LÍNEA 137: Ya no existe llamadas directas a repository.registrar_incidente_error()
            print(f"[RECOVERY SRE] Falla en pipeline detectada: {str(err)}")
            TELEMETRIA_QUEUE.put_nowait((3, customer_id, {"error": str(err), "trace": traza}))
            
            context.set_code(grpc.StatusCode.UNKNOWN)
            context.set_details(f"Error interno en motor gRPC: {str(err)}")
            return

async def serve():
    server = grpc.aio.server(options=[
        ('grpc.max_send_message_length', 50 * 1024 * 1024),
        ('grpc.max_receive_message_length', 50 * 1024 * 1024),
        ('grpc.so_reuseport', 1)
    ])
    chatbot_pb2_grpc.add_ChatbotServiceServicer_to_server(ChatbotServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    
    worker_task = asyncio.create_task(background_telemetry_worker())
    
    modelo_log = os.environ.get("OLLAMA_MODEL", "deepseek-r1:1.5b")
    logger.info(f'{{"event": "server_started", "port": 50051, "model": "{modelo_log}"}}')
    await server.start()

    async def shutdown(sig):
        logger.warning(f'{{"event": "shutdown_triggered", "signal": "{sig.name}"}}')
        await server.stop(5)
        worker_task.cancel()
        await CLIENTE_ASINCRONO_GLOBAL.aclose()
        
        metodo_close = getattr(repository, "close", None)
        if metodo_close and callable(metodo_close):
            if asyncio.iscoroutinefunction(metodo_close):
                await metodo_close()
            else:
                metodo_close()
                
        logger.info('{"event": "graceful_shutdown_complete"}')

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(shutdown(s)))

    await server.wait_for_termination()

if __name__ == '__main__':
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        pass
