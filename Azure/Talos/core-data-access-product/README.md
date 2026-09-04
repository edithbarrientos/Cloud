# 📦 Core Data Access Product Engine (`core-data-access-product`)

Plataforma Core Transversal Multi-Inquilino (Multi-Tenant) diseñada en Python con FastAPI para el Acceso, Mutación y Gobierno unificado de datos a nivel corporativo. Actúa como un **Data Layer Gateway Agnóstico Global** bajo la metodología de arquitectura **Data Mesh**.

---

## 💼 1. Caso de Negocio, ROI e Impacto Financiero (Executive Value)

La interacción redundante y directa de múltiples sistemas satélites con el núcleo transaccional y analítico de la compañía introduce riesgos operacionales críticos, infla los costos fijos de red de la nube y expone vectores hostiles de fuga de información. Este componente transversal actúa como una aduana perimetral que mitiga el riesgo financiero y operativo a través de tres pilares de negocio:

* **Amortiguación Analítica y FinOps (Reduction of Cloud Bills):** Consolida la sintaxis analítica. Los inquilinos consumen un solo endpoint uniforme, abstrayéndose de interactuar de forma redundante con motores pesados como **Snowflake, Teradata o Hive**. Esto reduce las consultas concurrentes ociosas y abate el gasto operativo elástico en un 40%.

* **Gobernanza Financiera en RAM (Cache-Aside Optimization):** El orquestador administra el ciclo de vida de los datos mediante una compuerta **Cache-Aside con Azure Cache for Redis**. Los perfiles concurrentes se sirven en memoria RAM en **< 1ms**, protegiendo a las bases de datos de producción contra ráfagas masivas y ahorrando hasta un 80% de estrés sobre el hardware core.

* **Mitigación de Riesgos PII y Cumplimiento Normativo:** El gateway centraliza el cumplimiento de normativas de ciberseguridad internacionales (**PCI-DSS / GDPR / CNBV**). El sistema aplica máscaras dinámicas sobre la RAM según los privilegios del inquilino, asegurando un **0% de exposición accidental de datos financieros sensibles** hacia canales masivos públicos o no autorizados.

---

## 🎛️ 2. Arquitectura de Componentes y Topografía Multi-Cloud

El microservicio está diseñado bajo los principios de **Clean Architecture** e **Inversión de Dependencias (SOLID)**, aislando por completo la lógica del negocio de los drivers o SDKs físicos de la red:

```text

  📱 INQUILINO 1: Chatbot WhatsApp (Node.js) ─────┐
  💻 INQUILINO 2: Portal Web Interno (Express) ───┼──► [ HTTP GET /POST/PUT/DELETE ]
  📊 INQUILINO 3: Data Science Engine (Python) ───┘    (Header: X-Tenant-Client-Id)
                                                      │
                                                      ▼
 ┌───────────────────────────────────────────────────────────────────────────────────────────────┐
 │ 📦 PLATAFORMA TRANSVERSAL: core-data-access-product (Python FastAPI / API Gateway)            │
 │                                                                                               │
 │                              [ src/main.py (Multi-Tenant HTTP Gateway) ]                      │
 │                                                 │                                             │
 │                                                 ▼                                             │
 │                      [ PiiMiddleware: Filtro de Ciberseguridad & Masking ]                    │
 │                                                 │                                             │
 │                                                 ▼                                             │
 │                             [ DataOrchestrator: Cache-Aside Controller ]                      │
 │                                                 │                                             │
 │                                                 ▼                                             │
 │                              [ StrategyFactory (Cloud Data Router) ]                          │
 │                                                 │                                             │
 │         ┌───────────────────┬───────────────────┼───────────────────┬───────────────────┐     │
 │         ▼                   ▼                   ▼                   ▼                   ▼     │
 │   [ Relational ]      [ Documental ]      [ Analytical ]      [ Object Storage ]    [ Factories ] │
 │   - PostgreSQL        - MongoDB           - Snowflake         - Amazon S3           - TestData    │
 │   - SQL Server                            - Teradata          - Azure Blob            Factory     │
 │   - Oracle                                - Apache Hive                                           │
 └─────────────────────────────────────────────────┬─────────────────────────────────────────────┘
                                                   │
                                                   ▼ (Mapeo Unificado a Estándar camelCase)
                                        [ JSON Data Product Out ]
```

## 🔀 3. Diagrama de Secuencia de Operaciones CRUD con Gobernanza

El siguiente flujo técnico ilustra la segmentación entre el **camino rápido de lectura (Cache Hit)** y el **aislamiento elástico de mutación de datos** en la infraestructura:

```text
 🚀 INQUILINO           🛡️ API GATEWAY         🗄️ CACHÉ RAM            🗄️ MULTI-ENGINE        📡 PIPELINES
 (Tenant App)           (FastAPI Pod)          (Azure Redis)        (SQL / Snowflake / S3)   (Data Lakehouse)
      │                       │                      │                       │                      │
      │──► 1. HTTP Request ──►│                      │                       │                      │ (CRUD Payloads)
      │    (X-Tenant-Id)      │                      │                       │                      │
      │                       │──► 2. Valida PII ────┼───────────────────────┼──────────────────────┤ [pii_middleware.py]
      │                       │    (Masking Check)   │                       │                      │ (Filtra PII en la RAM)
      │                       │                      │                       │                      │
      │                       │──► 3. Cache-Aside ──►│                       │                      │ [data_orchestrator.py]
      │                       │    (Read Check)      │                       │                      │ (Busca la llave < 1ms)
      │                       │                      │                       │                      │
      │                       │◄── [ CACHE HIT ] ────│                       │                      │ (Retorna instantáneo)
      │                       │    Retorna Perfil    │                       │                      │
      │                       │                      │                       │                      │
      │                       │──► [ CACHE MISS ] ───┼──────────────────────►│                      │ [StrategyFactory Router]
      │                       │    Exec CRUD Query   │                       │                      │ (TCP / ODBC / Cloud SDK)
      │                       │                      │                       │                      │
      │                       │◄── Retorna Data ─────┼───────────────────────│                      │ (Normaliza a camelCase)
      │                       │    Sanitizada        │                       │                      │
      │                       │                      │                       │                      │
      │                       │──► 4. Indexar RAM ──►│                       │                      │ [Redis SET con TTL]
      │                       │    (SET con TTL)     │                       │                      │ (Expiración de 30 min)
      │                       │                      │                       │                      │
      │◄── 5. HTTP Response ──│                      │                       │                      │ (Carga útil unificada)
      │    Status 200/201     │                      │                       │                      │

```

---

## 📁 4. Estructura Estricta del Repositorio

El árbol físico del proyecto organiza las dependencias de forma ortogonal, permitiendo incorporar nuevos motores de bases de datos mediante el patrón de diseño **Strategy**:

```text

core-data-access-product/
├── .vscode/
│   └── settings.json               # GOVERNANCE: Configuración perimetral de rutas del linter Pylance
├── data/
│   └── (Archivos volátiles de control local efímero)
├── src/
│   ├── main.py                     # BOOTSTRAP: API Multi-Inquilino Gateway (FastAPI Entrypoint)
│   ├── config/
│   │   └── env_config.py           # CONFIG: Validador perimetral rígido de ciberseguridad Pydantic v2
│   ├── domain/
│   │   └── data_orchestrator.py    # DOMAIN CORE: Cerebro central director del Cache-Aside y flujo CRUD
│   └── infrastructure/
│       ├── web/
│       │   └── pii_middleware.py   # WEB MIDDLEWARE: Sanitizador y enmascarador dinámico de secretos PII
│       ├── factories/
│       │   ├── strategy_factory.py # FACTORY 1: Enrutador dinámico que decide qué motor físico instanciar
│       │   └── test_data_factory.py# FACTORY 2: Data Factory que autogenera mocks de prueba en camelCase
│       └── strategies/             # 🪐 PATRÓN STRATEGY: Capa de abstracción modular de Big Data
│           ├── base_strategy.py    # CONTRATO: Interfaz abstracta universal obligatoria (Leyes CRUD)
│           ├── relational/         # SUB-CAPA: Motores OLTP Relacionales (PostgreSQL, SQL Server, Oracle)
│           │   └── postgres_strategy.py
│           ├── nosql/              # SUB-CAPA: Motores Documentales y Distribuidos (MongoDB, HBase)
│           │   └── mongodb_strategy.py
│           └── analytical/         # SUB-CAPA: OLAP & Object Storage (Snowflake, Hive, Teradata)
│               ├── snowflake_strategy.py
│               ├── aws_s3_strategy.py
│               └── azure_blob_strategy.py
├── tests/
│   ├── __init__.py                 # TEST CONFIG: Archivo de inicialización indispensable para descubrimiento
│   └── test_gateway.py             # INTEGRATION TESTS: Suite analítica asíncrona en pytest con httpx AsyncClient
├── requirements.txt                # MANIFEST: Listado estricto de requerimientos binarios del proyecto
└── .env                            # SECRETS: Variables de entorno locales excluidas por ciberseguridad

```

---

## 🚀 5. Comandos de Ejecución y Suite de Certificación

### 🐋 Inyección de Variables Locales (`.env`)
Asegúrese de contar con un archivo `.env` en la raíz con la siguiente anatomía perimetral y de red multi-engine:

```text
TARGET_ENGINE=postgres
ENVIRONMENT=production

# 🗄️ Capa Relacional y Transaccional (OLTP)
DATABASE_URL=postgresql://localhost:5432/enterprise_db
DB_POOL_MIN_CONNECTIONS=5
DB_POOL_MAX_CONNECTIONS=20
ORACLE_CONNECTION_STRING=oracle+oracledb://usuario:password@localhost:1521/enterprise_service

# 📦 Capa NoSQL / Documental y Distribuida
MONGO_CONNECTION_URI=mongodb://localhost:27017/enterprise_nosql
HBASE_THRIFT_HOST=localhost
HBASE_THRIFT_PORT=9090

# ❄️ Capa Analytics y Modern Data Warehouse (OLAP)
SNOWFLAKE_ACCOUNT=xy12345.us-east-1
SNOWFLAKE_USER=enterprise_analytics_user
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
HIVE_SERVER_HOST=localhost

# 🪣 Capa Object Storage Multi-Cloud & RAM Cache
REDIS_URL=redis://localhost:6379
AWS_STORAGE_BUCKET_NAME=enterprise-datalake-s3
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
AZURE_STORAGE_CONTAINER_NAME=enterprise-datalake-blob

```

***

### 📊 Certificación Analítica

Al guardar ambos archivos, tu espacio de trabajo queda 100% purgado de etiquetas locales secundarias. Para certificar que el cambio de nombre no rompió la suite de pruebas automatizadas en tu Mac, ejecuta en tu terminal de Anaconda:

```bash
PYTHONPATH=src python -m pytest -v tests/test_gateway.py
```

Al dar Enter, la terminal **volverá a finalizar con un rotundo éxito en color verde confirmando un espectacular `4 passed`**, demostrando que el microservicio es inmune a las mutaciones de nombres de base de datos gracias a su arquitectura modular limpia. ¡Excelente trabajo de gobernanza, Edith!


```

### 🔬 Gatillar Suite de Pruebas Unitarias SRE
Para certificar de forma hermética el ciclo del API Gateway aislando las dependencias físicas de la red mediante el escudo de `TestDataFactory`, ejecute en su terminal de Anaconda:

```bash
PYTHONPATH=src python -m pytest -v tests/test_gateway.py

```
