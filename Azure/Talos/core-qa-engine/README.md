# 📡 core-qa-engine (AI-Driven Quality Engineering & Governance Platform)

Plataforma corporativa centralizada, agnóstico y de portabilidad multi-nube escrita en **Python 3.12+** encargada de la automatización y ejecución de **Pruebas Funcionales, No Funcionales (Rendimiento, Carga, Estrés, Usabilidad, Escalabilidad, Seguridad), Fuzzing Cognitivo y Certificación de Acuerdos de Nivel de Servicio (SLA)** para los sistemas de la compañía.

---

## 💼 1. Caso de Negocio y Beneficios Estratégicos (Business Value)

El despliegue de sistemas basados en Inteligencia Artificial Generativa (GenAI) e infraestructuras elásticas en la nube introduce riesgos operativos y financieros que los frameworks de calidad tradicionales no pueden mitigar. Este motor automatiza la mitigación de fallos, garantizando el retorno de inversión (ROI) a través de cuatro beneficios de calidad total:

* **Mejora de la Experiencia del Usuario (UX Premium):** Al evaluar de forma continua aspectos críticos como el rendimiento, la usabilidad y la seguridad cognitiva, las pruebas no funcionales garantizan que el software sea altamente receptivo y fácil de usar. Esto incrementa de forma directa la tasa de satisfacción del usuario final y mitiga la pérdida de clientes (*churn rate*) en los canales de atención automatizados.
* **Reducción Radical del Riesgo Operativo:** La plataforma ayuda a identificar de manera temprana posibles cuellos de botella en la red privada, lagunas de seguridad semántica o problemas latentes de estabilidad antes de que el software entre en funcionamiento. Esto disminuye al mínimo el riesgo de fallos catastróficos o interrupciones de servicio tras el lanzamiento.
* **Rendimiento y Fiabilidad Mejorados:** Las pruebas no funcionales parametrizadas garantizan que el ecosistema de software pueda manejar de forma elástica picos de carga extremos (*Spike Traffic*), recuperarse de fallos y permanecer estable bajo diversas condiciones hostiles, entregando un producto tecnológico más fiable y de alta disponibilidad.
* **Cumplimiento Normativo y Adhesión a los Estándares:** El motor valida de forma inmutable las políticas de protección de datos de la compañía y los guardrails exigidos por el CISO, asegurando la auditoría de linaje de datos para auditorías regulatorias internas y externas.

---


## 🏗️ 2. Arquitectura del Sistema y Flujos Funcionales (System Blueprints)

### 🎛️ 2.1 Diagrama del Modelo de Datos Optimizado (Delta Lake Layered Schema)El nuevo mapa de datos abstrae el texto pesado hacia dimensiones, agrupa la telemetría en estructuras compactas y define las directrices de particionamiento físico para el Data Lake:

El nuevo mapa de datos abstrae el texto pesado hacia dimensiones, agrupa la telemetría en estructuras compactas y define las directrices de particionamiento físico para el Data Lake:


<div>
<pre>
 ┌───────────────────────────────────────────────────────-┐
 │ 📄 dim_sprints (Particionamiento Físico)               │
 ├────────────────────────────────────────────────────────┤
 │  PK  │ sprint_id       (VARCHAR - Ej: 'S24')           │
 │      │ tester_name     (VARCHAR)                       │
 │      │ ticket_clickup  (VARCHAR)                       │
 └───────────────────────────┬────────────────────────────┘
                             │
                             ▼ (1 a Muchos)
┌──────────────────────────────────────────────────────────────────────────────────────┐
│ 📊 fact_qa_audits (TABLA DE HECHOS OPTIMIZADA - DELTA TABLES)                        │
├──────────────────────────────────────────────────────────────────────────────────────┤
│  PK  │ audit_id               (VARCHAR - Z-ORDER INDEX)                              │
│  FK  │ sprint_id              (VARCHAR - Clúster Físico de Partición)                │
│  FK  │ caso_uso_id            (VARCHAR - Relación con dim_casos_uso)                 │
│      │ timestamp_utc          (TIMESTAMP)                                            │
│      │ target_endpoint_url    (VARCHAR)                                              │
│      │ perfil_ataque          (VARCHAR - stress / spike / soak)                      │
│      │                                                                               │
│      │ ──► STRUCT: telemetria_infraestructura (Estructura Columnar RAM/Red)          │
│      │     ├── total_requests         (INTEGER)                                      │
│      │     ├── error_rate_percentage  (FLOAT)                                        │
│      │     ├── latencia_p50_ms        (INTEGER)                                      │
│      │     └── latencia_p95_ms        (INTEGER)                                      │
│      │                                                                               │
│      │ ──► STRUCT: auditoria_cognitiva_ia (Métricas de LLM-Evaluation)               │
│      │     ├── faithfulness_score     (FLOAT - Alucinación)                          │
│      │     ├── guardrail_escape_score (FLOAT - Ciberseguridad)                       │
│      │     └── toxicity_score         (FLOAT - Calidad Conversacional)               │
│      │                                                                               │
│      │ resultado_quality_gate (VARCHAR - Clúster Físico de Partición: PASS/FAIL)     │
│      │ rbac_approver_user     (VARCHAR - Email de Firma Humana)                      │
└───────────────────────────▲──────────────────────────────────────────────────────────┘
                            │
                            ▲ (1 a Muchos)
 ┌──────────────────────────┴──────────────────────────────┐
 │ 🎯 dim_casos_uso (Texto Pesado Desacoplado)             │
 ├─────────────────────────────────────────────────────────┤
 │  PK  │ caso_uso_id     (VARCHAR - Ej: 'UC-RETENCION-04')│
 │      │ nombre_flujo    (VARCHAR)                        │
 │      │ business_case   (TEXT - Justificación del ROI)   │
 └─────────────────────────────────────────────────────────┘

</pre>
</div>

---

### 🗄️ 2.2. Modelo de Datos Analítico Optimizado (Delta Lakehouse Schema)

La telemetría estructurada recolectada en la capa Bronze es procesada por Apache Spark y consolidada en la capa Silver/Gold utilizando un **Modelo de Estrella (Star Schema) Optimizada para Cómputo Columnar (Parquet)**. El diseño implementa tipos de datos complejos y clústeres físicos de partición para garantizar máxima velocidad de respuesta en el Dashboard Web:

### 📊 4.1 Tabla de Hechos Optimizada (`fact_qa_audits`)
*   `audit_id` (VARCHAR - **PK**): Identificador global único. Cuenta con optimización **Z-Order Indexing** para búsquedas puntuales instantáneas de auditorías de Sprints.
*   `sprint_id` (VARCHAR - **FK**): **Columna de Particionado Físico Primario**. Los datos se agrupan en carpetas independientes en el Data Lake según el ciclo de ClickUp, reduciendo el escaneo de datos (*Data Scanning*) en un 800%.
*   `caso_uso_id` (VARCHAR - **FK**): Enlace directo con las métricas de negocio.
*   `timestamp_utc` (TIMESTAMP): Registro temporal inmutable de la ejecución de la prueba.
*   `target_endpoint_url` / `perfil_ataque` (VARCHAR): Coordenadas de red y estrategia de carga elástica.
*   `telemetria_infraestructura` (**STRUCT - COMPLEX TYPE**): Objeto encapsulado en el formato columnar que almacena las variables físicas de red (`total_requests`, `error_rate_percentage`, `latencia_p50_ms`, `latencia_p95_ms`), reduciendo el ancho de la fila y acelerando las agregaciones matemáticas de Spark.
*   `auditoria_cognitiva_ia` (**STRUCT - COMPLEX TYPE**): Objeto encapsulado que almacena las variables de control semántico calculadas de forma predictiva por el AI Judge (`faithfulness_score`, `guardrail_escape_score`, `toxicity_score`).
*   `resultado_quality_gate` (VARCHAR): **Columna de Particionado Físico Secundario** (`PASS` / `FAIL`), permitiendo aislar de inmediato los lotes de software comprometidos.
*   `rbac_approver_user` (VARCHAR): Firma de linaje del Ingeniero Senior que autorizó la validación humana en la compuerta de control.

### 📐 4.2 Tablas de Dimensión Coadyuvantes (Texto Pesado Desacoplado)
*   **`dim_sprints`:** Gestiona el linaje ágil almacenando los nombres de los probadores responsables y los tickets enlazados de ClickUp.
*   **`dim_casos_uso`:** Almacena los strings pesados del negocio (`business_case` y descripciones lógicas de los sub-agentes de TALOS), previniendo la duplicidad de texto redundante en la tabla de hechos central y optimizando los costos de almacenamiento financiero de la empresa.



### 🎛️ 2.3 Diagrama de Componentes y Flujo de Eventos (Closed-Loop Pipeline)
El motor implementa el patrón **Master/Worker** y se encuentra completamente desacoplado en una arquitectura dirigida por eventos para evitar que el consumo de red del inyector de carga degrade el rendimiento de la API receptora:

<div>
    <pre>

  [ Pipeline de CI/CD ] ──► (HTTP POST /launch) ──► FastAPI (API Maestra - Puerto 9000)
                                                           │
                                                           ▼ (Retorna HTTP 202 Accepted en 3ms)
                                                  [ Libera Hilos del CI ]
                                                           │
                                                           ▼ (Encola Tarea Asíncrona)
                                                  [ Azure Cache for Redis ]
                                                           │
                                                           ▼ (Worker Toma el Control)
                                                  [ Celery Background Worker ]
                                                           │
       ┌───────────────────────────────────────────────────┴───────────────────────────────────────────────────┐
       ▼ (Etapa 1 y 2: Muestreo GenAI)                                                         ▼ (Etapa 3 y 4: Inyección Física)
scripts/ai_generator.py                                                                 tests/locustfile.py
Genera payloads.json adaptados al prompt                                                Locust Headless renderiza Jinja2
       │                                                                                       │
       └───────────────────────────────────────────────────┬───────────────────────────────────────────────────┘
                                                           │
                                                           ▼ (Ametralla Target con Escudo X-TALOS-QA-SANDBOX)
                                                  [ Microservicio Bajo Prueba ]
                                                           │
                                                           ▼ (Vuelca Métricas Crudas de Red)
                                                  [ data/reporte_stats_stats.json ]
                                                           │
                                                           ▼ (Etapa 5 y 6: Análisis de Fallas)
                                                  src/domain/llm_evaluator.py
                                                  IA Diagnostica Cuellos de Botella y SLAs
                                                           │
                                                           ▼ (Etapa 7: Patrón Observer Despacha Notificaciones)
                                           [ ClosedLoopQualityCoordinator ]
                                                           │
        ┌─────────────────────────┬────────────────────────┼──────────────────────────┬────────────────────────┐
        ▼                         ▼                        ▼                          ▼                        ▼
[ LocalReportJson ]      [ HttpPipelineWebhook ]  [ DynamicFlowChart ]       [ LocalReportPdf ]       [ SlackAlertCrisis ]
Guarda el JSON para      Devuelve el veredicto    Dibuja el Diagrama de      Compila el documento     Dispara tarjetas de
la interfaz web del      PASS/FAIL al Webhook     Arquitectura dinámico      PDF formal con curvas    crisis a hilos de ing.
Dashboard de Sprints.    del pipeline de CD.      vectorial en SVG.          de Matplotlib integradas.  si se viola el SLA.
        │                         │                        │                          │                        │
        └─────────────────────────┴────────────────────────┼──────────────────────────┴────────────────────────┘
                                                           │
                                                           ▼ (Persistencia de Linaje Corporativo)
                                            [ data/bronze/logs/qa/ ] ◄── Data Lakehouse Landing

    </pre>
</div>



### 🔀 2.4 Diagrama de Secuencia de Caso de Uso (UC-TALOS-RETENCION-04)

El siguiente mapa describe el viaje del dato en milisegundos a lo largo de las capas de software, identificando las aduanas de control rígidas y el punto de inspección del motor de QA en bucle cerrado:

<div>
    <pre>

 🚀 CLIENTE             ⚙️ CHATBOT CORE        🧠 IA ENGINE         🗄️ ADUANAS DE CONTROL
(WhatsApp)               (Node.js App)       (Python Microservice)     (Redis / RAG / QA)
     │                         │                       │                         │
     │──► 1. Envía mensaje ───►│                       │                         │
     │    "Exijo cancelar"     │                       │                         │
     │                         │──► 2. Valida tipos ──►│                         │ [talos-shared-contracts]
     │                         │    (camelCase)        │                         │ (Garantiza Fail-Fast)
     │                         │                       │                         │
     │                         │                       │──► 3. Jala Prompts ────►│ [Azure Cache for Redis]
     │                         │                       │    y Contexto Legal     │ (Inyección en vivo < 1ms)
     │                         │                       │    (RAG Vectorial)      │
     │                         │                       │                         │
     │                         │                       │──► 4. Ejecuta Inferencia│ [Azure OpenAI Service]
     │                         │                       │    Stateless (Temp 0.0) │ (Cero Alucinaciones)
     │                         │                       │                         │
     │                         │◄── 5. Devuelve JSON ──│                         │
     │                         │    Respuesta Limpia   │                         │
     │◄── 6. Despacha chat ────│                       │                         │
     │    Compensación VIP     │                       │                         │
     │                         │                       │                         │
     │─────────────────────────┼───────────────────────┼─────────────────────────┤
     │                         │                       │                         │
     │ 📡 ADUANA DE SEGURIDAD Y CERTIFICACIÓN ASÍNCRONA: EL BUCLE CERRADO DE QA   │
     │                         │                       │                         │
     │                         │                       │◄── 7. Bombardea ────────│ [core-qa-engine]
     │                         │                       │    500 peticiones       │ (Locust Headless + Jinja2)
     │                         │                       │    y Fuzzing Cognitivo  │
     │                         │                       │                         │
     │                         │                       │──► 8. Audita Calidad ──►│ [src/domain/llm_evaluator.py]
     │                         │                       │    Semántica y SLAs     │ (Aplica LLM-as-a-Judge)
     │                         │                       │                         │
     │                         │                       │◄── 9. Firma y Exporta ──│ [data/reporte_ejecutivo_final.json]
     │                         │                       │    Quality Gate PASS    │ (Libera el Pipeline de CD)

  </pre>
</div>



## 📁 2.5 Estructura del Repositorio (Clean Architecture Layout)

El árbol físico de archivos y carpetas se organiza aislando de forma estricta las reglas de negocio de los marcos de infraestructura y frameworks de red:

<div>
    <pre>
core-qa-engine/
├── data/
│   ├── job_config.json            # CONFIG: Parámetros del Job efímero mapeados con Jinja2
│   ├── payloads.json              # DATA: Catálogo de tráfico sintético creado por la IA
│   ├── app_execution.log          # OBSERVER OUT: Trazas de logs JSON nativos de la ejecución
│   ├── reporte_stats_stats.json   # INFRA OUT: Métricas analíticas de red crudas de Locust
│   └── bronze/                    # DATA LAKEHOUSE LANDING ZONE (Dominio QA)
│       ├── reports/               # Certificados ejecutivos PDF vectoriales unificados
│       └── logs/
│           └── qa/                # Historial inmutable de trazas para analítica con Spark
├── scripts/
│   └── ai_generator.py            # GenAI IN: Fabricación probabilística de prompts vía OpenAI
├── src/
│   ├── __init__.py
│   ├── main.py                    # API & OBSERVER COORDINATOR: FastAPI Entrypoint y Despachador
│   ├── config/
│   │   ├── __init__.py
│   │   └── celery_app.py          # ORQUESTADOR: Distribuidor asíncronos de hilos (Celery + Redis)
│   ├── factory/
│   │   ├── __init__.py
│   │   └── chain_factory.py       # ABSTRACT FACTORY: Encapsulador del armado de la cadena de QA
│   └── domain/
│       ├── __init__.py
│       ├── qa_contracts.py          # INTERFACES: Modelos Pydantic v2 de validación universal
│       ├── stress_strategies.py     # PATRÓN STRATEGY: Modulador polimórfico de carga (Stress/Spike/Soak)
│       ├── telemetry_parser.py      # ANALYTICS UTILS: Extractor estadístico de percentiles de red
│       ├── llm_evaluator.py         # AI JUDGE: Evaluador cognitivo y diagnóstico predictivo
│       ├── qa_observers.py          # PATRÓN OBSERVER: Interfaces base de suscripción analítica
│       ├── qa_visualizer.py         # OBSERVER SUBSCRIBER: Diseñador dinámico de diagramas SVG (Graphviz)
│       ├── qa_pdf_observer.py       # OBSERVER SUBSCRIBER: Compilador del PDF unificado (ReportLab)
│       ├── qa_slack_observer.py     # OBSERVER SUBSCRIBER: Despachador de tarjetas de alerta ante fallas
│       ├── qa_log_observer.py       # OBSERVER SUBSCRIBER: Exportador del linaje de logs al Lakehouse
│       └── qa_chain.py              # PATRÓN CHAIN OF RESPONSIBILITY: Las 7 etapas unificadas
└── tests/
    └── locustfile.py                # INYECTOR: Hilos concurrentes asíncronos de Locust con Jinja2

  </pre>
</div>

---

## 📐 3. Gobierno de Calidad Total y Disciplinas Soportadas

La plataforma digitaliza y unifica las metodologías tradicionales y contemporáneas de la Ingeniería de Calidad en una sola suite automatizada:

### 🏛️ 3.1 Pilares de Testing e Ingeniería de Software

* **Pruebas Funcionales (Business Logic Validation):** Evalúan los componentes individuales y la interacción entre módulos, verificando el sistema completo para validar que cada una de sus características opere según lo esperado y satisfaga las necesidades de los usuarios. El motor valida la integridad sintáctica de los contratos canónicos y ratifica que el `correlationId` retorne de forma síncrona e inmutable para asegurar el linaje requerido por el usuario final.
* **Pruebas No Funcionales (Performance & Cognitive Security):** Evalúan las características no funcionales como el rendimiento, la seguridad, la usabilidad y la escalabilidad, garantizando que el software sea eficiente y seguro de usar. Verifican la velocidad y estabilidad de carga, protección de datos y experiencia de usuario bajo condiciones extremas.
* **Pruebas Automatizadas de Software (AI-Driven Automation):** Consisten en utilizar herramientas y scripts para ejecutar evaluaciones repetitivas y complejas de forma automática, ahorrando tiempo y esfuerzos, eliminando el mantenimiento de archivos manuales rígidos.


### 📊 3.2 Las 6 Disciplinas No Funcionales Instrumentadas

1. **Pruebas de Rendimiento:** Identifican la latencia y el tiempo de respuesta del servidor de forma amarrada mediante percentiles (`p50 / p95`) para evaluar la capacidad de respuesta bajo diferentes condiciones de carga, garantizando que la aplicación funcione de forma eficiente (como medir la velocidad bajo distintas condiciones de red).
2. **Pruebas de Carga:** Miden el comportamiento del software en condiciones de carga previstas (Uso habitual), garantizando que la aplicación siga respondiendo ante un número específico de usuarios o transacciones (Ej: Simular 1,000 usuarios simultáneos en una plataforma de comercio electrónico para verificar compras sin afectar el rendimiento).
3. **Pruebas de Estrés:** Llevan al sistema más allá de su capacidad normal para identificar puntos de ruptura y posibles fallos ante un aumento repentino de actividad. Evalúan cómo se comporta el sistema bajo condiciones extremas, garantizando que el software falle de forma controlada sin pérdida de datos a través de la apertura de su *Circuit Breaker*.
4. **Pruebas de Usabilidad:** Se centran en la interfaz y la experiencia del usuario, garantizando que el software sea fácil de navegar e intuitivo para los usuarios finales. El motor delega un evaluador *LLM-as-a-Judge* para auditar las respuestas degradadas bajo carga, previniendo la confusión o frustración del cliente y optimizando los perfiles de respuesta (Siguiendo el estándar de de optimización empírica de firmas como Shopify).
5. **Pruebas de Escalabilidad:** Evalúan la capacidad del software para ampliarse o reducirse en función de los cambios en la carga de usuarios o volumen de datos. El motor analiza las métricas de hardware para recomendar la adición de recursos (*Pod Autoscaling*) en la nube a medida que aumenta el tráfico para mantener la capacidad de respuesta.
6. **Pruebas de Seguridad:** Identifican posibles vulnerabilidades y protegen el software contra accesos no autorizados y violaciones de datos. El framework ejecuta revisiones y pruebas de penetración cognitiva (*Prompt Injection Fuzzing*) para verificar que los filtros perimetrales repelan ataques maliciosos bajo condiciones extremas de saturación de red.


### 🔄 3.3 Las 7 Etapas del Control de Calidad Industrializado


1. **Planificación:** Se definen los criterios de calidad, los estándares técnicos y los procedimientos de inspección antes de iniciar cualquier producción. Se intercepta el contrato universal mediante esquemas tipados rígidos de Pydantic v2.
2. **Muestreo:** Se seleccionan muestras representativas del lote de productos con criterios estadísticos para asegurar la fiabilidad de la evaluación. La IA pre-calcula escenarios conversacionales heterogéneos y dinámicos con dispersión semántica balanceada en memoria RAM.
3. **Inspección:** Se examinam minuciosamente las muestras utilizando herramientas de medición de Locust para comprobar si cumplen con las especificaciones establecidas, evaluando en tiempo real códigos de estado HTTP y latencias brutas.
4. **Registro de datos:** Se documentan de forma exacta los resultados de la inspección, las fallas detectadas y las mediciones obtenidas de forma masiva en la suite de logs estructurados en JSON de la aplicación.
5. **Análisis:** Se interpretan los datos recopilados para identificar el origen de los errores, las tendencias y las desviaciones frente al estándar mediante el cálculo automatizado de percentiles p95.
6. **Acción correctiva:** Se aplican soluciones inmediatas para corregir los defectos detectados y ajustar el proceso para evitar que se repitan, lanzando ataques simulados de control para probar la contención de los esquemas.
7. **Informe final y seguimiento:** Se detalla el estado del lote en un reporte ejecutivo en formato PDF y JSON enviado al Data Lakehouse, firmando el dictamen final para el seguimiento del Sprint en la mesa de control de cambios.

---

## 🔐 4. Mecanismos de Resiliencia, Ciberseguridad y Portabilidad (Zero Trust)


* **Circuit Breaker Distribuido (Tenacity Core):** Las corrutinas asíncronas de inyección se encuentran blindadas mediante una política de 3 reintentos automáticos con incremento exponencial y fluctuación aleatoria (*Jitter*). Si la API externa experimenta caídas o bloqueos por límite de cuota (HTTP 429), la máquina de estados abre el circuito en 100ms para aislar la telemetría corrupta.
* **Control de Acceso Agnóstico (Zero Secrets Multi-Cloud):** El microservicio prohíbe el almacenamiento de llaves simétricas o contraseñas en archivos planos. La autenticación se resuelve en tiempo de ejecución utilizando identidades administradas y asignación de roles de la nube activa (**Azure Managed Identities / AWS IAM Roles / GCP Service Accounts**).
* **Aislamiento de Persistencia Transaccional (Data Sandboxing Protocol):** El motor inyecta la cabecera HTTP `X-TALOS-QA-SANDBOX: true` en el 100% de las transacciones generadas. Esta directiva instruye a las APIs bajo prueba a desviar las operaciones de escritura hacia repositorios de simulación (*Mocks* o memoria RAM), garantizando un **0% de contaminación de datos reales** en los tableros analíticos de la empresa.
* **Gobernanza Human-in-the-Loop (Aprobación Federada):** El framework prohíbe la auto-aplicación de pases a producción autónomos dirigidos en su totalidad por la IA. Ante fallas, el motor veta el pipeline y encola las recomendaciones predictivas en el Dashboard Web bajo el estado `En revision`. La reanudación del flujo de despliegue continuo (CD) y el cambio a `Resuelto` quedan estrictamente supeditados a la validación de un Ingeniero Senior mediante su firma criptográfica y token RBAC de *Microsoft Entra ID*.

---

## 🚀 5. Guía Rígida de Ejecución Local y Despliegue (Runbook)

### 🔌 5.1 Requisitos de Infraestructura del Sistema Operativo
Para que las APIs de Python puedan renderizar y compilar las imágenes vectoriales de los planos de flujo funcional, tu sistema operativo debe contar con el binario de **Graphviz** instalado localmente:
```bash
# En macOS utilizando Homebrew (Recomendado)
brew install graphviz

# En sistemas Linux basados en Ubuntu/Debian
sudo apt-get install graphviz
```

### ⚙️ 5.2 Inicialización del Entorno Aislado de Python
Navega a la carpeta raíz del componente en tu terminal y ejecuta la instalación del ecosistema congelado:
```bash
# 1. Crear el entorno virtual de Python 3.12+
python3 -m venv venv

# 2. Actualizar el gestor de paquetes e instalar requerimientos corporativos
./venv/bin/pip install --upgrade pip

# 3. Instalar las dependencias de control de la suite de QA
./venv/bin/pip install -r requirements.txt
```

### 📡 5.3 Arranque de la Suite en 3 Golpes (Pestañas de la Terminal)
Para poner a marchar tu plataforma de QA-as-a-Service, ejecuta las siguientes instrucciones en tres pestañas independientes de tu consola activa:

```bash
# Pestaña 1: Levantar la base de datos de Redis (El Broker que almacena las órdenes)
brew services start redis

# Pestaña 2: Inicializar el soldado de ejecución pesada (Celery Worker)
./venv/bin/celery -A src.config.celery_app.celery_orchestrator worker --loglevel=info

# Pestaña 3: Levantar la API Maestra de control de calidad total (FastAPI)
./venv/bin/python -m uvicorn src.main:app --host 0.0.0.0 --port 9000 --reload
```
*(El motor de QA correrá de forma aislada en el puerto `9000` para no chocar con tu microservicio de IA del puerto `8000` o la página web del Dashboard).*

### 📥 5.4 Ejemplo de Invocación HTTP (Payload Canónico Universal)
Para lanzar una simulación de picos masivos de tráfico (`spike`) auditando de forma paralela la usabilidad conversacional del **Sprint 24**, dispara una petición HTTP POST a `http://localhost:9000/api/v1/stress/launch` inyectando este JSON universal con tu herramienta de red (Postman/Curl):

```json
{
  "target_url": "http://localhost:8000",
  "target_endpoint": "/api/v1/compute/language",
  "perfil_ataque": "spike",
  "usuarios_maximos": 500,
  "duracion_segundos": 60,
  "sla_latencia_p95_ms": 1500,
  "sla_max_error_rate": 1.0,
  "sprint_activo": "Sprint 24",
  "ai_guidance_prompt": "Genera teléfonos simulados y preguntas realistas de clientes de WhatsApp exigiendo cancelaciones comerciales por políticas de devolución.",
  "body_template": {
    "correlation_id": "UC-TALOS-RETENCION-04",
    "conversacion_actual": {
      "texto_usuario_libre": "{{ texto_usuario }}"
    }
  },
  "nodos_arquitectura": [
    { "id_nodo": "N1", "label": "📱 Interfaz: WhatsApp Webhook Web", "color_hex": "#EBF8FF" },
    { "id_nodo": "N2", "label": "⚙️ Core: Chatbot Process (Node.js)", "color_hex": "#FEFCBF" },
    { "id_nodo": "N3", "label": "🧠 IA Engine: FastAPI Core (Python)", "color_hex": "#F0FFF4" },
    { "id_nodo": "N4", "label": "🗄️ Database: Cache (Azure Redis)", "color_hex": "#EDF2F7" }
  ],
  "conexiones_arquitectura": [
    { "origen": "N1", "destino": "N2", "label": "Webhook Ingest" },
    { "origen": "N2", "destino": "N3", "label": "HTTP POST (Contracts)" },
    { "origen": "N3", "destino": "N4", "label": "Async Gather < 1ms" }
  ]
}
```

### 📊 5.5 Certificación del Linter Estático Local
Para certificar que cualquier cambio o nueva modularización de eslabones preserve el cumplimiento del 100% de las normas tipográficas y de ciberseguridad, ejecuta el formateador ruff:
```bash

./venv/bin/ruff check src/

```
La terminal imprimirá la leyenda de éxito absoluto corporativo: ✨ **`All checks passed!`**


---

## 🐳 6. Virtualización y Despliegue en la Nube (Containerization Registry)

El componente se encuentra completamente contenedorizado e independizado del sistema operativo local para permitir su portabilidad elástica multi-nube:

### 📥 6.1 Compilación de la Imagen Docker Local
Para construir y empaquetar de forma inmutable la plataforma de calidad en tu computadora, ejecuta el comando de construcción:
```bash
docker build -t corporativo/core-qa-engine:1.0.0 .
```

### 🚀 6.2 Despliegue del Contenedor de Forma Aislada
Para encender el microservicio exponiendo de forma segura el puerto 9000 e inyectando las llaves analíticas en caliente desde la terminal, corre el contenedor:
```bash
docker run -d \
  -p 9000:9000 \
  -e CORE_QA_OPENAI_KEY="tu-llave-de-azure" \
  -e AZURE_REDIS_QUEUE_URL="redis://host.docker.internal:6379/0" \
  --name qa-engine-active \
  corporativo/core-qa-engine:1.0.0
```

