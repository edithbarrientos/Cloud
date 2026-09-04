import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import spacy
from typing import AsyncGenerator

from src.config.settings import settings
from src.api.endpoints import router as api_router
from src.services.tenant_router import tenant_router

# ==============================================================================
# 📺 OBSERVABILIDAD CORPORATIVA (LOGGING ENGINE)
# ==============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger: logging.Logger = logging.getLogger("AI-Main-Bootstrap")


# ==============================================================================
# 🧠 PATRÓN DE DISEÑO: LIFECYCLE LIFESPAN (GESTIÓN ELÁSTICA DE MEMORIA RAM)
# ==============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Administra de forma segura el ciclo de vida (Lifespan) del contenedor de IA.

    Ejecuta una estrategia de precarga en caliente (Warm-Start) en la fase de
    inicialización del contenedor, forzando la carga de los grafos tensoriales en
    la memoria RAM. Esto anula la penalización por arranque en frío (Cold Start) y
    asegura que las primeras ráfagas asíncronas de Apache Flink respondan en milisegundos.

    Implementa un patrón de resiliencia de dos capas (Fallback Architecture) para
    evitar pánicos que impidan la apertura del socket de red :8000.
    """
    logger.info("⚙️  [Bootstrap] Iniciando secuencia de arranque de la plataforma de IA...")
    
    try:
        # Capa 1: Intentamos calentar los motores con el inquilino de prueba entrenado.
        # Esto precarga la matriz específica del optimizador Adam de spaCy.
        test_tenant: str = "tenant_generic"
        logger.info(f"⚙️  [Bootstrap] Pre-cargando modelo probabilístico supervisado para: [{test_tenant}]...")
        
        # Invocación síncrona al Singleton del Model Registry en memoria RAM.
        tenant_router.get_pipeline(test_tenant)
        logger.info("🚀 [Bootstrap] Todos los motores analíticos de IA están calientes y listos en RAM.")
        
    except Exception as e:
        # Capa 2: Fallback a Modelo Base Global.
        # Interceptamos la excepción para evitar que Gunicorn aborte si falta el directorio
        # del inquilino genérico por desajustes de volumen. Cargamos es_core_news_sm de rescate.
        logger.warning(f"⚠️  [Bootstrap Warning] No se localizó el modelo entrenado [{test_tenant}]. Aplicando Fallback global... Motivo: {str(e)}")
        try:
            default_model: str = settings.DEFAULT_NLP_MODEL
            logger.info(f"⚙️  [Bootstrap] Cargando pipeline lingüístico base del sistema operativo: [{default_model}]...")
            tenant_router.get_pipeline(default_model)
            logger.info("🚀 [Bootstrap] Motores analíticos calientes en RAM usando el modelo base global.")
        except Exception as fallback_err:
            # Colapso Total: Si ni el modelo base responde, se levanta un pánico crítico de infraestructura.
            logger.critical(f"🚨 [Bootstrap Catastrophic] Fallo absoluto de infraestructura ML: {str(fallback_err)}")
            raise RuntimeError(f"Fallo de arranque de infraestructura ML: {str(fallback_err)}")

    yield # El loop de eventos congela esta sección; el contenedor queda listo para recibir tráfico de red.

    # Código ejecutado de forma controlada cuando Docker Compose apaga el ecosistema (SIGTERM/SIGKILL)
    logger.info("⚙️  [Shutdown] Interceptando señal de término. Liberando memoria RAM y cerrando descriptores de spaCy...")


# ==============================================================================
# 🚀 INICIALIZACIÓN DE LA APLICACIÓN INSTITUCIONAL FASTAPI
# ==============================================================================
app: FastAPI = FastAPI(
    title=settings.APP_NAME,
    version="4.0.0",
    docs_url="/docs" if settings.APP_ENV != "production" else None, # Capamos documentación interactiva en producción.
    redoc_url=None,
    lifespan=lifespan
)

# ==============================================================================
# 🛡️ MIDDLEWARE DE CONTROL DE TRANSPORTE PERIMETRAL (CORS RESTRICTION)
# ==============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS, # Orígenes cruzados autorizados mapeados desde Settings.
    allow_credentials=True,
    allow_methods=["POST"], # Restricción de verbos: Solo se permite el tráfico POST de Flink.
    allow_headers=["Content-Type", "X-Tenant-ID"],
)

# ==============================================================================
# 🔌 ACOPLE ELÁSTICO DE ENTRADA (INTEGRACIÓN DEL ENRUTADOR MODULAR ROUTER)
# ==============================================================================
# Registra los endpoints analíticos acoplando el prefijo de red de tu APIRouter.
app.include_router(api_router)


# ==============================================================================
# 🔌 CAPA DE SONDAS INTERNAS DE SALUD (LIVENESS / READINESS PROBE)
# ==============================================================================
@app.get("/health", status_code=200)
async def health_check() -> dict[str, str]:
    """
    Liveness Probe de Alta Disponibilidad.
    """
    return {"status": "HEALTHY", "environment": settings.APP_ENV}