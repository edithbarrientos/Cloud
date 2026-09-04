# 🏛️ ai-agentic-deequ-core - Operations & MLOps Manual

> Manual técnico operativo y de AI Engineering destinado al análisis de modelos estocásticos, algoritmos de machine learning embebidos, Feature Store perimetral, esquemas NoSQL y directivas elásticas de orquestación en Kubernetes.

---

## 🧮 Especificación Algorítmica y MLOps Performance Feature Store

### 1. Edge Inference Pipeline (Logit Dense Perceptron Graph)
El motor de ejecución de **ONNX Runtime (C++ Engine)** procesa las características en tiempo constante \(\mathcal{O}(1)\) para inferir la probabilidad de corrupción latente del dato de entrada. Mapea en el silicio un grafo neuronal de un solo perceptrón denso, resolviendo la siguiente ecuación logística:

\[Z = (\omega_1 \cdot \text{inputMetricValue}) + (\omega_2 \cdot \text{inputStepSequence}) + b\]

\[\text{predictedProbability} = \sigma(Z) = \frac{1}{1 + e^{-Z}}\]

*Donde el vector de pesos fijos (weights) corresponde a:* ω₁ = 2.85, ω₂ = -0.001 y el sesgo (bias) b = -2.10. La salida escalar es desempaquetada a nivel atómico binario de memoria mediante el método `.item()`, evitando la sobrecarga de conversión del intérprete.

### 2. Monitoreo de Data Drift Continuo (Stochastic Anomalies Engine)
Para evaluar la degradación del Producto de Datos en background sin penalizar el throughput de la red, el sistema acopla en paralelo dos metodologías estadísticas continuas:

* **Métrica de Distancia Analítica (Wasserstein Distance Simplificada)**: Mide el desplazamiento geométrico absoluto del lote en caliente (*Feature Store Stream*) frente a la distribución nominal base cargada en la RAM del pod (\(\mu_{\text{base}} = 0.90\)):
\[\text{observedWassersteinDistance} = \vert{}\text{inputMetricValue} - 0.90\vert{}\]

* **Cálculo de Desviación Estocástica Real (Z-Score Drift)**: Determina cuántas desviaciones estándar (σ) se encuentra el vector actual lejos de la media móvil adaptativa histórica rastreada en la caché L1 local:
\[\text{actualZScoreDrift} = \frac{\text{inputMetricValue} - \mu_{\text{historical}}}{\sigma}\]

*Gatillo Automático de Re-entrenamiento (MLOps Closed-Loop)*: Si el motor de anomalías registra un actualZScoreDrift > 3.0 (Frontera crítica de tres sigmas en la campana de Gauss), la señal FinOps `isReTrainingTriggered` conmuta a `TRUE`. Esto despacha un message reactivo no bloqueante hacia el clúster distribuidor de **Apache Spark MLlib**, el cual re-entrena el modelo y re-emplaza el artefacto `.onnx` en el Object Store.

---

## 💾 Modelo de Datos Fusionado NoSQL / Delta Lake

La persistencia operativa hacia bases de datos NoSQL se almacena en formato de **Documentos JSON jerárquicos estructurados en lowerCamelCase**. Por la noche, Apache Spark ejecuta el operador `EXPLODE` sobre la matriz para alimentar la tabla analítica relacional consolidada (`ColFusedDamaDriftLedger`) en el Data Lakehouse:

```sql
CREATE TABLE IF NOT EXISTS ColFusedDamaDriftLedger (
    rowUid STRING NOT NULL COMMENT 'UUID unico de la fila desanidada y fusionada',
    logId STRING NOT NULL COMMENT 'FK de enlace directo a la bitacora de ejecucion (trace_id)',
    dimensionName STRING NOT NULL COMMENT 'Nombre de la dimension DAMA extendida',
    dimensionStatus STRING NOT NULL COMMENT 'Estatus local de aprobacion (SUCCESS | FAILED)',
    anomalySeverity STRING NOT NULL COMMENT 'Severidad dictaminada (NOMINAL | HIGH | CRITICAL)',
    compliancePercentage DOUBLE NOT NULL COMMENT 'Porcentaje exacto calculado por las formulas de negocio',
    observedWassersteinDistance DOUBLE NOT NULL COMMENT 'ML DRIFT: Distancia analitica de distribucion',
    actualZScoreDrift DOUBLE NOT NULL COMMENT 'ML DRIFT: Z-Score estocastico calculado por el AI Engine',
    isReTrainingTriggered BOOLEAN NOT NULL COMMENT 'ML DRIFT: Flag de re-entrenamiento de Spark'
) USING DELTA LOCATION 'data/lakehouse/silver/ColFusedDamaDriftLedger';
```

---

## 📈 Contrato de Observabilidad para Prometheus & Grafana Endpoints

Para el monitoreo centralizado de la salud del Data Product en clusters distribuidos, cada Pod expone las métricas DAMA agregadas y el performance del modelo ONNX en el estándar abierto OpenMetrics:

```text
# HELP deequ_core_inference_latency_microseconds Latencia pura de inferencia de C++ ONNX en microsegundos
# TYPE deequ_core_inference_latency_microseconds gauge
deequ_core_inference_latency_microseconds{modelUid="onnx-dense-mlp-v1.4.0", datasetName="iot_sensor_telemetry"} 42.0

# HELP deequ_core_dama_compliance_ratio Porcentaje de cumplimiento matematico por cada dimension DAMA
# TYPE deequ_core_dama_compliance_ratio gauge
deequ_core_dama_compliance_ratio{dimensionName="EXACTITUD", domainScope="Logistics"} 92.89
deequ_core_dama_compliance_ratio{dimensionName="COMPLETITUD", domainScope="Logistics"} 100.00
deequ_core_dama_compliance_ratio{dimensionName="UNICIDAD", domainScope="Logistics"} 100.00
```

---

## 🛠️ Guía de Operación Local (Automation Tooling)

El repositorio está instrumentado con un `Makefile` inteligente equipado con colores ANSI y sondas previas de salud del S.O.

* `make help`          : Despliega el menú ejecutivo indexado de comandos.
* `make init`          : Inicializa el entorno virtual Python 3.12 y congela las dependencias.
* `make compile-proto` : Compila los contratos binarios hacia stubs Python.
* `make run-local`     : Arranca el clúster multiprocesamiento nativo (`SO_REUSEPORT`).
* `make stress-test`   : Gatilla el bombardeo multiplexado elástico a 1,998 req/seg.

---

## 📦 Arquitectura de Despliegue en la Nube (Kubernetes / AKS ready)

La suite cuenta con una receta de construcción **Dockerfile Multi-Stage Hardened** de peso pluma (**<50MB**), la cual remueve compiladores como `gcc` en su fase final y corre bajo un identificador de usuario **No-Root (UID 10001)** para mitigar escalamientos de privilegios en la nube (CIS Benchmark Compliance).

Los manifiestos alojados en `deployments/kubernetes/k8s_deployment.yaml` aprovisionan:
* **Tuning de Kernel**: Un `initContainer` de Linux configura `net.core.somaxconn=32768` para digerir ráfagas extremas.
* **Elasticidad Dinámica**: Configuración de `HorizontalPodAutoscaler` (HPA) para escalar de 3 hasta 10 réplicas concurrentes si el uso de CPU cruza el 75%.
* **Zero Data Loss**: Inyección de un ciclo de vida `preStop` con un retraso elástico de `sleep 15` para vaciar las colas asíncronas de la RAM (`asyncio.Queue`) hacia el storage analítico antes de desmantelar el pod.
