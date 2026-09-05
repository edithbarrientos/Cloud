# Enterprise GenAI Agents - Auditoría de Inventario Expresa por API

Este repositorio contiene la Prueba de Concepto (PoC) corporativa para el despliegue de un **Agente Autónomo de Inteligencia Artificial** enfocado en la automatización de la toma de decisiones en la cadena de suministro de la empresa.

El sistema expone un endpoint seguro que intercepta solicitudes de órdenes urgentes de ventas, valida los datos, consulta los balances de inventario de forma concurrente en el ERP corporativo y genera un dictamen ejecutivo de auditoría en segundos utilizando **Semantic Kernel v1+** y **FastAPI**.

---

## 💼 Caso de Uso y Valor de Negocio

### El Problema Tradicional
La verificación manual de existencias físicas frente a órdenes de compra masivas en el sistema ERP (SAP/Oracle) genera cuellos de botella burocráticos, errores humanos en la captura y retrasos en los despachos logísticos de más de 24 horas.

### La Solución Implementada
Un Agente de IA Orquestador que:
*   **Blinda los datos**: Valida formatos de SKU corporativos mediante contratos estrictos de Pydantic v2.
*   **Opera de forma concurrente**: Consulta asíncronamente las bases de datos de inventario.
*   **Aplica razonamiento cognitivo**: Genera reportes gerenciales estructurados con **Azure OpenAI (GPT-4o)** que dictaminan la viabilidad de la orden en **3.5 segundos**.

---


## 💼 Componentes diseñado específicamente para tu estructura de proyecto


<div style="overflow-x: auto;">
<pre>
+---------------------------------------------------------------------------------------------------------+

|                                    ENTERPRISE GENAI AGENT SYSTEM                                        |
+---------------------------------------------------------------------------------------------------------+

|                                                                                                         |
|  +---------------------------------------------------------------------------------------------------+  |
|  | [src/app/] - FastAPI Application Container                                                         | |
|  |                                                                                                    | |
|  |   +------------------+  Invocación Async   +-----------------------+                               | |
|  |   |    [api.py]      |-------------------->|    [plugins/erp.py]   |                               | |
|  |   |                  |                     |                       |                               | |
|  |   |  Servidor API    |                     |  Conector Asíncrono   |                               | |
|  |   |  y Orquestador   |                     |  SAP / Oracle / ERP   |                               | |
|  |   |   del Agente     |                     +-----------------------+                               | |
|  |   +------------------+                                 |                                           | |
|  |         |                                              | Consulta Stock Real                       | |
|  |         | Carga Variables                              v                                           | |
|  |         v                                   +---------------------+                                | |
|  |   +------------------+                      |   [Sistema ERP]     |                                | |
|  |   |  [core/config]   |                      | (Base de Datos / API)  |                             | |
|  |   |                  |                      +---------------------+                                | |
|  |   | Pydantic Schema  |                                                                             | |
|  |   |   y Validación   |                                                                             | |
|  |   +------------------+                                                                             | |
|  +---------|-----------------------------------------------------------------------------------------+  |
|            |                                                                                            |
|            | Lee .env / Secretos                                                                        |
|            v                                                                                            |
|  +----------------------+                                                                               |
|  |       [.env]         | <================================+                                            |
|  |  Variables de Entorno|                                  |                                            |
|  +----------------------+                                  |                                            |
|                                                            | Inyecta Secretos                           |
|                                                            | de forma segura                            |
|  +---------------------------------------------------------|-----------------------------------------+  |
|  | [infrastructure/] - Azure Cloud Platform (Terraform)    |                                         |  |
|  |                                                         |                                         |  |
|  |   +-------------------------+                 +-------------------------+                         |  |
|  |   | [Databricks Workspace]  |                 | [Databricks Secret]     |                         |  |
|  |   |                         |                 |                         |                         |  |
|  |   |  • Clúster ML (Runtime) |                 | • audit-agent-secrets   |                         |  |
|  |   |  • Vector Search        |                 +-------------------------+                         |  |
|  |   +-------------------------+                              ^                                      |  |
|  |                ^                                           |                                      |  |
|  |                | Despliega e Interconecta                  | Resguarda tokens                     |  |
|  |                +----------------------[main.tf]------------+                                      |  |
|  |                                                                                                   |  |
|  |   +--------------------------------------------------------------------------------------------+  |  |
|  |   | [Azure Virtual Network]                                                                    |  |  |
|  |   |                                                                                            |  |  |
|  |   |   +--------------------------+              +--------------------------+                   |  |  |
|  |   |   |    [sub-db-public]       |              |    [sub-db-private]      |                   |  |  |
|  |   |   | Interfaz Pública de API  | <========--> |  Tráfico de Datos Seguro |                   |  |  |
|  |   |   +--------------------------+              +--------------------------+                   |  |  |
|  |   +--------------------------------------------------------------------------------------------+  |  |
|  +---------------------------------------------------------------------------------------------------+  |
+---------------------------------------------------------------------------------------------------------+

+---------------------------------------------------------------------------------------------------------+

|                                    TESTING & VALIDATION PIPELINE                                        |
+---------------------------------------------------------------------------------------------------------+

|                                                                                                         |
|   +-----------------------+  Bypass de API (Simulación)   +----------------------------------+          |
|   | [tests/test_agente.py]|------------------------------>| [src/app/core/ o plugins/]       |          |
|   | Pruebas de Calidad QA |                               | Validación de Lógica del Agente  |          |
|   +-----------------------+                               +----------------------------------+          |
+---------------------------------------------------------------------------------------------------------+
</pre>
</div>


## 🏗️ Descripción Detallada del Flujo


1. Punto de Entrada (api.py): Recibe la solicitud de análisis de inventario por HTTP REST de forma asíncrona. Actúa como el cerebro del agente, coordinando cuándo consultar datos y cuándo procesar el lenguaje natural.

2. Componente de Configuración (core/): Utilice Pydantic Settings para validar que todas las variables del archivo .env e infraestructura existan y tengan el formato correcto antes de arrancar el agente.

3. Capa de Extensibilidad (plugins/): El módulo erp.py se dispara de manera no bloqueante (async) para extraer el stock teórico del ERP corporativo.

4. Infraestructura Segura (infraestructura/): main.tf garantiza que todo el procesamiento pesado de incrustaciones, reglas de auditoría cruzada y búsqueda vectorial ocurre dentro del aislamiento de la subred privada de Azure Databricks, protegiendo los datos confidenciales de inventario.



## 📂 Estructura del Repositorio


<div style="overflow-x: auto;">
<pre>

enterprise-genai-agent/
├── .dockerignore         # Exclusiones de empaquetado para Docker
├── .gitignore            # Exclusiones de seguridad para el control de versiones Git
├── .env                  # Secretos locales (Excluido de Git)
├── requirements.txt      # Dependencias fijadas estables libres de conflictos
├── Dockerfile            # Empaquetado optimizado multi-stage con usuario no-root
├── infrastructure/       # Automatización de Infraestructura como Código (Terraform)
│   ├── main.tf           # Orquestador principal de Azure
│   ├── variables.tf      # Variables globales
│   ├── outputs.tf        # Salidas raíz acopladas
│   └── modules/
│       ├── ai_services/  # Backend cognitivo (Azure OpenAI GPT-4o)
│       └── monitoring/   # Backend de observabilidad (Application Insights)
├── src/                  # Código fuente productivo de la solución
│   └── app/
│       ├── api.py        # Servidor API asíncrono y control de lifespan
│       ├── core/
│       │   └── config.py # Configuración inmutable mediante Pydantic Settings
│       └── plugins/
│           ├── __init__.py # Exposición y gobierno de plugins
│           └── strategies.py # Conector resiliente al ERP (Tenacity)
└── tests/
    └── test_agente.py    # Script de bypass para pruebas rápidas de procesamiento QA
</pre>
</div>

---

## 🛠️ Guía de Ejecución y Pruebas Locales

### Prerrequisitos
*   Python 3.12 (Entorno Virtual configurado)
*   Homebrew instalado en Mac Intel
*   Colima (Motor de contenedores ligero para Mac)

### 1. Inicializar el Entorno de Desarrollo NATIVO
Si requieres validar la lógica de negocio saltándote la capa de red perimetral del sistema operativo, ejecuta el script de pruebas automatizado:

```bash
# Limpiar puertos ocupados previos por seguridad
kill -9 \$(lsof -t -i:8000 -i:8080) 2>/dev/null

# Ejecutar el bypass de pruebas por código nativo
PYTHONPATH=. ./.venv/bin/python tests/test_agente.py
```

### 2. Construcción y Arranque en Contenedores (Docker / Colima)
Para garantizar la portabilidad absoluta del agente hacia la nube, empaqueta la solución en un contenedor Linux seguro:

```bash
# A. Saneamiento de tuberías viejas del sistema operativo
sudo rm -f /var/run/docker.sock
docker context use default

# B. Encender el motor virtual de Colima
colima start

# C. Configurar el socket y compilar la imagen
export DOCKER_HOST="unix://\${HOME}/.colima/default/docker.sock"
docker build -t api-agente-negocio .

# D. Arrancar la API de agentes en el puerto alternativo limpio 8080
docker rm -f api-agente-prod 2>/dev/null
docker run -d --name api-agente-prod -p 8080:8000 \
  -e PROJECT_CONNECTION_STRING="eastus2.api.azureml.ms;sub-123;rg-genai;ws-negocio" \
  -e ERP_API_URL="https://tuempresa.internal" \
  api-agente-negocio
```

### 3. Consumo de la API Corporativa
Para recibir el **Dictamen de Auditoría IA**, extrae primero tu dirección IP de red privada en la Mac (`ipconfig getifaddr en0`) y ejecuta la consulta de red estructurada forzando el canal IPv4:

```bash
curl -4 -X POST http://<TU_IP_LOCAL>:8080/api/v1/audit \
  -H "Content-Type: application/json" \
  -d '{"sku": "PROD-777"}' -w "\n"
```

---

## 🚀 Despliegue Automatizado en la Nube con Terraform

Con la API local y el contenedor totalmente aprobados, procede al aprovisionamiento automático de los servicios cognitivos de producción (**Azure OpenAI con GPT-4o** y **Azure AI Search**):

```bash
# 1. Autenticar la terminal en la cuenta corporativa de Microsoft
az login

# 2. Entrar a la carpeta de arquitectura cloud
cd infrastructure/

# 3. Inicializar el entorno de Terraform
terraform init

# 4. Inspeccionar el plan técnico de infraestructura antes de inyectar
terraform plan

# 5. Aplicar el despliegue en la nube real de Azure
terraform apply -auto-approve
```

---

## 🔒 Gobierno, Telemetría y Control de Calidad
*   **Estándar de Formato**: Validado al 100% mediante reglas estrictas de código estático con `ruff check src/`.
*   **Monitoreo**: El ciclo de vida (`lifespan`) inyecta trazas distribuidas nativas de OpenTelemetry directo hacia **Azure Application Insights** para auditorías de uso.


---

## 🚀 Guía de Ejecución Local de la API (Estabilizada)

Para ejecutar la API de forma 100% local con costo cero, librándote de bloqueos de red externos, sigue estos pasos en tu entorno de desarrollo:

### 1. Activar el entorno de Anaconda
Asegúrate de estar posicionada en la raíz de tu proyecto e ingresa a tu ambiente activo:
```bash
conda activate genai-agent
```

### 2. Inicializar el Servidor Web (FastAPI + Uvicorn Nativo)
Ejecuta el servidor web forzando el mapeo del `PYTHONPATH` local y deshabilitando la telemetría remota. Esto activará además el sistema de logs de auditoría detallado con IP de clientes y milisegundos de procesamiento:

```bash
PYTHONPATH=. OTEL_TRACES_SAMPLER=always_off python3 -m uvicorn src.app.app:api --host 0.0.0.0 --port 8080 --log-level debug
```
*El sistema estará encendido cuando la terminal se quede en espera con la línea:* `INFO: Application startup complete.`

### 3. Verificar Salud del Sistema (Healthcheck)
Abre una **segunda pestaña o ventana de la terminal** y corre esta validación rápida para certificar que el microservicio esté respondiendo:
```bash
curl -X GET http://localhost:8080/health
```
*Respuesta JSON esperada:* `{"status":"healthy","version":"2.7.3","environment":"local_ready"}`

### 4. Consumir Endpoint de Auditoría (`POST /audit`)
En la misma segunda pestaña de la terminal, envía el payload JSON dinámico para detonar el flujo autónomo del Agente de IA:
```bash
curl -X POST http://localhost:8080/audit \
