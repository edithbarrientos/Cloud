# 🤖 Project Nexus: Chatbot Ecosystem (Nexus-Mesh)

Este proyecto implementa una arquitectura nativa de la nube (Cloud-Native) de alta disponibilidad para desplegar un ecosistema de Chatbot corporativo impulsado por Inteligencia Artificial. Utiliza orquestación en **Kubernetes (via Kind)** y contenedores ligeros sobre **Docker (via Colima)** optimizados para procesadores Intel/Mac.

---

## 🚀 Capacidades del Proyecto (Capabilities)

- **IA Conectada Local/Cloud:** Integración nativa con **Ollama** ejecutando modelos locales de alto rendimiento (`deepseek-r1:1.5b`) o APIs externas.
- **Base de Datos Vectorial de Alta Densidad:** Uso de **Qdrant** como almacén vectorial indexado para persistencia de embeddings e implementación de arquitecturas RAG (Retrieval-Augmented Generation).
- **Caché y Mensajería Ultrarrápida:** Gestión de sesiones y estados temporales de chat mediante una base de datos **Redis** en memoria.
- **UI Modular Multipropósito:** Capas de interfaces desacopladas (`dev-ui-oficial` y `dev-ui-web-oficial`) servidas eficientemente mediante Nginx Alpine y configuradas dinámicamente con Kubernetes ConfigMaps.
- **Protocolo de Control MCP:** Soporte para contenedores satélite basados en el *Model Context Protocol* (`mcp-server`) integrados al backend.
- **Estrategia Despliegue Zero-Downtime:** Configuración de actualización bajo políticas `Recreate` y validaciones de salud continuas (*Readiness* y *Liveness Probes*).

---

## 🏗️ Diagrama de Arquitectura Global por Capas

El ecosistema se divide en 5 niveles operativos desacoplados, implementando el estándar moderno de comunicación perimetral e infraestructura distribuida:

<div style="overflow-x: auto;">
<pre>

==================================================================================================
📊 CAPA 1: ACCESO PERIMETRAL (User Layer)
==================================================================================================
     [ Navegador Web del Usuario ]
                  │
                  ▼ (Tráfico Externo mapeado a http://localhost:30080)
     [ Service: dev-ui-service-real ] 
                  │
                  ▼
==================================================================================================
🔀 CAPA 2: ENRUTAMIENTO AVANZADO (Gateway API Layer)
==================================================================================================
     [ Gateway: nexus-gateway-nativo ] (Estándar Kubernetes Gateway API)
            ├── HTTPRoute: ingress.yaml (Reglas de desacoplamiento perimetral)
            └── Controlador: [ nexus-internal-proxy ] (Gestión de mallas y timeouts)
                  │
                  ├─────────────────────────────────────────┐
                  ▼ (Tráfico Web Estático)                  ▼ (Tráfico gRPC / API Multiplexado)
==================================================================================================
🎨 CAPA 3: INTERFAZ DE USUARIO / FRONTEND (Presentation Layer)
==================================================================================================
     [ Pod: dev-ui-oficial ] (Nginx Alpine Web Server)
            ├── Contenedor: nginx-container (Sirve archivos estáticos HTML/JS/CSS)
            └── Volume Mount: [ ConfigMap: ui-archivos-config ] (index.html, app.js, style.css)
                  │
                  ▼ (Llamadas asíncronas vía gRPC-Web / HTTP Streaming)
==================================================================================================
⚙️ CAPA 4: LÓGICA DE NEGOCIO / BACKEND (Application & Orchestration Layer)
==================================================================================================
     [ Service: chatbot-backend-service ] (ClusterIP Interno - Puerto 50051)
                  │
                  ▼
     [ Pod: chatbot-backend ] 
            ├── Contenedor 1: backend (Imagen local: v16 con empaquetado Python optimizado)
            └── Contenedor 2: mcp-server (Satélite Alpine para Model Context Protocol)
                  │
                  ├───────────────────────────────┼───────────────────────────────┐
                  ▼ (gRPC Nativo)                 ▼ (HTTP/REST API)               ▼ (TCP Socket)
==================================================================================================
🗄️ CAPA 5: INFRAESTRUCTURA DE DATOS E IA (Data & Core AI Infrastructure Layer)
==================================================================================================
     [ Pod: redis-cache ]            [ Pod: ollama-deployment ]       [ Pod: qdrant-vector-db ]
     (Service: redis-cache)          (Service: ollama-service)        (Service: qdrant-service)
     - Cacheo de Contextos           - Motor de Inferencia LLM        - Engine Indexador HNSW
     - Control de Concurrencia       - Modelo: deepseek-r1:1.5b       - Distancia Coseno (Métricas)
==================================================================================================
</pre>
</div>


### 📝 Descripción de la Arquitectura 
1. **Acceso y Gateway API (Capas 1 y 2):** El proyecto sustituye los controladores Ingress tradicionales por el estándar **Gateway API**. Esto desacopla la infraestructura de red de la lógica de la aplicación mediante recursos de enrutamiento separados (`HTTPRoute`). El tráfico es recibido por el proxy de entrada (`nexus-internal-proxy`), encargado de balancear, romper hilos persistentes y proteger los microservicios internos.
2. **Presentación Desacoplada (Capa 3):** La interfaz visual corre en contenedores Nginx sin estado. En lugar de compilar el código frontend en la imagen, el servidor consume archivos inyectados dinámicamente desde un `ConfigMap` de Kubernetes (`ui-archivos-config`), permitiendo modificar la lógica visual del cliente en caliente.
3. **Procesamiento de Negocio Combinado (Capa 4):** El Pod `chatbot-backend` (**versión v16**) utiliza el patrón *Multi-Container Pod* (Sidecar). El contenedor principal procesa la lógica pesada y delega las llamadas a herramientas y APIs del sistema a un contenedor satélite ligero basado en el estándar abierto *Model Context Protocol* (`mcp-server`), maximizando la extensibilidad.
4. **Infraestructura de Datos Distribuida (Capa 5):** Diseñada para la persistencia no relacional e IA. Se compone de un almacenamiento clave-valor (`Redis`) para sesiones volátiles y cacheo de respuestas repetidas, un motor de inferencia local (`Ollama`) que aísla el procesamiento cognitivo, y una base de datos de conocimiento persistente (`Qdrant`) para potenciar el análisis contextual RAG.



## 🔄 Diagrama de Secuencia Súper Detallado

A continuación se expone la interacción síncrona y asíncrona de **todos** los componentes que participan activamente en el ciclo de vida de una petición dentro del ecosistema *Nexus Mesh*:

<div style="overflow-x: auto;">
<pre>

Usuario       Gateway API      Proxy Interno     UI (Nginx)     Backend (v16)     MCP Sidecar     Redis Cache      Qdrant DB      Ollama LLM
  │                 │                │               │                │               │                │               │              │
  │── 1. Prompt ───►│                │               │                │               │                │               │              │
  │   (HTTP Req)    │── 2. Evalúa ──►│               │                │               │                │               │              │
  │                 │   (HTTPRoute)  │── 3. Carga ──►│                │               │                │               │              │
  │                 │                │   Assets Web  │                │               │                │               │              │
  │◄─────────────────────────────────────────────────│                │               │                │               │              │
  │             4. Renderiza Chat en Pantalla        │                │               │                │               │              │
  │                                                  │                │               │                │               │              │
  │── 5. Envía Entrada de Texto ("Hola Bot") ───────►│                │               │                │               │              │
  │                                                  │── 6. Stream ──►│                │               │                │              │
  │                                                  │   (gRPC-Web)   │── 7. Check ──►│                │               │              │
  │                                                  │                │   Sesión      │── 8. Query ───►│               │              │
  │                                                  │                │               │◄─ 9. Token OK ─│               │              │
  │                                                  │                │                                │               │              │
  │                                                  │                │── 10. Generar Embeddings ─────────────────────►│              │
  │                                                  │                │◄── 11. Vectores de Contexto RAG ───────────────│              │
  │                                                  │                │                                                │              │
  │                                                  │                │── 12. Requiere Herramientas del Sistema ────►│ │              │
  │                                                  │                │◄── 13. Datos Estructurales (OS/Logs) ─────────│ │              │
  │                                                  │                │                                                │              │
  │                                                  │                │── 14. Prompt Enriquecido (Contexto + RAG) ───────────────────►│
  │                                                  │                │◄── 15. Stream de Respuesta (Chunks) ──────────────────────────│
  │                                                  │◄─ 16. Relay ───│                                                               │
  │◄── 18. Renderizado Dinámico Word-by-Word ────────│   gRPC Chunks  │                                                               │
  │                                                  │                │                                                               │

</pre>
</div>


### 📝 Descripción Paso a Paso del Flujo
- **Fase de Acceso e Ingesta (Pasos 1-4):** El usuario inicia la interacción ingresando a la URL mapeada. La solicitud llega a la **Gateway API**, la cual evalúa las políticas de seguridad de `ingress.yaml` y delega el tráfico al controlador `nexus-internal-proxy`. El proxy enruta al usuario al servidor `dev-ui-oficial` (Nginx), el cual retorna los archivos HTML/JS estáticos inyectados por el ConfigMap para renderizar la UI en el cliente.
- **Fase de Inicialización del Mensaje (Pasos 5-6):** Cuando el usuario escribe un prompt y presiona enviar, la interfaz captura el texto y abre un canal bidireccional asíncrono utilizando **gRPC-Web** hacia el contenedor principal del `chatbot-backend` (versión v16).
- **Fase de Control de Estado y Enriquecimiento Semántico (Pasos 7-11):** El backend intercepta el string y consulta inmediatamente a `Redis` para validar la sesión y recuperar el contexto temporal. Validada la sesión, el backend convierte el prompt a vectores semánticos y ejecuta una búsqueda de vecino más cercano (HNSW) en `Qdrant` para extraer información institucional complementaria (Estrategia RAG).
- **Fase de Ejecución Multicontenedor e Inferencia (Pasos 12-18):** Si el prompt requiere interactuar con el entorno del sistema operativo, el backend delega la acción al contenedor coprocesador `mcp-server`. El backend consolida todos los datos recopilados en un único prompt enriquecido y lo transmite a `Ollama` (`deepseek-r1:1.5b`), el cual retorna la respuesta en streaming continuo de vuelta a la UI.

---

## 🏗️ Patrones de Diseño Utilizados

### Patrones de Infraestructura (Cloud-Native Patterns)
- **Sidecar Pattern (Contenedor Próximo):** Implementado en el Pod de backend, donde el contenedor `mcp-server` complementa de forma independiente al motor principal (v16) para proveer contexto del sistema sin acoplar el código fuente.
- **Gateway / Reverse Proxy Pattern:** El componente `nexus-internal-proxy` centraliza el punto de entrada de la red mesh, abstrayendo la ubicación de los microservicios y protegiendo el backend de sobrecargas externas.
- **External Configuration Pattern:** Uso de `ConfigMaps` para separar los artefactos de software (`app.js`, `index.html`) del ciclo de vida del contenedor de infraestructura Nginx.

### Patrones de Código Interno (Software Design Patterns)
- **Mediator Pattern (Mediador):** El orquestador principal del backend Python coordina de forma centralizada las consultas entre `Redis`, `Qdrant` y `Ollama`, evitando que las bases de datos interactúen entre sí de forma directa.
- **Adapter Pattern (Adaptador):** Implementado para interactuar indistintamente con diferentes arquitecturas de LLM (conectores para Ollama local o APIs en la nube) bajo una misma interfaz abstracta.

---

## 🧮 Algoritmos Clave Implementados

- **Indexación Espacial HNSW (Hierarchical Navigable Small World):** Utilizado internamente por `Qdrant` para estructurar los vectores en grafos multicapa. Permite realizar búsquedas del vecino más cercano aproximado (k-NN) con una complejidad de tiempo logarítmica \(\mathcal{O}(\log N)\), vital para responder prompts en milisegundos.
- **Métrica de Similitud del Coseno:** Algoritmo matemático para comparar la distancia angular entre el vector del prompt del usuario y los vectores de conocimiento almacenados en la base de datos:
  \[\text{Similitud}(A, B) = \frac{A \cdot B}{\Vert{}A\Vert{} \Vert{}B\Vert{}}\]

---

## 📦 Librerías Core del Proyecto

Basado en la configuración inyectada dinámicamente en el entorno de ejecución del contenedor del backend, el sistema opera con las siguientes dependencias fundamentales:
- **`grpcio` & `grpcio-tools` (v1.x):** Framework de comunicación RPC de alto rendimiento utilizado para la transferencia binaria de streams de datos entre la UI, el proxy y el backend.
- **`pydantic` & `pydantic-settings` (v2.x):** Librería para la validación de estructuras de datos y el parseo estricto de variables de entorno del sistema.
- **`httpx`:** Cliente HTTP de última generación con soporte nativo asíncrono, empleado para el consumo de la API de inferencia de Ollama en flujos de streaming continuo.

---

## 🗂️ Estructura Completa de Directorios del Proyecto

El árbol de directorios del repositorio se encuentra estructurado bajo un estándar modular que separa la infraestructura elástica de la lógica de código:

<div style="overflow-x: auto;">
<pre>

📂 .
├── 📄 README.md                        # Documentación técnica principal del ecosistema
├── 📂 backend/                         # Código fuente de la lógica de negocio (Python v16)
│   ├── 🐳 Dockerfile                   # Receta de empaquetado del Backend corporativo
│   ├── 📋 requirements.txt             # Dependencias de Python estrictas (gRPC, Pydantic, etc.)
│   └── 📂 src/
│       ├── 🐍 main.py                  # Punto de entrada y orquestador del servicio gRPC
│       ├── 📂 adapters/                # Adaptadores para Ollama y clientes externos
│       └── 📂 utils/                   # Conectores y controladores matemáticos de Qdrant/Redis
├── 📂 frontend/                        # Archivos de la interfaz visual del Chatbot
│   └── 📂 assets/
│       ├── 🌐 index.html               # Estructura del cliente web servido por Nginx
│       ├── 📜 app.js                   # Lógica de renderizado asíncrono y llamadas gRPC-Web
│       └── 🎨 style.css                # Estilos visuales del Chatbot
└── 📂 k8s/                             # Orquestación de infraestructura en Kubernetes
    └── 📂 base/
        ├── ☸️ kustomization.yaml       # Archivo central de orquestación de Kustomize
        ├── ⚙️ deployment.yaml          # Definición de Namespaces, UI Oficial y Backend (v16)
        ├── 🛠️ infrastructure.yaml      # Recursos base de DB (Redis, Qdrant, Ollama)
        ├── 🖼️ nexus-front-oficial.yaml # Definiciones secundarias de visualización web
        ├── 🔀 nexus-gateway-nativo.yaml # Configuración unificada de Kubernetes Gateway API
        └── 🛣️ ingress.yaml             # Reglas HTTPRoute aplicadas al Gateway perimetral

</pre>
</div>


## 🛠️ Guía de Ejecución Completa del Proyecto (Comandos)

Sigue estrictamente esta secuencia de comandos para inicializar, inyectar y ejecutar de forma garantizada el ecosistema en tu Mac Intel con virtualización emulada:

### 1. Inicializar el Entorno Docker Mejorado (Colima)
Ejecuta el reinicio forzado asignando **4 CPUs y 6 GB de memoria RAM** (óptimo para evitar congelamientos):

```bash
# Detener y borrar instancias colgadas previas de raíz
colima stop -f
colima delete -f

# Iniciar entorno con Virtualización QEMU y Editor interactivo activo
colima start --cpu 4 --memory 6 --vm-type qemu --edit
```

> ⚠️ **IMPORTANTE:** Cuando se abra el editor interactivo de texto en tu pantalla, asegúrate de cambiar el driver de red al modo avanzado de macOS e inyectar los DNS públicos de Google:
> ```yaml
> network:
>   mode: vmnet
> dns:
>   - 8.8.8.8
>   - 8.8.4.4
> ```
> *Guarda con `Ctrl + O`, presiona `Enter` y sal con `Ctrl + X`. macOS te solicitará tu contraseña de administrador para mapear el puente virtual.*

### 2. Crear el Clúster de Kubernetes Ligero (Kind)
Configura el clúster usando el motor de contenedores optimizado de Colima:

```bash
# Crear clúster aislado de Kubernetes
kind create cluster --name chatbot-cluster

# Verificar que las credenciales apunten de forma correcta y el nodo responda
kubectl get nodes
```

### 3. Cargar la Imagen de tu Backend Local (Versión v16)
Antes de aplicar las configuraciones, inyecta la imagen construida en tu Mac dentro del almacén interno de nodos de Kind para evitar bloqueos de red externos (`ImagePullBackOff`):

```bash
kind load docker-image chatbot-backend:v16 --name chatbot-cluster
```

### 4. Desplegar la Infraestructura Completa con Kustomize
Muévete a la ubicación de tus manifiestos orquestados y aplica la inyección limpia de componentes:

```bash
# Cambiar de directorio hacia el contexto de Kustomize
cd k8s/base

# Aplicar manifiestos estructurales de forma síncrona
kubectl apply -k .
```

### 5. Control y Verificación de Estado
Monitorea que no existan Pods repetidos y que las bases de datos transicionen correctamente a estado saludable:

```bash
# Consultar los Pods corriendo dentro de tu Namespace Corporativo dedicado
kubectl get pods -n nexus-mesh

# Consultar todos los endpoints de red y servicios activos
kubectl get svc -n nexus-mesh
```

Una vez que todos los componentes marquen `Running` y sus réplicas estén balanceadas en `1/1`, abre tu navegador en tu sistema operativo Mac e ingresa a la interfaz mediante el puerto expuesto del clúster:

👉 **`http://localhost:30080`**

