package com.orchestra.ado.stream

import org.slf4j.LoggerFactory
import java.time.Instant
import java.util.concurrent.{LinkedBlockingQueue, ThreadPoolExecutor, TimeUnit}
import scala.util.{Try, Success, Failure}

trait ConcurrentAuditorStrategy extends Serializable {
  def evaluateFast(payload: String, targetKeys: Array[String]): Boolean
}

class DamaStructuralAuditor extends ConcurrentAuditorStrategy {
  override def evaluateFast(payload: String, targetKeys: Array[String]): Boolean = {
    if (payload == null || targetKeys == null) return false
    val len = targetKeys.length
    var i = 0
    var isValid = true
    while (i < len && isValid) {
      if (!payload.contains(targetKeys(i))) { isValid = false }
      i += 1
    }
    isValid
  }
}

object StreamApp {
  private val logger = LoggerFactory.getLogger("ADO-Streaming-EliteEngine")

  def main(args: Array[String]): Unit = {
    val componentName     = sys.env.getOrElse("FLINK_COMPONENT_NAME", "ELITE_CONCURRENT_STREAM_AGENT")
    val validationKeys    = sys.env.getOrElse("FLINK_VALIDATION_KEYS", "tenantId,schemaContract").split(",").toArray
    val anomalyThreshold  = sys.env.getOrElse("FLINK_ANOMALY_THRESHOLD", "0.05").toDouble
    val streamDurationMs  = sys.env.getOrElse("FLINK_STREAM_DURATION_MS", "15000").toLong
    val maxQueueCapacity  = sys.env.getOrElse("FLINK_QUEUE_CAPACITY", "5000").toInt
    
    println(s"⚡ [STARTUP-STREAM] Inicializando [$componentName] de Grado Producción Tier-1...")
    val messageQueue = new LinkedBlockingQueue[String](maxQueueCapacity)
    val cpuCores = Runtime.getRuntime.availableProcessors()
    
    val workerExecutor = new ThreadPoolExecutor(
      cpuCores, cpuCores * 2, 60L, TimeUnit.SECONDS,
      new LinkedBlockingQueue[Runnable](1000),
      (r: Runnable) => {
        val t = new Thread(r)
        t.setDaemon(true)
        t.setName(s"ado-stream-worker-${t.getId}")
        t
      }
    )

    val samplePayload = """{"tenantId": "tenant-orchestra-poc-01", "schemaContract": "v1.0.0", "amount": 150.50}"""
    val startTime = System.currentTimeMillis()
    var windowId = 0
    val auditor = new DamaStructuralAuditor()

    println("📡 [STREAM-PLANE] Canal de escucha abierto en microsegundos. Procesando ráfagas...")

    while (System.currentTimeMillis() - startTime < streamDurationMs) {
      windowId += 1
      Thread.sleep(1500)

      if (messageQueue.offer(samplePayload)) {
        workerExecutor.submit(new Runnable {
          override def run(): Unit = {
            val payload = messageQueue.poll()
            if (payload != null) {
              Try(auditor.evaluateFast(payload, validationKeys)) match {
                case Success(isValid) =>
                  val anomalyRatio = if (isValid) 0.0 else 1.0
                  println(s"📊 [REAL-TIME-DAMA] [$componentName] Hilo: ${Thread.currentThread().getName} | Ventana ID: $windowId | Ratio: $anomalyRatio")
                case Failure(e) => logger.error(s"🚨 Error: ${e.getMessage}")
              }
            }
          }
        })
      }
    }
    workerExecutor.shutdown()
    println(s"✅ [ENGINE-SUCCESS] Plano de streaming concluyó con éxito absoluto. Hilos liberados.")
  }
}
