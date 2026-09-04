# 📦 talos-shared-contracts (Ecosistema de Tipados Canónicos)

Librería centralizada y distribuida en **Node.js** y **TypeScript** que contiene las interfaces e invariantes lógicas de los contratos canónicos de la Plataforma **TALOS**.

## 🏛️ Propósito Arquitectónico y Fail-Fast Principle
De acuerdo con las especificaciones de diseño de la Fase 0, este componente actúa como el **Registry de Esquemas Canónicos** para todas las aplicaciones y microservicios upstream escritos en la suite de TypeScript (como `talos-service-chatbot-core`).

Su objetivo es aplicar el principio de **Fail-Fast (Fallo Temprano)** en tiempo de compilación. Al obligar a los módulos emisores a tipar sus estructuras mediante esta librería, se garantiza que cualquier inconsistencia de datos (ej: ausencia del `correlationId` o error en el tipado del `perfilAgente`) sea atrapada por el compilador de TypeScript (`tsc`) en la computadora del desarrollador o en el pipeline de CI/CD, previniendo la transmisión de payloads corruptos a través de la red de Azure.

---

## 🔄 Diagrama de Integración Políglota y Bus de Eventos

El siguiente mapa describe el ciclo de vida del dato, demostrando cómo esta librería de Node.js (`camelCase`) se acopla con la autopista asíncrona de Event Hubs y el motor de inferencia en Python (`snake_case`):

```text
 🚀 CLIENTE (WhatsApp / Web Gateway)
      │
      ▼ (Entra petición HTTP Webhook)
 ┌────────────────────────────────────────────────────────┐
 │ ⚙️ talos-service-chatbot-core (Node.js App)            │
 ├────────────────────────────────────────────────────────┤
 │ • Importa: IAIEngineRequest                            │ -> Valida tipos en camelCase al vuelo
 │ • Ensambla payload inmutable con su correlationId      │ -> Garantiza consistencia de los datos
 └────────────────────────┬───────────────────────────────┘
                          │
                          ▼ (Pone el mensaje crudo en la cola de entrada de forma asíncrona)
 ┌────────────────────────────────────────────────────────┐
 │ ⚡ AZURE EVENT HUBS: evh-talos-ingress-whatsapp       │ -> Amortigua ráfagas concurrentes masivas
 └────────────────────────┬───────────────────────────────┘ -> Retención y durabilidad de datos por 7 días
                          │
                          ▼ (El Worker consume el mensaje y dispara el request HTTP)
 ┌────────────────────────────────────────────────────────┐
 │ 📡 HTTP POST PAYLOAD SERIALIZADO (JSON camelCase)      │ -> Tránsito seguro por la red interna
 └────────────────────────┬───────────────────────────────┘
                          │
                          ▼ (Aduana Perimetral de Entrada: FastAPI + Pydantic v2)
 ┌────────────────────────────────────────────────────────┐
 │ 🧠 talos-service-ia-engine (Python Microservice)       │
 ├────────────────────────────────────────────────────────┤
 │ • alias_generator=to_camel                             │ -> Traduce dinámicamente de Camel a Snake
 │ • Lee identidad desde Redis y conocimiento desde RAG   │ -> Cómputo Cognitivo Determinista
 └────────────────────────┬───────────────────────────────┘
                          │
                          ▼ (Retorna el JSON IAIEngineResponse transformado a camelCase)
 ┌────────────────────────────────────────────────────────┐
 │ ⚡ AZURE EVENT HUBS: evh-talos-analytics-telemetry     │ -> Interceptado por Azure Fabric OneLake
 └────────────────────────────────────────────────────────┘ -> Auditoría de costos y linaje para el CISO
```

---

## 🔀 Mecanismo de Mapeo Automático (Snake vs. Camel)

Para respetar los estándares nativos de cada lenguaje de programación y maximizar la comodidad del equipo de desarrollo, la Plataforma **TALOS** implementa un patrón de traducción de fronteras transparente:

* **Upstream Layer (Node.js / TypeScript):** Utiliza estrictamente la convención estándar **notaciónCamel** (`camelCase`) (ej: `correlationId`, `perfilAgente`).
* **Downstream Layer (Python / FastAPI):** Utiliza la convención nativa **snake_case** (`correlation_id`, `perfil_agente`).

La serialización y el acoplamiento semántico entre ambos entornos se resuelven en caliente en la aduana perimetral de la API de IA mediante el generador dinámico de aliases de **Pydantic v2** (`alias_generator=to_camel`), permitiendo que el bus de datos sea políglota sin requerir transformaciones manuales de strings en Node.js.

---

## 📁 Estructura Anatómica del Repositorio

```text
talos-shared-contracts/
├── dist/                           # Código JavaScript nativo y declaraciones compiladas (.js / .d.ts)
├── src/                            # CAPA DE DISEÑO (Código Fuente TypeScript)
│   ├── index.ts                    # Punto de exposición y exportación central unificada
│   ├── aiEngineRequest.interface.ts  # Interfaz canónica del payload de entrada (Input JSON)
│   └── aiEngineResponse.interface.ts # Interfaz canónica del payload de retorno (Output JSON)
├── package.json                    # Manifiesto de dependencias bloqueadas y scripts NPM
├── tsconfig.json                   # Directrices estrictas del compilador de TypeScript
└── README.md                       # Manual técnico del componente
```

---

## 📜 Especificación de Interfaces e Invariantes

### 📥 Contrato de Entrada (`IAIEngineRequest`)
Define la estructura obligatoria que el orquestador de mensajería debe ensamblar antes de invocar el motor de inferencia lingüística:

```typescript
export interface IRagContext {
  origenDocumentoId: string;        // UUID o Hash del manual indexado en Azure Purview
  fragmentoLegalVeridico: string;    // Chunk inmutable extraído de Azure AI Search
}

export interface IChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface IChatContext {
  textoUsuarioLibre: string;
  historialRecienteCache: IChatMessage[]; // Memoria histórica extraída de Redis
}

export interface IRoutingConfig {
  modeloAsignado: string;            // LLM seleccionado por el Prompt Router (gpt-4o-mini / gpt-4)
  temperaturaComputo: number;        // Determinismo lógico (Fijado en 0.0 para FAQs de negocio)
  maxTokensPermitidos: number;       // Cerca presupuestaria de consumo de hardware de IA
  perfilAgente: 'logistica' | 'finanzas' | 'legal' | 'retencion' | 'general'; // Identidad del sub-agente
}

export interface IAIEngineRequest {
  correlationId: string;             // Identificador único global de transacción para telemetría distribuida
  canalUsuarioId: string;            // Identificador físico del cliente final (WhatsApp ID / Web Token)
  configuracionRuteo: IRoutingConfig;
  contextoInyectadoRag?: IRagContext;
  conversacionActual: IChatContext;
}
```

### 📤 Contrato de Salida (`IAIEngineResponse`)
Estructura unificada que el microservicio de IA devuelve hacia el procesador asíncrono para su distribución en Azure Event Hubs:

```typescript
export interface ITelemetryConsumption {
  modeloUtilizado: string;
  tokensPromptEntrada: number;
  tokensCompletionSalida: number;
  tokensTotalesFacturables: number;  // Insumo directo para el cálculo de ROI financiero (FinOps)
  latenciaComputoMilisegundos: number; // Métrica de rendimiento para acuerdos de nivel de servicio (SLA)
}

export interface ISecurityAudit {
  guardrailsEntradaAprobados: boolean;
  guardrailsSalidaAprobados: boolean; // Certificación del CISO contra fuga de información
  scoreConfianzaRag: number;          // Grado de correlación matemática con la verdad de la empresa
}

export interface IAIEngineResponse {
  correlationId: string;             // Retorna el mismo ID de entrada para auditoría de linaje de datos
  canalUsuarioId: string;
  textRespuestaGenerada: string;     // Frase limpia redactada por GenAI para desplegar al usuario
  telemetriaConsumo: ITelemetryConsumption;
  auditoriaSeguridad: ISecurityAudit;
}
```

---

## 🛠️ Ciclo de Desarrollo Local y Compilación

Para compilar las interfaces y generar los artefactos de distribución corporativa, ejecuta los siguientes comandos dentro de la raíz del directorio con tu entorno de Node.js activo:

```bash
# 1. Instalar las dependencias de desarrollo e infraestructura de tipado
npm install

# 2. Compilar el código fuente y exportar los binarios de TypeScript
npm run build

# 3. Limpiar los artefactos de compilación previos del disco
npm run clean
```
