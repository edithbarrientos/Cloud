import os
import time
import json
import logging
import psutil
from functools import wraps

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

class DevProdLogFormatter(logging.Formatter):
    def format(self, record):
        RESET = "\033[0m"
        CYAN = "\033[36m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        MAGENTA = "\033[35m"
        BLUE = "\033[34m"
        
        iconos = {
            "DEBUG": "🐛 [DEBUG]", "INFO": "🟢 [INFO ]", "WARNING": "⚠️  [WARN ]",
            "ERROR": "❌ [ERROR]", "CRITICAL": "🚨 [CRIT ]"
        }
        icon = iconos.get(record.levelname, "📝")
        message = record.getMessage()

        if ENVIRONMENT == "production":
            return f'{{"time": "{self.formatTime(record)}", "level": "{record.levelname}", "component": "{record.name}", "message": {message}}}'
        else:
            if "📊 [TELEMETRÍA]" in message:
                message = f"{CYAN}{message}{RESET}"
            elif "⏱️  [METRICA IA]" in message:
                message = f"{YELLOW}{message}{RESET}"
            elif "📊 [METRICAS E2E]" in message:
                message = f"{GREEN}{message}{RESET}"
            elif "💾 [MEMORIA]" in message:
                message = f"{MAGENTA}{message}{RESET}"
            elif "🔌 [POOL_SALUD]" in message:
                message = f"{BLUE}{message}{RESET}"

            return f"{icon} {self.formatTime(record)} | {record.name} ──► {message}"

handler = logging.StreamHandler()
handler.setFormatter(DevProdLogFormatter())
logging.basicConfig(level=LOG_LEVEL, handlers=[handler])
logger = logging.getLogger("nexus-telemetry")

def obtener_uso_memoria_mb() -> float:
    proceso = psutil.Process(os.getpid())
    return proceso.memory_info().rss / (1024 * 1024)

def medir_telemetria_async(componente: str):
    def decorador(func):
        @wraps(func)
        async def envoltura(*args, **kwargs):
            mem_inicial = obtener_uso_memoria_mb()
            start_time = time.perf_counter()
            try:
                resultado = await func(*args, **kwargs)
                latency_ms = (time.perf_counter() - start_time) * 1000
                mem_final = obtener_uso_memoria_mb()
                logger.info(f"📊 [TELEMETRÍA] Componente: {componente} | Operación: {func.__name__} | Latencia: {latency_ms:.2f}ms")
                logger.info(f"💾 [MEMORIA] Componente: {componente} | RAM Base: {mem_inicial:.2f}MB | RAM Final: {mem_final:.2f}MB | Delta: {max(0.0, mem_final - mem_inicial):.2f}MB")
                return resultado
            except Exception as e:
                raise e
        return envoltura
    return decorador

def resolver_url_servicio(nombre_env: str, host_defecto: str, puerto_defecto: int) -> str:
    url_proveída = os.getenv(nombre_env, "").strip()
    match url_proveída:
        case "":
            return f"http://{host_defecto}:{puerto_defecto}"
        case url if url.startswith("http://") or url.startswith("https://"):
            return url
        case _:
            return f"http://{url_proveída}"
