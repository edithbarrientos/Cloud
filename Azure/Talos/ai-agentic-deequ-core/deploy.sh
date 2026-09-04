#!/usr/bin/env bash
# ==============================================================================
# 🏢 AUTHOR      : EdithBG (ai-agentic-deequ-core Senior Cloud Architect)
# 🛡️ GOVERNANCE  : High-Performance Atomic Deployment Trigger (FAANG Standard)
# ==============================================================================
set -e

# Paleta ANSI de control ejecutivo
CLR_CYAN="\033[36m"
CLR_GREEN="\033[32m"
CLR_RESET="\033[0m"

echo -e "${CLR_CYAN}[🚀 PIPELINE] Iniciando ciclo de liberacion atomica multinube...${CLR_RESET}"

# 1. Ejecutar las reglas nominales del Makefile local
make clean-cache
make compile-proto
make build-image

# 2. Aprovisionar el Namespace en el cluster de Kubernetes
echo -e "${CLR_CYAN}[☸️ KUBERNETES] Sincronizando namespaces e infraestructura...${CLR_RESET}"
kubectl create namespace data-mesh-governance --dry-run=client -o yaml | kubectl apply -f -

# 3. Aplicar los manifiestos endurecidos de orquestacion elistica
kubectl apply -f deployments/kubernetes/k8s_deployment.yaml

echo -e "${CLR_GREEN}✅ [PIPELINE_SUCCESS] ¡Data Product 'ai-agentic-deequ-core' desplegado con exito total!${CLR_RESET}"
