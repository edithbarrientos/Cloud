package com.orchestra.ado.stream

import com.orchestra.ado.models.DataContract
import org.apache.flink.runtime.testutils.MiniClusterResourceConfiguration
import org.apache.flink.test.util.MiniClusterWithClientResource
import org.apache.flink.streaming.api.scala._
import org.apache.flink.streaming.api.scala.async.AsyncDataStream
import org.scalatest.BeforeAndAfterAll
import org.scalatest.matchers.should.Matchers
import org.scalatest.wordsspec.AnyWordSpec
import org.slf4j.LoggerFactory
import java.util.concurrent.TimeUnit
import scala.util.Random

/**
 * === Flink Stream Topology AI Integration Specification ===
 * Suite de pruebas de integración que levanta un MiniCluster nativo de la JVM implementando
 * algoritmos estocásticos de IA para simular variaciones semánticas volumétricas en la malla.
 */
class StreamTopologySpec extends AnyWordSpec with Matchers with BeforeAndAfterAll {

  private val logger = LoggerFactory.getLogger(this.getClass)

  // Infraestructura elástica: Crear un mini-nodo de Flink embebido en memoria RAM
  private val flinkCluster = new MiniClusterWithClientResource(
    new MiniClusterResourceConfiguration.Builder()
      .setNumberSlotsPerTaskManager(2)
      .setNumberTaskManagers(1)
      .build()
  )

  override protected def beforeAll(): Unit = {
    super.beforeAll()
    flinkCluster.before()
    logger.info("🏢 [MINI-CLUSTER FLINK]: Nodo local tolerante a fallos inicializado en la memoria de la Mac.")
  }

  override protected def afterAll(): Unit = {
    flinkCluster.after()
    logger.info("🏢 [MINI-CLUSTER FLINK]: Recursos desmontados y liberados de la JVM de forma limpia.")
    super.afterAll()
  }

  /**
   * 🚀 ALGORITMO DE IA ADVERSARIA: Sintetizador de Desviación Semántica Corporativa.
   * Genera dinámicamente strings de chat simulando alta entropía y mutaciones de payload.
   */
  private def synthesizeContextualDrift(tenant: String): String = {
    val corpora = List(
      "SELECT completeness FROM delta_lake.azure_table WHERE tenant = '",
      "ERROR: OutOfMemoryException caught in JVM task slot reference: ",
      "Hola, requiero procesar la gobernanza DAMA de la ráfaga continua id: ",
      "{\"quality_metrics\": {\"completitud\": 0.99, \"uuid\": \""
    )
    val baseSeed = corpora(Random.nextInt(corpora.size))
    val noisePadding = Random.alphanumeric.take(15).mkString
    s"$baseSeed$tenant-$noisePadding'"
  }

  "La Topología Continua del Stream Plane (DataOps Pipeline)" should {

    "orquestar la ingesta distribuida, mapear logs asíncronos y despachar las evaluaciones de IA sin colapsar" in {
      
      implicit val env: StreamExecutionEnvironment = StreamExecutionEnvironment.getExecutionEnvironment
      env.setParallelism(2)

      // 🚀 INFERENCIA DEL SINTETIZADOR DE IA: Construcción elástica de la ráfaga de datos inmutable
      val simulatedChatBatches = (1 to 5).map { index =>
        val targetTenant = if (index % 2 == 0) "tenant-alpha-enterprise" else "tenant-beta-gov"
        val aiGeneratedPayload = synthesizeContextualDrift(targetTenant)
        val estimatedTokens = DataContract.estimateTokens(aiGeneratedPayload)

        logger.info(s"🧠 [SINTETIZADOR COGNITIVO] Registrando Batch #$index | Tenant: $targetTenant | Payload Mutado: '$aiGeneratedPayload' | Tokens: $estimatedTokens")

        DataContract(
          id = s"stream-ai-uuid-0$index",
          tenantId = targetTenant,
          sessionId = s"sess-token-k8s-00$index",
          payload = aiGeneratedPayload,
          timestamp = System.currentTimeMillis(),
          estimatedTokens = estimatedTokens,
          charCount = aiGeneratedPayload.length
        )
      }.toList

      // Convertir la colección en un canal de transmisión de datos puro de Flink
      val chatStream: DataStream[DataContract] = env.fromCollection(simulatedChatBatches)

      // Acoplar la ventana elástica del evaluador asíncrono no bloqueante
      val diagnosticStream: DataStream[String] = AsyncDataStream.unorderedWait(
        chatStream,
        new AsyncAIEvaluator("http://localhost:8999/v1/evaluate", timeoutMs = 3000L, maxRetries = 1),
        3000L,
        TimeUnit.MILLISECONDS,
        10
      ).name("Test-Async-AI-Evaluator")

      diagnosticStream.print().name("Test-Console-Sink")

      // Forzar el arranque de los hilos de streaming y certificar que no arroje excepciones catastróficas
      noException should be thrownBy {
        logger.info("⚙️ [TEST RUN]: Ejecutando topología inmutable sobre el MiniCluster con datos elásticos de IA...")
        env.execute("Test-Omega-QualityMesh-Stream-Plane")
      }
    }
  }
}
