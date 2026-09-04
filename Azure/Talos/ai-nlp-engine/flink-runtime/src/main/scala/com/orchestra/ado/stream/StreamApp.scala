package com.orchestra.ado.stream

import org.apache.flink.api.common.typeinfo.TypeInformation
import org.apache.flink.util.Collector
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment
import org.apache.flink.streaming.api.datastream.DataStream
import org.apache.flink.streaming.api.datastream.AsyncDataStream
import org.apache.flink.api.common.functions.MapFunction
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.module.scala.DefaultScalaModule
import com.typesafe.config.ConfigFactory
import org.slf4j.LoggerFactory
import java.util.concurrent.TimeUnit
import java.util.UUID

/**
  * Orquestador Core Distribuidor Elástico con Server Socket Automático.
  * Abre el puerto 9999 de forma nativa eliminando la necesidad del comando nc -lk.
  * 
  * @author Edith Barrientos
  * @version 9.0.0-AUTONOMOUS-SERVER
  */
object StreamApp {
  
  @transient lazy val log = LoggerFactory.getLogger(getClass)

  def main(args: Array[String]): Unit = {
    import org.apache.flink.api.scala.createTypeInformation

    val conf = ConfigFactory.load()
    val defaultParallelism   = conf.getInt("flink.default-parallelism")
    val checkpointInterval   = conf.getLong("flink.checkpoint-interval-ms")
    val aiApiUrl             = conf.getString("ai-service.api-url")
    val aiTimeoutMs          = conf.getLong("ai-service.timeout-ms")
    val maxConcurrentRequests = conf.getInt("ai-service.max-concurrent-requests")
    val maxRetries           = conf.getInt("ai-service.max-retries")

    log.info("⚙️  [StreamApp-Bootstrap] Inicializando grafo de Flink con Server TCP nativo.")

    // ⎈ 2. CONFIGURACIÓN DEL ENTORNO DE EJECUCIÓN DISTRIBUIDO
    val env = StreamExecutionEnvironment.getExecutionEnvironment
    env.setParallelism(defaultParallelism)
    env.getCheckpointConfig.setCheckpointInterval(checkpointInterval)

    // ==============================================================================
    // 📦 4. CONECTOR COMPONENTE: SOURCE (ACTÚA COMO SERVER EN EL PUERTO 9999)
    // Al usar "0.0.0.0", Flink abre el puerto y se queda escuchando a tu Mac.
    // ==============================================================================
    val stringStream: DataStream[String] = env.socketTextStream("0.0.0.0", 9999, '\n', 10)

    // 🧮 5. CAPA DE TRANSFORMACIÓN Y ACOPLE CONTRACTUAL DE CALIDAD (MAP STAGE)
    val mappedStream: DataStream[AnomalyEvent] = stringStream.map(new MapFunction[String, AnomalyEvent] {
      @transient private lazy val mapper: ObjectMapper = {
        val m = new ObjectMapper()
        m.registerModule(DefaultScalaModule)
        m
      }

      override def map(value: String): AnomalyEvent = {
        if (value != null && value.contains("{")) {
          try {
            mapper.readValue(value, classOf[AnomalyEvent])
          } catch {
            case _: Exception => generateFallback(value)
          }
        } else {
          generateFallback(value)
        }
      }

      private def generateFallback(content: String): AnomalyEvent = {
        val randId = UUID.randomUUID().toString.take(8)
        AnomalyEvent(
          tenantId = "tenant_generic", clientId = s"client-$randId", customerId = s"cust-$randId",
          sessionId = "session-stream-99", messageId = s"msg-$randId", timestamp = java.time.Instant.now().toString,
          source = "JVM_SERVER_SOCKET", message = content, rawMessage = content, issueCategory = "GREETING",
          summary = "Internal Flink Server Socket", attachment = "NONE"
        )
      }
    })

    // 🚀 6. CAPA ASÍNCRONA DE ALTA DISPONIBILIDAD (INFERENCIA MULTIPLEXADA NO BLOQUEANTE)
    val evaluator = new AsyncAIEvaluator(aiApiUrl, aiTimeoutMs, maxRetries)
    val resultStream = AsyncDataStream.unorderedWait(
      mappedStream, evaluator, aiTimeoutMs, TimeUnit.MILLISECONDS, maxConcurrentRequests
    )

    // 🧠 6.5. INYECCIÓN DEL MOTOR COGNITIVO AVANZADO SINCRO-TIPADO
    val finalRoutedStream = AIIntentRoutingEngine.injectAdvancedPipeline(env, resultStream)

    // 🔌 7. SINK FINAL MULTI-CANAL EN VIVO
    finalRoutedStream.print().name("Sink-Flujo-Estandar")
    finalRoutedStream.getSideOutput(AIIntentRoutingEngine.criticalBillingTag).print().name("Sink-VIP-Financiero-Alertas")
    finalRoutedStream.getSideOutput(AIIntentRoutingEngine.deadLetterQueueTag).print().name("Sink-DLQ-Gobernanza")
    
    env.execute("Omega-QualityMesh-Stream-Protobuf-Nativo")
  }
}