

# 🦫 AI-Deequ-Engine: Orquestador Distribuido de Eventos en Streaming

Motor de procesamiento de datos de misión crítica basado en Apache Flink y Scala. Este componente actúa como el orquestador principal del flujo elástico (Dataflow Layer), encargado de succionar datos binarios desde Apache Pulsar, aplicar mecanismos de tolerancia a fallos y despachar las cargas de texto de forma no bloqueante hacia el cerebro de Inteligencia Artificial remoto.

---

## 🏛️ 1. Arquitectura de la Solución y Niveles del Sistema

```text
========================================================================================
 CAPA 1: INFRAESTRUCTURA PERIMETRAL (Event Ingestion Layer)
========================================================================================
  [ Clientes Chat / UI ] ──(HTTP/JSON)──► [ API Gateway ] ──► [ Apache Pulsar Broker ]
                                                                      │
                                                            (Bytes crudos en cola)
                                                                      ▼
========================================================================================
 CAPA 2: ORQUESTACIÓN Y PROCESAMIENTO STREAMING (Distributed Dataflow Layer)
========================================================================================
  [ Módulo: flink-runtime ]
   ├── StreamApp.scala       🪐 (Succiona bytes de Pulsar de forma continua)
   ├── AnomalyEvent.scala    🪐 (Mapea el tipado intermedio del Dataflow)
   └── AsyncAIEvaluator.scala🪐 (Dispara hilos asíncronos no bloqueantes por Red)
                                                                      │
                                                        (Contrato Binario: Protobuf)
                                                                      ▼
========================================================================================
 CAPA 3: ADAPTADORES DE TRANSPORTE RED (Inference Delivery Layer)
========================================================================================
  [ Módulo: nlp-ml-brain ] ──► Capa de Entrada (FastAPI / Uvicorn ASGI Server)
   ├── src/main.py           🔌 (Punto de entrada de red del contenedor Docker)
   ├── src/api/endpoints.py  🔌 (Receptor de Alta Velocidad: Deserializa bytes a objetos)
   └── src/api/middlewares.py🛡️ (Auditoría, telemetría y métricas de inferencia)
                                                                      │
                                                            (Modelos de Dominio Puros)
                                                                      ▼
========================================================================================
 CAPA 4: DOMINIO CENTRAL DE IA (Domain Core Layer)
========================================================================================
   └── src/domain/models.py  🧬 (Entidades tipadas e Interfaces agnósticas de la IA)
                                                                      │
                                                            (Casos de Uso de Machine Learning)
                                                                      ▼
========================================================================================
 CAPA 5: CASOS DE USO Y ALGORITMOS DE MACHINE LEARNING (ML Business Logic Layer)
========================================================================================
   ├── src/services/tenant_router.py 🔀 [PATRÓN: MODEL ROUTER] (Enrutador Multicliente)
   │                                    Carga en caliente modelos aislados desde /models_store
   │                                                                  │
   └── src/services/analyzer.py      🧪 [PATRÓN: PREDICTIVE FALLBACK] (Pipeline NLP Streaming)
                                        ├── Intent Detection 🤖 (TextCNN / Regresión Multinomial)
                                        ├── Sentiment Score  🤖 (Regresión Lineal / VADER)
                                        └── NER Extractor    🤖 (Campos Aleatorios Condicionales - CRF)
========================================================================================


```

1. Aislamiento de Carga (Capas 1 y 2): Flink mantiene el stream volando a nivel de microsegundos en la Capa 2 [local]. Al despachar la petición de forma asíncrona, delega la carga computacional pesada hacia las capas inferiores de la Inteligencia Artificial [local].

2. Desacoplamiento Tecnológico (Capa 3): FastAPI intercepta el búfer binario en la Capa 3 [local]. Si el día de mañana decides migrar el backend de Python a Rust o C++ por rendimiento, Flink nunca se entera porque el contrato de la capa de transporte (Protobuf) permanece idéntico.

3. Independencia Multi-Tenant (Capa 5): Los datos cruzan de la Capa 3 a la 4 y estallan de forma dinámica en la Capa 5. El algoritmo tenant_router.py rompe la rigidez tradicional mapeando en caliente el modelo exacto del cliente final [local], asegurando que las capas de negocio de la IA estén completamente aisladas por inquilino.

---


## 🧠 2. Patrones de Diseño de Ingeniería y Algoritmos Aplicados

### Patrones de Diseño de Software e IA Implementados

*   **⚡ Inferencia Asíncrona (Asynchronous Inference Pattern):** Mediante el operador `AsyncDataStream.unorderedWait`, el motor despacha las peticiones HTTP/Protobuf hacia el backend de IA y, sin quedarse esperando la respuesta de red, continúa consumiendo los siguientes miles de eventos de Pulsar.
*   **🛡️ Resguardo Predictivo (Predictive Fallback Pattern):** El mapeador intermedio envuelve la succión en un bloque seguro `catch`. Si llega a pasar un mensaje corrupto que no cumple con el esquema JSON o Protobuf, el sistema no se detiene; captura la anomalía y autogenera metadatos dinámicos por UUID para salvar la ejecución.
*   **🧳 Serialización por Contrato Estricto (Canonical Data Model Pattern):** Sustituye el uso de strings planos por Google Protobuf. Las variables se empaquetan binariamente byte por byte en un buffer rígido respetando la especificación Varint, optimizando el consumo del ancho de banda del clúster en un 400%.

### Algoritmos y Mecanismos de Control de Flink

*   **Control de Backpressure (Tolerancia a Inundaciones):** Algoritmo nativo de Flink basado en créditos de búfer de red (*Credit-based Flow Control*). Si el microservicio de NLP se ralentiza, Flink frena automáticamente la succión en Pulsar para proteger la memoria RAM.
*   **Tolerancia a Fallos (Exactly-Once):** Algoritmo distribuido de instantáneas asíncronas (*Chandy-Lamport Algorithm*). Flink guarda el estado y el offset de Pulsar cada 10 segundos, asegurando que si un Pod se cae, el sistema reanude exactamente donde se quedó sin duplicar mensajes.

---

## 📊 3. Diagrama de Secuencia del Pipeline (Event Flow)

El siguiente diagrama detalla la interacción cronológica y el comportamiento no bloqueante de los hilos distribuidos entre Apache Pulsar, Apache Flink y el Cerebro de NLP:

```text
[Gateway API]          [Apache Pulsar]        [StreamApp (Flink)]     [AsyncAIEvaluator]     [nlp-ml-brain]
      │                       │                        │                       │                    │
      │ 1. POST Ingest JSON   │                        │                       │                    │
      ├──────────────────────►│                        │                       │                    │
      │ 2. HTTP 200 OK (Ack)  │                        │                       │                    │
      ◄───────────────────────┤                        │                       │                    │
      │                       │                        │                       │                    │
      │                       │ 3. Consume bytes       │                       │                    │
      │                       ◄────────────────────────┤                       │                    │
      │                       │    (Array[Byte])       │                       │                    │
      │                       │                        │                       │                    │
      │                       │                        │ 4. map() / Jackson    │                       │
      │                       │                        ├─────────────────┐     │                    │
      │                       │                        │ Parseo / UUID   │     │                    │
      │                       │                        ◄─────────────────┘     │                    │
      │                       │                        │                       │                    │
      │                       │                        │ 5. asyncInvoke()      │                    │
      │                       │                        ├──────────────────────►│                    │
      │                       │                        │  (AnomalyEvent DTO)   │                    │
      │                       │                        │                       │                    │
      │                       │                        │                       │ 6. writeVarint()   │
      │                       │                        │                       ├──────────────┐     │
      │                       │                        │                       │ Serializa a  │     │
      │                       │                        │                       │ Protobuf JJS │     │
      │                       │                        │                       ◄──────────────┘     │
      │                       │                        │                       │                    │
      │                       │                        │                       │ 7. POST (Protobuf) │
      │                       │                        │                       ├───────────────────►│
      │                       │                        │                       │                    │
      │                       │                        │                       │                    │ 8. Inferencia
      │                       │                        │                       │                    │    Multi-Tenant
      │                       │                        │                       │                    ├───────────┐
      │                       │                        │                       │                    │ spaCy CNN │
      │                       │                        │                       │                    │ NER / CRF │
      │                       │                        │                       ◄──────────────┘
      │                       │                        │                       │                    │
      │                       │                        │                       │ 9. HTTP 200 (JSON) │
      │                       │                        │                       ◄────────────────────┤
      │                       │                        │                       │                    │
      │                       │                        │ 10. complete(result)  │                    │
      │                       │                        ◄───────────────────────┤                    │
      │                       │                        │                       │                    │
      │                       │                        │ 11. resultStream.print()                   │
      │                       │                        ├─────────────────┐     │                    │
      │                       │                        │ Sink Analítico  │     │                    │
      │                       │                        ◄─────────────────┘     │                    │
      │                       │                        │                       │                    │
      ▼                       ▼                        ▼                       ▼                    ▼


```


### 🔍 Descripción del Flujo del Diagrama

*   **Paso 1 y 2 (Desacoplamiento Perimetral):** El cliente recibe su respuesta inmediata del Gateway en cuanto el mensaje toca la cola de Pulsar. Esto garantiza que el usuario experimente cero latencia, sin importar qué tan saturada esté la IA [local].
*   **Paso 3 y 4 (Succión Segura):** Flink extrae los bytes crudos y ejecuta el mapeador. Si el JSON viene mal, el bloque `catch` inyecta un UUID dinámico para salvar el hilo [local].
*   **Paso 5 al 7 (Inferencia Asíncrona):** El `AsyncAIEvaluator` corre en un hilo independiente. Transforma el DTO a la especificación binaria compacta con Varints (`writeVarint`) y dispara el socket TCP hacia Python [local].
*   **Paso 8 al 10 (Procesamiento Aislado):** El contenedor de Python procesa de forma no bloqueante, ejecuta spaCy y retorna el veredicto estructurado. Al recibir el código `200`, el hilo de Flink despierta, completa la promesa (`resultFuture.complete`) y entrega el resultado enriquecido al Sink final [local].



---

## 📦 4. Estructura Completa del Proyecto y Descripción de Componentes

```text
ai-nlp-engine/                        --> 🚀 Raíz Única del Repositorio Completo (Monorepo)
├── ⚙️ .github/workflows/             --> Automatización de CI/CD para Flink y Python
├── ☸️ k8s/                            --> Manifiestos de despliegue para todo el clúster
│   ├── 📜 flink-jobmanager.yaml      --> Orquestación del JobManager de Flink
│   ├── 📜 flink-taskmanager.yaml     --> Orquestación del TaskManager de Flink
│   ├── 📜 nlp-brain-deployment.yaml  --> Orquestación del Pod de Python (Replicas, CPU, RAM)
│   └── 📜 nlp-brain-service.yaml     --> DNS elástico interno para comunicar Flink con Python
├── 📜 proto/                         --> Contrato binario único y centralizado
│   └── 📄 chat_anomaly.proto         --> Archivo fuente Protobuf que leen ambos módulos
│
├── 🦫 flink-runtime/                  --> 🪐 MÓDULO 1: AGENTE DE STREAMING (Scala / SBT)
│   ├── 📂 src/main/resources/
│   │   └── 📄 application.conf       --> Propiedades de Pulsar y variables Typesafe
│   └── 📂 src/main/scala/com/orchestra/ado/stream/
│       ├── 📄 AnomalyEvent.scala     --> Caso de clase para tipado intermedio
│       ├── 📄 AsyncAIEvaluator.scala --> Operador asíncrono que golpea al módulo de Python
│       └── 📄 StreamApp.scala        --> Entrada principal del pipeline de Flink
│
└── 🐍 nlp-ml-brain/                  --> 🧠 MÓDULO 2: CEREBRO DE IA (Python / FastAPI / spaCy)
    ├── 📄 .dockerignore              --> Exclusión de archivos basura para el build de IA
    ├── 🐳 Dockerfile                 --> Construcción Multi-Stage optimizada para Python
    ├── 📋 requirements.txt           --> Dependencias estrictas de Machine Learning
    ├── 📂 models_store/              --> Repositorio local de pesos de modelos por Cliente
    ├── 📂 src/                       --> Código fuente de Python bajo Clean Architecture
    │   ├── 📄 main.py                --> Inicializador del servidor web asíncrono ASGI (Uvicorn)
    │   ├── 🔧 config/settings.py     --> Parámetros globales y de entorno mediante Pydantic v2
    │   ├── 🌐 api/endpoints.py       --> Receptor FastAPI (Deserializa los bytes de Flink)
    │   ├── 🧬 domain/models.py       --> Contratos internos y tipado estricto de datos de la IA
    │   └── 🧠 services/
    │       ├── 🧪 analyzer.py        --> Pipeline de NLP (Intent Detection, Sentiment, NER)
    │       └── 🔀 tenant_router.py   --> Router Multicliente (Carga dinámica desde models_store/)
    └── 📂 tests/                     --> Validaciones de calidad de software e IA (F1-Score)
```

---


## 📜 4. Contratos de Datos (Data Contracts)


### 📥 Contrato de Entrada (Hacia Flink / Python via Protobuf)
Definido en `proto/chat_anomaly.proto`:
```protobuf
syntax = "proto3";

package com.orchestra.ado.models;

message ChatAnomaly {
  string tenant_id = 1;
  string session_id = 2;
  string message_payload = 3;
}
```

### 📤 Contrato de Resultado (Salida Enriquecida JSON de la API de IA)
```json
{
  "status": "SUCCESS",
  "tenantId": "orchestra-tenant-1",
  "sessionId": "sess-dinamica-1",
  "analytics": {
    "intent": "SUPPORT_REQUEST",
    "intent_confidence": 0.94,
    "sentiment_score": -0.75,
    "entities": [
      {"entity_type": "ACCOUNT_NUMBER", "value": "1234-5678-90"}
    ]
  }
}
```

---

## ☸️ 5. Despliegue e Instalación en Kubernetes (k8s)

El aprovisionamiento del motor de streaming se gestiona mediante manifiestos YAML independientes para garantizar el aislamiento de recursos y la asignación exacta de memoria.

### Perfiles de Configuración de Recursos por Objeto

*   **flink-jobmanager.yaml (Deployment y Service):**
    *   Puerto Expuesto: 6123 (RPC de control), 8081 (Consola de Administración Web).
    *   Límites de Recursos: CPU: 1.0 núcleos, RAM: 1024 MiB.
    *   Propósito: Coordinador maestro distribuido encargado de recibir el JAR y asignar tareas operativas a los TaskManagers.
*   **flink-taskmanager.yaml (Deployment):**
    *   Puerto Expuesto: Sockets dinámicos de comunicación interna del clúster.
    *   Límites de Recursos: CPU: 2.0 núcleos, RAM: 2048 MiB.
    *   Propósito: Contenedor físico de ejecución masiva donde se alojan los hilos paralelos del AsyncAIEvaluator y el cliente de Pulsar.

### Secuencia Estricta de Instalación y Arranque

Ejecuta esta ráfaga de comandos en orden secuencial desde la terminal de tu Mac para compilar y levantar el pipeline de procesamiento en vivo:

1. **Crear el Namespace elástico para el aislamiento del proyecto:**
   ```bash
   kubectl create namespace ai-deequ
   ```
2. **Generar el empaquetado Fat JAR autocontenido de Flink usando SBT:**
   ```bash
   sbt "flinkRuntime/clean; flinkRuntime/assembly"
   ```
3. **Desplegar la infraestructura del orquestador en el clúster de Kubernetes:**
   ```bash
   kubectl apply -f k8s/flink-jobmanager.yaml
   kubectl apply -f k8s/flink-taskmanager.yaml
   ```
4. **Transferir el binario compilado al almacenamiento temporal del JobManager activo:**
   ```bash
   kubectl cp flink-runtime/target/artifacts/flink-stream-agent.jar deployment/ai-deequ-flink-jobmanager:/tmp/flink-stream-agent.jar -n ai-deequ
   ```
5. **Lanzar la ejecución de la topología sobre las ranuras físicas de procesamiento:**
   ```bash
   kubectl exec -it deployment/ai-deequ-flink-jobmanager -n ai-deequ -- flink run -c com.orchestra.ado.stream.StreamApp /tmp/flink-stream-agent.jar
   ```

### Verificación Funcional y Telemetría del Pipeline

Utiliza estos comandos de inspección en vivo para auditar el flujo de streaming e interceptar las marcas dinámicas del logger en tiempo real:

*   **Verificación del estado de las ranuras (Slots) de Flink:**
    ```bash
    kubectl get pods -n ai-deequ -o wide | grep jobmanager
    ```
    *Criterio de éxito: El Pod debe reportar estado 'Running' y estar en capacidad '1/1 Ready' indicando disponibilidad de memoria.*

*   **Auditoría de los logs dinámicos de succión en los TaskManagers:**
    ```bash
    kubectl logs deployment/ai-deequ-flink-taskmanager -n ai-deequ --tail=50 -f
    ```
    *Criterio de éxito: Muestra en pantalla las marcas '==>' y '-->' creadas con SLF4J, reflejando el procesamiento de los tenants de forma elástica y sin caídas.*


*   **Inyección perimetral de tráfico de prueba con pasaporte de red:**
    ```bash
    kubectl exec -it deployment/ai-deequ-flink-jobmanager -n ai-deequ -- sh -c 'for i in 1 2 3; do curl -s -X POST http://ai-deequ-gateway-api-service:50051/v1/ingest -H "Content-Type: application/json" -H "X-Tenant-ID: orchestra-tenant-\$i" -d "{\"tenantId\":\"orchestra-tenant-\$i\",\"sessionId\":\"sess-dinamica-\$i\",\"payload\":\"Mensaje de auditoria numero \$i OK\"}"; done'
    ```
    *Criterio de éxito: El perímetro de red autoriza las transacciones y las pantallas de logs de Flink se mueven solas mostrando las identidades dinámicas de negocio procesadas.*
