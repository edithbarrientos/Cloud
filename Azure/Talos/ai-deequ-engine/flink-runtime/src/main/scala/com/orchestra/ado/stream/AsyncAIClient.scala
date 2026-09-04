package com.orchestra.ado.stream

import com.orchestra.ado.models.DataContract
import org.slf4j.LoggerFactory
import java.net.URI
import java.net.http.{HttpClient, HttpRequest, HttpResponse}
import java.time.Duration
import java.util.concurrent.{CompletableFuture, ScheduledExecutorService, Executors, TimeUnit}
import java.util.concurrent.atomic.AtomicInteger
import upickle.default._

/**
 * ==============================================================================================
 * 🚀 CLIENTE DE TRANSMISIÓN ASÍNCRONA DE IA CON PATRONES DE DISEÑO LLMOps & DAMA GOVERNANCE
 * ==============================================================================================
 * 
 * DESIGN PATTERN: Async I/O Multiplexing (No-Bloqueante)
 * Este cliente encapsula el motor HTTP/2 de Java 11 para despachar contratos analíticos de chat
 * de manera asíncrona hacia microservicios perimetrales (Akka HTTP). Su propósito fundamental es 
 * asegurar que los hilos de procesamiento de Apache Flink (TaskManager) nunca entren en estado 
 * de espera síncrona (Block Estado), lo que destruiría el rendimiento del clúster distributed.
 *
 * @param apiUrl     Ruta DNS interna y absoluta del endpoint de evaluación analítica dentro de Kubernetes.
 * @param timeoutMs  Ventana máxima de tolerancia de red en milisegundos por cada intento HTTP antes de abortar.
 * @param maxRetries Límite estricto de intentos de red permitidos para mitigar fallas transitorias antes de colapsar.
 */
class AsyncAIClient(apiUrl: String, timeoutMs: Long, maxRetries: Int) extends Serializable {
  
  // Instanciación perezosa y transient para evitar errores de serialización Java al distribuir la clase por la red
  @transient private lazy val logger = LoggerFactory.getLogger(this.getClass)
  
  /**
   * DESIGN PATTERN: Thread Pool Isolation (Aislamiento de Hilos)
   * Pool de hilos dedicado exclusivamente a planificar los retrasos de los reintentos analíticos.
   * Al aislarlo en un pool de un solo hilo dedicado, garantizamos que los reintentos exponenciales
   * no consuman, ni interfieran, con el pool de hilos principal de ejecución de Apache Flink.
   */
  @transient private lazy val scheduler: ScheduledExecutorService = Executors.newScheduledThreadPool(1)
  
  /**
   * DESIGN PATTERN: HTTP/2 Multiplexing Pipeline
   * Cliente HTTP nativo configurado explícitamente en modo HTTP_2. Esto permite que decenas de peticiones
   * viajen en paralelo a través de un único socket tcp abierto hacia tu API de Akka HTTP, evitando la 
   * saturación de puertos efímeros en el Kernel de Linux de Colima.
   */
  @transient private lazy val httpClient: HttpClient = HttpClient.newBuilder()
    .version(HttpClient.Version.HTTP_2)
    .connectTimeout(Duration.ofMillis(timeoutMs))
    .build()

  /**
   * Punto de entrada de despacho asíncrono.
   * Convierte un flujo secuencial en una promesa futura compatible con la API reactiva de Flink.
   *
   * @param contract Estructura inmutable del contrato de datos de chat extraído de Apache Pulsar.
   * @return Un [[java.util.concurrent.CompletableFuture]] que Flink resolverá cuando el microservicio responda.
   */
  def evaluatePayloadAsync(contract: DataContract): CompletableFuture[String] = {
    val finalFuture = new CompletableFuture[String]()
    // Iniciamos el ciclo recursivo asíncronamente con un contador de intentos inicializado en 0
    executeWithRetry(contract, new AtomicInteger(0), finalFuture)
    finalFuture
  }

  /**
   * Pipeline interno recursivo encargado de estructurar las cabeceras analíticas de IA.
   */
  private def executeWithRetry(
    contract: DataContract, 
    attempt: AtomicInteger, 
    resultFuture: CompletableFuture[String]
  ): Unit = {
    try {
      // Serialización ultra rápida del contrato utilizando la librería nativa uPickle
      val jsonPayload = write(contract)

      /**
       * DESIGN PATTERN: Contextual Metadata Enrichment (Enriquecimiento Perimetral)
       * Inyección de metadatos analíticos clave directamente en las cabeceras HTTP. 
       * Este patrón permite que proxies de IA o Service Meshes auditen cuotas de tokens, límites de
       * velocidad y telemetría por Tenant a nivel de red (Capas 4/7) sin incurrir en el costo computacional 
       * de abrir y deserializar el cuerpo del JSON (Payload Body) en cada salto.
       */
      val request = HttpRequest.newBuilder()
        .uri(URI.create(apiUrl))
        .timeout(Duration.ofMillis(timeoutMs))
        .header("Content-Type", "application/json")
        .header("X-Tenant-ID", contract.tenantId)
        .header("X-Session-ID", contract.sessionId)
        .header("X-Estimated-Tokens", contract.estimatedTokens.toString)
        .header("X-Chat-Char-Count", contract.charCount.toString)
        .POST(HttpRequest.BodyPublishers.ofString(jsonPayload))
        .build()

      // Despacho asíncrono puro no bloqueante al Stack de Red del sistema operativo
      httpClient.sendAsync(request, HttpResponse.BodyHandlers.ofString())
        .thenAccept(new java.util.function.Consumer[HttpResponse[String]] {
          override def accept(response: HttpResponse[String]): Unit = {
            response.statusCode() match {
              case 200 => 
                // Éxito absoluto: Completamos la promesa y Flink continúa el stream de inmediato
                resultFuture.complete(response.body())
                
              case 429 => 
                // DESIGN PATTERN: Backpressure Tolerant (Tolerancia a la Saturación del Clúster de IA)
                // Si la API responde 429 (Rate Limit), se asume fatiga transitoria y se gatilla el reatrás exponencial.
                logger.warn(s"⚠️ [AI THROTTLED] Código 429 detectado en Tenant: ${contract.tenantId}. Gatillando reintento exponencial.")
                handleRetry(contract, attempt, resultFuture, new RuntimeException("AI API Rate Limited (429)"))
                
              case status =>
                // Error Semántico Controlado: La API contestó un error (400, 500, etc.)
                // No rompemos el hilo distribuido; devolvemos un JSON de bandera estructurado para auditoría.
                logger.error(s"❌ [ERROR SEMÁNTICO] Respuesta anómala ($status) del motor de Akka HTTP para mensaje: ${contract.id}")
                resultFuture.complete(s"""{"status":"ERROR","code":$status,"message_id":"${contract.id}"}""")
            }
          }
        }).exceptionally(new java.util.function.Function[Throwable, Void] {
          override def apply(ex: Throwable): Void = {
            // Error de Conectividad de Red Física (Timeout, Host Inalcanzable, etc.)
            logger.warn(s"⚠️ [FALLO DE CONEXIÓN] Intento ${attempt.get() + 1} fallido para mensaje ${contract.id}: ${ex.getMessage}")
            handleRetry(contract, attempt, resultFuture, ex)
            null
          }
        })

    } catch {
      case ex: Exception =>
        // Error catastrófico estructural interno del código
        logger.error(s"💥 Excepción crítica estructural en el cliente asíncrono de Flink: ${ex.getMessage}")
        resultFuture.complete(s"""{"status":"CRITICAL_FAILURE","exception":"${ex.getClass.getSimpleName}"}""")
    }
  }

  /**
   * ==============================================================================================
   * DESIGN PATTERN: Exponential Backoff (Algoritmo de Retroceso Exponencial Asíncrono)
   * ==============================================================================================
   * Calcula el tiempo de retraso óptimo utilizando una curva exponencial multiplicada por un factor base.
   * Evita el efecto de "manada desbocada" (*Thundering Herd Problem*) sobre tu API de Akka HTTP.
   * 
   * Fórmula Matemática del retraso: Latencia = (2 ^ Intento) * 250 milisegundos.
   *   - Intento 1: (2^1) * 250ms = 500ms de espera.
   *   - Intento 2: (2^2) * 250ms = 1000ms de espera.
   *   - Intento 3: (2^3) * 250ms = 2000ms de espera.
   */
  private def handleRetry(
    contract: DataContract, 
    attempt: AtomicInteger, 
    resultFuture: CompletableFuture[String], 
    ex: Throwable
  ): Unit = {
    if (attempt.incrementAndGet() <= maxRetries) {
      val backoffMs = Math.pow(2, attempt.get().toDouble).toLong * 250L
      
      // El planificador agenda el reintento futuro de forma no bloqueante
      scheduler.schedule(new Runnable {
        override def run(): Unit = executeWithRetry(contract, attempt, resultFuture)
      }, backoffMs, TimeUnit.MILLISECONDS)
      
    } else {
      /**
       * DESIGN PATTERN: Autonomous Circuit Breaker (Cierre de Circuito Autónomo por Mensaje)
       * Si se agota el número límite de reintentos analíticos permitidos (`maxRetries`), el componente
       * activa su disyuntor automático, aborta la operación y emite un JSON seguro de bandera 
       * para evitar que el Job de Flink se congele en un bucle infinito o degrade la memoria RAM.
       */
      logger.error(s"🔒 [CIRCUIT BREAKER] Límite de reintentos alcanzado para mensaje: ${contract.id}. Abortando pipeline.")
      resultFuture.complete(s"""{"status":"CIRCUIT_BREAKER_ABORT","exception":"${ex.getClass.getSimpleName}","message_id":"${contract.id}"}""")
    }
  }
}