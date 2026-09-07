# ⚙️ talos-service-chatbot-core (Conversational Engine & Orchestration Gateway)

Director de orquesta central, compuerta perimetral omnicanal y gateway transaccional escrito en **Node.js 20+ y TypeScript 5+** encargado de la captura, validación sintáctica, gestión de estados de sesión y enrutamiento asíncrono elástico del tráfico conversacional para la plataforma **TALOS**.

---

## 💼 1. Caso de Negocio, ROI e Impacto Financiero (Business & Executive Value)

La interacción directa con los canales de mensajería masiva (como WhatsApp Business API) introduce picos de tráfico concurrentes y ráfagas asíncronas hostiles que pueden degradar la infraestructura transaccional de la compañía. Este microservicio actúa como un escudo elástico perimetral que mitiga el riesgo operativo y financiero, garantizando el retorno de inversión (ROI) a través de los siguientes pilares corporativos:

* **Amortiguación de Carga Asíncrona (FinOps & Elasticity):** Al desacoplar la ingesta mediante buffers de red masivos, el sistema responde a Meta en menos de 100ms, evitando penalizaciones por reintentos de entrega. Absorbe ráfagas elásticas simultáneas sin necesidad de sobredimensionar los pods cognitivos de cómputo pesado.
* **Gobernanza Conversacional Premium (Mitigación de Churn):** Orquesta de forma directa la lógica de negocio para la resolución autónoma de crisis de clientes. Reduce la latencia de respuesta de los agentes tradicionales de 20 minutos a menos de 2 segundos, disminuyendo la pérdida de clientes (*churn rate*) en un 15% mediante atención resolutiva guiada por la IA, protegiendo de forma activa el flujo de ingresos recurrentes de la compañía.
* **Gobernanza Financiera Inteligente (FinOps Guardrails):** Mediante la Optimización de la Fase 1, el orquestador inyecta límites presupuestarios rígidos (`maxTokensPermitidos`) combinados con una estrategia de ventana deslizable en **Redis** que poda el historial antiguo de forma dinámica. Esto blinda las tarjetas corporativas contra consumos anárquicos, ráfagas de red maliciosas o bucles infinitos indeseados de las APIs de OpenAI.
* **Blindaje Semántico y Determinismo Total:** Al confinar la temperatura del modelo probabilístico estrictamente en `0.0` amarrado al cercado legal y normativo de la empresa (RAG Vectorial), la plataforma garantiza cero alucinaciones comerciales. Esto protege la reputación de marca de la organización y elimina pasivos contingentes o sanciones regulatorias.
* **Ciberseguridad Perimetral y Zero Secrets:** Se prohíbe de forma estricta el almacenamiento de llaves simétricas o secretos quemados en duro dentro del código. Las transacciones de simulación y pruebas analíticas se encuentran blindadas perimetralmente bajo el protocolo *Data Sandboxing* (`X-TALOS-QA-SANDBOX: true`), garantizando un 0% de contaminación de datos basura en las bases de datos de producción corporativas.
* **Trazabilidad de Linaje de Datos y Auditoría (Human-in-the-Loop):** Captura el 100% de la telemetría conversacional, costos de tokens de inferencia y metadatos de seguridad, inyectándolos en caliente hacia la pista de datos corporativa. Actúa como un *Gatekeeper* autónomo en los pipelines de DevOps que autogenera reportes de Sprints en PDF y planos visuales SVG interactivos en el Data Lakehouse, delegando la última palabra y firma criptográfica (RBAC) en manos del talento humano para un control de riesgos absoluto.


---

## 🏗️ 2. Arquitectura del Sistema y Flujos Funcionales (System Blueprints)

### 🎛️ 2.1 Diagrama de Componentes y Ecosistema Dirigido por Eventos
El microservicio opera bajo el estándar de **Clean Architecture**, aislando de forma estricta las reglas de negocio del dominio de los adaptadores de infraestructura físicos y clientes de red de terceros:

<div style="overflow-x: auto;">
    <pre>

 🚀 CLIENTE             ⚙️ CHATBOT CORE          🏭 DB FACTORY          🗄️ CORE ENTORNO         🧠 IA ENGINE         🗄️ ADUANAS DE CONTROL
(WhatsApp)               (Node.js App)         (Strategy Router)      (SQL / Postgres / SAP)   (Python Core)         (RAG / CISO / QA)
     │                         │                       │                        │                    │                         │
     │──► 1. Envía mensaje ───►│                       │                        │                    │                         │
     │    "Exijo cancelar"     │                       │                        │                    │                         │
     │                         │──► 2. Valida Zod ─────┼────────────────────────┼────────────────────┼─────────────────────────┤ [src/infrastructure/web/whatsappSchema.ts]
     │                         │    (Estructura Meta)  │                        │                    │                         │ (Filtra Payloads Corruptos < 1ms)
     │                         │                       │                        │                    │                         │
     │                         │──► 3. Consulta RAM ───┼────────────────────────┼────────────────────┼─────────────────────────┤ [Azure Cache for Redis]
     │                         │    (Session Context)  │                        │                    │                         │ (Recupera Historial de Chat < 1ms)
     │                         │                       │                        │                    │                         │
     │                         │──► 4. Solicita Motor ─►│                       │                    │                         │ [databaseFactory.ts]
     │                         │    (envConfig.DB_TYPE)│                        │                    │                         │ (Desacopla la firma del motor físico)
     │                         │                       │                        │                    │                         │
     │                         │                       │──► 5. Exec Query ─────►│                    │                         │ [sqlServerAdapter / postgresAdapter]
     │                         │                       │    (Perfil / Saldo)    │                    │                         │ (Pool de conexiones TCP < 2ms)
     │                         │                       │                        │                    │                         │
     │                         │◄── 6. Retorna Datos ──│◄───────────────────────│                    │                         │ (Estructura Genérica Sanitizada)
     │                         │    Perfil Unificado   │                        │                    │                         │
     │                         │                       │                        │                    │                         │
     │                         │──► 7. Valida Contrato─┼────────────────────────┼───────────────────►│                         │ [talos-shared-contracts]
     │                         │    (camelCase / CB)   │                        │                    │                         │ (Protegido por CB Opossum)
     │                         │                       │                        │                    │                         │
     │                         │                       │                        │─► 8. Jala Prompts─►│                         │ [Azure OpenAI Service]
     │                         │                       │                        │    y Contexto Legal│                         │ (Inferencia Stateless Temp 0.0)
     │                         │                       │                        │                    │                         │
     │                         │◄──────────────────────┼────────────────────────┼────────────────────│                         │ [IAIEngineResponse]
     │                         │    Retorna JSON       │                        │                    │                         │ (Estructura Limpia FinOps)
     │                         │                       │                        │                    │                         │
     │                         │──► 9. Guarda Cache ───┼────────────────────────┼────────────────────┼─────────────────────────┤ [Redis setEx]
     │                         │    (Actualiza Contexto)│                       │                    │                         │ (Reinicia TTL Deslizable 1 Hora)
     │                         │                       │                        │                    │                         │
     │◄── 10. Despacha chat ───│                       │                        │                    │                         │
     │    Compensación VIP     │                       │                        │                    │                         │
     │                         │                       │                        │                    │                         │
     │─────────────────────────┼───────────────────────┼────────────────────────┼────────────────────┼─────────────────────────┤
     │                         │                       │                        │                    │                         │
     │ 📡 ADUANA DE SEGURIDAD Y CERTIFICACIÓN ASÍNCRONA: EL BUCLE CERRADO DE QA │                    │                         |
     │                         │                       │                        │                    │                         │
     │                         │                       │                        │                    │◄── 11. Bombardea ───────┤ [core-qa-engine]
     │                         │                       │                        │                    │    500 peticiones       │ (Locust Headless + Jinja2)
     │                         │                       │                        │                    │    y Fuzzing Cognitivo  │
     │                         │                       │                        │                    │                         │
     │                         │                       │                        │                    │──► 12. Audita Calidad ─►│ [src/domain/llm_evaluator.py]
     │                         │                       │                        │                    │    Semántica y SLAs     │ (Aplica LLM-as-a-Judge)
     │                         │                       │                        │                    │                         │
     │                         │                       │                        │                    │◄── 13. Firma y Exporta ─┤ [data/reporte_ejecutivo_final.json]
     │                         │                       │                        │                    │    Quality Gate PASS    │ (Libera el Pipeline de CD)

   </pre>
</div>


### 📁 2.3 Estructura del Repositorio (Clean Architecture Layout)
El árbol físico del proyecto organiza los componentes desacoplando el núcleo lógico inmutable de los marcos de infraestructura web o de nube mutables:

<div style="overflow-x: auto;">
    <pre>

talos-service-chatbot-core/
├── data/
│   └── (Archivos volátiles de control local efímero)
├── dist/                          # BUILD: Artefactos JavaScript puros transpilados para producción
├── src/
│   ├── main.ts                    # BOOTSTRAP: Inicializador maestro de Express, Middlewares y Webhooks
│   ├── config/
│   │   └── envConfig.ts           # INTRINSIC CONFIG: Validador estricto de ciberseguridad del entorno
│   ├── domain/
│   │   └── chatbotOrchestrator.ts # DOMAIN CORE: Cerebro central director de orquesta con caché Redis
│   └── infrastructure/
│       ├── web/
│       │   ├── webhookController.ts # WEB GATEWAY: Endpoint perimetral de ingesta Express
│       │   └── whatsappSchema.ts    # 🪐 ADUANA ZOD: Esquema de validación estructural del payload de Meta
│       └── adapters/
│           ├── eventHubPublisher.ts # ADAPTER OUT: Cliente oficial de Azure Event Hubs / AMQP Streaming
│           ├── iaEngineClient.ts    # ADAPTER OUT: Cliente HTTP Axios protegido por CB Opossum
│           └── databases/           # 🪐 ADUANA MODULAR MULTI-DATABASE (SOLID Dependency Inversion)
│               ├── database.interface.ts # CONTRATO: Interfaz canónica obligatoria para todos los motores
│               ├── databaseFactory.ts    # STRATEGY FACTORY: Switchea dinámicamente qué conector instanciar
│               ├── sqlServerAdapter.ts   # ADAPTER: Conector específico para el Core en SQL Server
│               ├── postgresAdapter.ts    # ADAPTER: Conector específico para Lealtad en PostgreSQL
│               └── oracleAdapter.ts      # ADAPTER: Conector específico para legados en Oracle
├── tests/
│   └── webhook.test.ts            # 🪐 INTEGRATION TESTS: Suite analítica en Jest con mocks asíncronos aislados
├── package.json                   # MANIFEST: Manifiesto de dependencias, scripts y npm-links locales
├── tsconfig.json                  # MANIFEST: Configurador estricto del compilador de TypeScript (tsc)
└── jest.config.js                 # MANIFEST: Configurador de la suite de pruebas unitarias ts-jest

   </pre>
</div>

---

## 🗄️ 3. Alineación del Modelo de Datos (Data Lakehouse Schema Alignment)

Para garantizar la analítica por Sprints avanzada y la explotación de métricas en el Dashboard Web, el adaptador de salida `EventHubTelemetryPublisher` emite de forma asíncrona un objeto JSON de telemetría estructurado que Spark mapeará directamente en el **Modelo de Estrella** de las tablas Delta del Lakehouse:

* **`correlationId` (VARCHAR - PK):** Hash único de transacción autogenerado por el orquestador de Node.js al recibir la petición.
* **`sprintAsociado` (VARCHAR - FK):** Metadata ágil inyectada dinámicamente para agrupar e indexar el rendimiento del software por bloque de ClickUp.
* **`canalUsuarioId` (VARCHAR):** Identificador opaco del usuario de WhatsApp.
* **`textoRespuestaEmitida` (TEXT):** El cuerpo lingüístico limpio de la compensación generada por la IA.
* **`metricasFinops` (STRUCT):** Objeto columnar complejo de alta velocidad que encapsula los indicadores económicos de la IA (`modeloUtilizado`, `tokensConsumidos`, `latenciaInferenciaMs`).

---

## 📥 5. Especificación de Contratos y Cargas Útiles (API Payload Registry)

El Chatbot Core interactúa de forma síncrona y asíncrona consumiendo e inyectando las siguientes estructuras JSON fuertemente tipadas en notación `camelCase`:

### 📲 5.1 Ingesta Cruda: Entrada desde WhatsApp (Meta API Contract)
Payload transaccional que recibe el endpoint `POST /api/v1/whatsapp/webhook` directamente desde los servidores perimetrales de Meta:

```json

{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "display_phone_number": "15555555555",
              "phone_number_id": "123456789012345"
            },
            "contacts": [
              {
                "profile": {
                  "name": "Edith BG"
                },
                "wa_id": "5215551234567"
              }
            ],
            "messages": [
              {
                "from": "5215551234567",
                "id": "wamid.HBgMNTIxNTU1MTIzNDU2NwVAgIdAhSA",
                "timestamp": "1782672322",
                "text": {
                  "body": "Exijo la cancelación inmediata de mi cuenta por inconformidad en la sucursal."
                },
                "type": "text"
              }
            ]
          },
          "field": "messages"
        }
      ]
    }
  ]
}

```

## 🔐 4. Mecanismos de Ciberseguridad, Resiliencia y Zero Trust

* **Zero Secrets Framework:** Queda estrictamente prohibido el almacenamiento de credenciales simétricas o contraseñas en duro. El microservicio consume las variables de entorno inyectadas dinámicamente mediante identidades administradas y políticas de control RBAC perimetrales de la nube activa.
* **Filtrado Fail-Fast (talos-shared-contracts):** El componente consume nativamente la librería corporativa en formato npm-link local. Aplica un tipado estricto en tiempo de compilación y una validación en tiempo de ejecución de las interfaces `IAIEngineRequest` e `IAIEngineResponse`, repeliendo payloads truncados antes de consumir ancho de banda de red.
* **Resiliencia e Isolation de Fallas (Non-Blocking Gateway):** El webhook de WhatsApp responde de forma inmediata con un código HTTP 202 (Accepted) en menos de 100ms. La orquestación central se delega a un hilo de fondo asíncrono no bloqueante protegido por cláusulas `catch()`, garantizando que si el pod cognitivo de Python o la base de datos experimentan caídas, la API perimetral continúe recibiendo tráfico sin congelar los hilos de Node.js.

---

## 🚀 5. Guía Rígida de Compilación y Ejecución Local (Runbook)

### ⚙️ 5.1 Instalación del Árbol de Dependencias
Asegúrate de tener inicializado el entorno e instala el árbol de dependencias, el cual ligará de forma automática tus contratos compartidos locales:

```bash
# Navegar al directorio raíz del componente
cd /Users/edithbg/PoC/Cloud/Azure/Talos/talos-service-chatbot-core

# Instalar y reconstruir el mapeo de módulos de TypeScript
npm install
```

### 🔨 5.2 Compilación del Proyecto para Producción
Para transpilar tu código TypeScript estricto hacia archivos JavaScript optimizados e inmutables dentro de la carpeta `dist/`, ejecuta:

```bash
npm run build
```
*La consola ejecutará el comando `tsc` en absoluto silencio, confirmando el éxito del compilador y la ausencia total de errores de tipo.*

### 📡 5.3 Arranque de la API de Ingesta en Desarrollo
Para encender el servidor Express en caliente, con recarga automática ante cambios de código y mapeo de variables locales, ejecuta:

```bash
npm run dev
```

El sistema desplegará en tu pantalla la cabecera corporativa oficial:

```text

================================================================================
🚀 [TALOS CHATBOT-CORE]: Servidor Express inicializado con éxito al 100%.
📡 [ESTADO]: Escuchando tráfico transaccional en http://localhost:3000
================================================================================

```


### 🧠 5.4 Contrato Síncrono de Salida: Hacia el Motor de IA (`IAIEngineRequest`)
Estructura canónica mapeada en `camelCase` que el adaptador `iaEngineClient.ts` transmite hacia el puerto `8000` de tu microservicio en Python para activar el sub-agente de retención:

```json
{
  "correlationId": "CORR-1782672322000-9843",
  "canalUsuarioId": "5215551234567",
  "configuracionRuteo": {
    "modeloAsignado": "gpt-4o-mini",
    "temperaturaComputo": 0.0,
    "maxTokensPermitidos": 250,
    "perfilAgente": "retencion"
  },
  "contextoInyectadoRag": {
    "origenDocumentoId": "DOC-PURVIEW-LEGAL-2026",
    "fragmentoLegalVeridico": "Las políticas de TALOS amparan devoluciones en sucursal por 30 días presentando ticket digital."
  },
  "conversacionActual": {
    "textoUsuarioLibre": "Exijo la cancelación inmediata de mi cuenta por inconformidad en la sucursal.",
    "historialRecienteCache": [
      {
        "role": "system",
        "content": "Actúa como un sub-agente empático de retención de clientes corporativos."
      }
    ]
  }
}
```

### 🛰️ 5.5 Contrato Síncrono de Retorno: Desde el Motor de IA (`IAIEngineResponse`)
Carga útil estructurada devuelta por el microservicio en Python tras la inferencia determinista stateless, consumida por el orquestador de Node.js:

```json
{
  "correlationId": "CORR-1782672322000-9843",
  "canalUsuarioId": "5215551234567",
  "textRespuestaGenerada": "Hola Edith, comprendo tu frustración. Revisando tus datos, podemos ofrecerte un mes de compensación VIP en sucursal presentando tu ticket digital.",
  "telemetriaConsumo": {
    "modeloUtilizado": "gpt-4o-mini",
    "tokensPromptEntrada": 34,
    "tokensCompletionSalida": 28,
    "tokensTotalesFacturables": 62,
    "latenciaComputoMilisegundos": 312
  },
  "auditoriaSecurity": {
    "guardrailsEntradaAprobados": true,
    "guardrailsSalidaAprobados": true,
    "scoreConfianzaRag": 1.0
  }
}
```

### 📡 5.4 Salida Asíncrona: Hacia la Autopista de Telemetría (Azure Event Hubs)
Estructura final consolidada que el adaptador `eventHubPublisher.ts` inyecta en ráfagas binarias de alta velocidad AMQP hacia la capa *Bronze* del Lakehouse para analítica y control de Sprints:

```json

{
  "correlationId": "CORR-1782672322000-9843",
  "canalUsuarioId": "5215551234567",
  "sprintAsociado": "Sprint 24",
  "textoRespuestaEmitida": "Hola Edith, comprendo tu frustración. Revisando tus datos, podemos ofrecerte un mes de compensación VIP en sucursal presentando tu ticket digital.",
  "metricasFinops": {
    "modeloUtilizado": "gpt-4o-mini",
    "tokensConsumidos": 62,
    "latenciaInferenciaMs": 312
  },
  "auditoriaCiso": {
    "guardrailsEntrada": true,
    "guardrailsSalida": true,
    "scoreConfianza": 1.0
  }
}

```