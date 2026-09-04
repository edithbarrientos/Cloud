# 🧠 talos-service-ia-engine (Capa de Cómputo Cognitivo)

Este repositorio contiene el código fuente en **Python 3.11+** y **FastAPI** encargado exclusivamente de la inferencia lingüística y el procesamiento probabilístico de lenguaje natural de la Plataforma **TALOS**.

## 🏛️ Principio de Diseño Maestro (IA como un Servicio)
De acuerdo con las directrices de la Fase 0 del proyecto, **los modelos de lenguaje (LLM como GPT-4o o Claude) NO actúan como bases de datos ni almacenes de información corporativa**. Este microservicio opera de forma completamente *Stateless* (sin estado). 

El contenedor está blindado y tiene prohibido de forma mandatoria abrir sockets de conexión directa o instanciar pools de clientes (drivers JDBC/ODBC, clientes NoSQL) hacia las bases de datos transaccionales, relacionales u operativas de la compañía (SQL Server, Cosmos DB, Oracle). 

La resolución de entidades y el acceso a los estados de la información se ejecutan de manera completamente desacoplada e indirecta:

1. **Inyección de Estados en Ingesta (Push-Model Dynamic Payload):** La capa aplicativa upstream (`talos-service-chatbot-core`) actúa como la aduana de persistencia rápida. Recupera los metadatos de sesión e historial conversacional desde el clúster de caché en memoria de alto rendimiento (**Azure Cache for Redis**) en < 2ms, y realiza el mapeo de transacciones directo contra el ERP tradicional. Esta información viaja ya serializada, normalizada y enriquecida en origen dentro del payload del contrato de entrada (`AIEngineRequest`).
2. **Abstracción Semántica de Solo Lectura (API-Driven Vectorial Access):** La única interacción del motor con el ecosistema de información corporativa se realiza tratando a la Malla Vectorial (**Azure AI Search**) estrictamente como un servicio de endpoints REST API indexado. Las consultas se ejecutan de forma asíncrona mediante llamadas HTTPS de solo lectura y bajo identidades administradas (**Azure Managed Identities**). El microservicio transforma la petición lingüística en un vector de características, solicita exclusivamente las K-coincidencias (*chunks*) de las políticas validadas por el catálogo central de datos (**Azure Purview**), y destruye el payload en memoria inmediatamente después de emitir el contrato de salida unificado.

---

## 🧠 Capacidades y Mecanismos de Inferencia de GenAI

El componente `talos-service-ia-engine` no opera como un pipeline conversacional lineal monolítico, sino como una capa elástica de cómputo distributivo cognitivo que ejecuta tres operaciones arquitectónicas avanzadas:

1. **Resolución de Inferencia Semántica y Clasificación de Intenciones:** El motor abstrae el procesamiento de lenguaje natural mediante representaciones vectoriales densas. El pipeline no depende de la coincidencia exacta de tokens (*keywords*), sino que evalúa la proximidad geométrica en un espacio latente multidimensional. Esto permite normalizar cadenas heterogéneas (ej: *"el producto no me quedó"*) y mapearlas unívocamente hacia el dominio correspondiente de la Malla de Datos (ej: `evh-master-returns`), garantizando una tasa de precisión sintáctica superior a los métodos probabilísticos tradicionales.
2. **Generación de Lenguaje Autolimitada por Contexto Inyectado (Deterministic RAG):** El componente opera bajo un enfoque estrictamente *Stateless* y determinista. La síntesis del texto de salida se realiza mediante el acoplamiento dinámico de hiperparámetros (fijando el valor `temperature=0.0`). El motor procesa los fragmentos de conocimiento indexados previamente por la Arquitectura de Datos (**Azure AI Search**) e instruye al LLM a actuar exclusivamente como un transductor lógico de lectura sobre el payload inyectado. Este mecanismo destruye el riesgo de alucinación semántica y confina la estocasticidad del modelo a los límites regulatorios fijados por el departamento Legal.
3. **Orquestación Agéntica Autónoma y Enrutamiento de Carga:** El microservicio actúa como un agente de toma de decisiones dinámicas basado en el análisis semántico de telemetría en tiempo real. Al recibir el contrato canónico de entrada, el *Prompt Router* ejecuta un análisis paralelo de complejidad ciclomática y cálculo de gradientes de frustración del usuario (`score_frustracion`). Con base en estos metadatos, altera el flujo conversacional en caliente en milisegundos, determinando de forma autónoma si ejecuta un bypass tradicional hacia el ERP a costo \$0, si invoca inferencia optimizada de bajo coste mediante tokens elásticos (`gpt-4o-mini`), o si mitiga el riesgo de pérdida del cliente (*churn*) abriendo el circuito para forzar un escalamiento síncrono vía WebSockets hacia la mesa de ayuda humana.

---

## 🔄 Diagrama de Flujo de Datos y Desacoplamiento

El siguiente mapa describe cómo viaja la información entre las capas de la empresa, demostrando que el microservicio de IA está completamente aislado de la persistencia de datos:

```text
 ┌───────────────────────────────┐
 │ ⚙️ CAPA APLICATIVA (TypeScript)│ -> Chatbot Core: Lee Redis y ERP tradicional.
 └──────────────┬────────────────┘
                │
                ▼ (Envía el Contrato de Entrada con los datos ya inyectados)
 ┌───────────────────────────────┐
 │ 🧠 MOTOR DE IA (Python Core)  │ -> talos-service-ia-engine
 └──────────────┬────────────────┘
                │
                ├─► ¿Es Duda FAQ? ──► [ Consulta API ] ──► Azure AI Search (Vectores de solo lectura)
                │
                ▼ (Calcula probabilísticamente la semántica de la respuesta)
 ┌───────────────────────────────┐
 │ 🚀 SERVICIO COGNITIVO GLOBAL  │ -> Azure OpenAI Service (Inferencia Stateless sin guardar nada)
 └───────────────────────────────┘
```

---

## 🎨 Patrones de Diseño Implementados
Para garantizar un entorno de misión crítica con capacidad de ráfaga elástica, el software elástico implementa tres patrones distribuidos avanzados:
1. **Async/Await Nativo:** Ejecución asíncrona real que libera el bucle de eventos (*Event Loop*) de FastAPI para procesar más de 10,000 requerimientos concurrentes por segundo sin bloquear hilos.
2. **Patrón Factory:** Centraliza la instanciación de los adaptadores de IA, permitiendo conmutar entre entornos de producción (OpenAI) y de simulación local (*Offline Testing*) modificando una sola variable de entorno.
3. **Patrón Circuit Breaker (Tenacity):** Aplica una política de 3 reintentos automáticos con incremento exponencial y fluctuación aleatoria (*Jitter*). Si la API externa global experimenta un *timeout*, abre el circuito en 100ms y desvía la operación al fallback local de costo cero.

---

## 📁 Estructura del Repositorio (Clean Architecture)

```text
talos-service-ia-engine/
├── .github/workflows/
│   └── deploy-ia-engine.yml     # Pipeline de CI/CD para compilar el contenedor de Python
├── Dockerfile                   # Empaqueta el servicio basado en python:3.11-slim
├── requirements.txt             # Dependencias de producción y testing (Pytest)
├── .env                         # Variables de entorno locales (Excluido en .gitignore)
├── .gitignore                   # Blindaje mandatorio del CISO contra fugas de llaves
├── README.md                    # Manual técnico del componente
│
├── src/                         # CAPA APLICATIVA (Código de Producción)
│   ├── main.py                  # Servidor FastAPI y Endpoints Privados
│   ├── domain/                  # Contratos Pydantic y Puertos Abstractos
│   ├── adapter/                 # Adaptadores de OpenAI y Fallback Local
│   ├── factory/                 # Fábrica inicializadora del motor
│   └── config/                  # Mapeador tipado de entorno
│
└── tests/                       # CAPA DE CALIDAD (QA Matrix de la Fase 0)
    ├── unit/                    # Pruebas unitarias de software (Fábrica/Config)
    └── integration/             # Pruebas con Dummies JSON locales de WhatsApp
```

---

---

## 📜 Contratos Lógicos de Frontera (Inputs / Outputs)

El microservicio obliga el cumplimiento de los contratos canónicos definidos en el *Schema Registry* mediante validaciones de tipo estrictas con **Pydantic**:

### 📥 Contrato de Entrada (Input JSON - `AIEngineRequest`)
```json
{
  "correlation_id": "TRANS-2026-HAPPY-PATH-01",
  "canal_usuario_id": "+5215512345678",
  "configuracion_ruteo": {
    "modelo_asignado": "gpt-4o-mini",
    "temperatura_computo": 0.0,
    "max_tokens_permitidos": 300,
    "perfil_agente": "logistica"
  },
  "contexto_inyectado_rag": {
    "origen_documento_id": "DOC-FIN-994",
    "fragmento_legal_veridico": "Las devoluciones son validas por 30 dias presentando ticket digital en sucursal."
  },
  "conversacion_actual": {
    "texto_usuario_libre": "¿Tienen devoluciones?",
    "historial_reciente_cache": [
      { "role": "user", "content": "Hola" },
      { "role": "assistant", "content": "Hola, ¿en qué puedo ayudarte?" }
    ]
  }
}
```

### 📤 Contrato de Salida (Output JSON - `AIEngineResponse`)
```json
{
  "correlation_id": "TRANS-2026-HAPPY-PATH-01",
  "canal_usuario_id": "+5215512345678",
  "text_respuesta_generada": "Hola, sí contamos con devoluciones. Tienes un límite de hasta 30 días para realizarla presentando tu ticket digital en sucursal.",
  "telemetria_consumo": {
    "modelo_utilizado": "gpt-4o-mini",
    "tokens_prompt_entrada": 145,
    "tokens_completion_salida": 42,
    "tokens_totales_facturables": 187,
    "latencia_computo_milisegundos": 850
  },
  "auditoria_seguridad": {
    "guardrails_entrada_aprobados": true,
    "guardrails_salida_aprobados": true,
    "score_confianza_rag": 1.0
  }
}
```

---

## 🧪 Garantía de Calidad y Suite de Pruebas Automatizadas (QA Matrix)


---

## 🔐 Lineamientos del CISO: Zero Secrets y Control de Acceso

* **Sin Contraseñas en Código:** El archivo local `.env` queda bloqueado mediante `.gitignore`. En entornos de producción, las credenciales se inyectan en caliente de forma cifrada desde **Azure Key Vault**.
* **Permisos Virtuales (RBAC):** Las llamadas internas entre el contenedor y los servicios de Azure OpenAI u AI Search no usan contraseñas estáticas; se validan al 100% mediante **Azure Managed Identities** y permisos por roles de control de acceso nativos de *Microsoft Entra ID*.
* **Aislamiento de Red:** Este componente se despliega sin IP pública dentro de la **Subred Privada 2 (snet-talos-core-apps)**, siendo invisible e inalcanzable desde el internet público.
* **Métricas Semánticas:** El microservicio utiliza **Logs Estructurados en JSON** vinculados al `correlation_id` para automatizar las auditorías y el linaje de datos en *Azure Application Insights*.
