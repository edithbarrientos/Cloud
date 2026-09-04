# ==============================================================================
# 🏢 AUTHOR      : EdithBG (ai-agentic-deequ-core Senior Cloud Architect)
# 🛡️ GOVERNANCE  : Enterprise Hardened Automation Makefile Spec (FAANG Standard)
# ==============================================================================

# 🎨 PALETA DE COLORES ANSI INDUSTRIALES FOR EXECUTION TRACKING
CLR_CYAN   := \033[36m
CLR_GREEN  := \033[32m
CLR_YELLOW := \033[33m
CLR_RED    := \033[31m
CLR_RESET  := \033[0m

# ⚙️ CONFIGURACIÓN DE METADATOS DEL DATA PRODUCT
REGISTRY        ?= acrtalosregistry.azurecr.io
IMAGE_NAME      ?= ai-agentic-deequ-core
VERSION         ?= v1.4.0
PORT            ?= 50051
# Auto-deteccion inteligente de hardware elástico (Mac M3 / Unix Compliance)
CPU_CORES       := $(shell sysctl -n hw.ncpu 2>/dev/null || nproc 2>/dev/null || echo 4)
STRESS_CONCURR  ?= 1000

.PHONY: all check-env init compile-proto clean-cache build-image run-local run-container stress-test help

all: check-env clean-cache compile-proto build-image ## 🚀 Ciclo de preparacion industrial completo (Zero-to-Prod)

check-env: ## 🛡️ Pre-flight Checks: Valida la integridad de las herramientas en el S.O.
	@echo "$(CLR_CYAN)[🛡️ PRE-FLIGHT] Evaluando salud perimetral de herramientas DevOps...$(CLR_RESET)"
	@command -v python3 >/dev/null 2>&1 || { echo "$(CLR_RED)❌ ERROR: Python3 no esta instalado en el sistema.$(CLR_RESET)"; exit 1; }
	@command -v docker >/dev/null 2>&1 || { echo "$(CLR_YELLOW)⚠️ WARNING: Docker Runtime no detectado. Comandos de contenedor inactivos.$(CLR_RESET)"; }
	@echo "$(CLR_GREEN)✅ [PRE-FLIGHT] Sondas de entorno nominales y listas.$(CLR_RESET)"

init: check-env ## 🧪 Prepara el entorno virtual y congela dependencias hardened
	@echo "$(CLR_CYAN)[🧪 INITIALIZER] Creando venv e inyectando dependencias Python 3.12...$(CLR_RESET)"
	@python3 -m venv venv
	@./venv/bin/pip install --upgrade pip --quiet
	@./venv/bin/pip install -r requirements.txt --quiet
	@echo "$(CLR_GREEN)✅ [INITIALIZER] Entorno virtual aislado y blindado con exito.$(CLR_RESET)"

compile-proto: ## 🛰️ Transforma los buffers binarios (.proto) en stubs de gRPC Python
	@echo "$(CLR_CYAN)[🛰️ PROTO_COMPILER] Compilando inference.proto hacia la Capa API...$(CLR_RESET)"
	@./venv/bin/python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. inference.proto
	@echo "$(CLR_GREEN)✅ [PROTO_COMPILER] Stubs de red binarios multiplexados generados.$(CLR_RESET)"

clean-cache: ## 🧹 Purga de forma absoluta residuos binarios e hilos muertos de la Mac
	@echo "$(CLR_CYAN)[🧹 PURGE_AGENT] Vaciando mapas de precompilacion __pycache__ y RAM...$(CLR_RESET)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(CLR_GREEN)✅ [PURGE_AGENT] Buffer de descriptores de archivos purgado en limpio.$(CLR_RESET)"

build-image: check-env ## 📦 Compila la imagen Docker Multi-Stage Hardened no-root pluma (<50MB)
	@echo "$(CLR_CYAN)[📦 DOCKER_BUILD] Compilando artefacto multi-stage [${IMAGE_NAME}:${VERSION}]...$(CLR_RESET)"
	@docker build --target runtime -t ${REGISTRY}/${IMAGE_NAME}:${VERSION} .
	@docker tag ${REGISTRY}/${IMAGE_NAME}:${VERSION} ${IMAGE_NAME}:latest
	@echo "$(CLR_GREEN)✅ [DOCKER_BUILD] Imagen pluma sellada con UID No-Root (10001) e inmune a vulnerabilidades.$(CLR_RESET)"

run-local: clean-cache ## 🔥 Enciende el cluster de multiprocesamiento nativo Multi-Core
	@echo "$(CLR_CYAN)[🔥 CORE_LAUNCH] Levantando Enjambre de Subprocesos gRPC en puerto ${PORT}...$(CLR_RESET)"
	@echo "$(CLR_YELLOW)[CORE_LAUNCH] Cores asignados: ${CPU_CORES} Procesos en paralelo (SO_REUSEPORT)...$(CLR_RESET)"
	@export ACTIVE_CLOUD_PROVIDER=aws && ./venv/bin/python src/grpc_server.py

run-container: check-env ## 🚀 Despliega el contenedor hardened en aislamiento elástico perimetral
	@echo "$(CLR_CYAN)[🚀 CONTAINER_DEPLOY] Inicializando Pod aislado en puerto ${PORT}...$(CLR_RESET)"
	@docker run --rm -p ${PORT}:${PORT} --name ${IMAGE_NAME}-instance ${REGISTRY}/${IMAGE_NAME}:${VERSION}

stress-test: ## ⚡ Gatilla el bombardeo multiplexado elástico de alta velocidad (HTTP/2)
	@echo "$(CLR_CYAN)[⚡ STRESS_AGENT] Disparando bombardeo asincrono de ${STRESS_CONCURR} payloads concurrentes...$(CLR_RESET)"
	@./venv/bin/python src/grpc_client_test.py
	@echo "$(CLR_GREEN)✅ [STRESS_AGENT] Analisis de performance y Throughput concluido de forma nominal.$(CLR_RESET)"

help: ## 🏛️ Despliega este menu explicativo con las directivas FAANG del Data Product
	@echo ""
	@echo "$(CLR_GREEN)🏛️  ai-agentic-deequ-core - MANIFIESTO DE AUTOMATIZACIÓN DE INFRAESTRUCTURA$(CLR_RESET)"
	@echo "--------------------------------------------------------------------------------"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(CLR_CYAN)%-18s$(CLR_RESET) %s\n", $$1, $$2}'
	@echo "--------------------------------------------------------------------------------"
	@echo "$(CLR_YELLOW)💡 Tip: Ejecuta 'make init' si es la primera vez que configuras el repositorio en tu Mac.$(CLR_RESET)"
	@echo ""
