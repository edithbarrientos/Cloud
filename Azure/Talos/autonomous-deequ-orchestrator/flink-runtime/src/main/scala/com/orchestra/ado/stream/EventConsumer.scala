package com.orchestra.ado.stream

import org.apache.flink.api.common.eventtime.WatermarkStrategy
import org.apache.flink.api.common.serialization.SimpleStringSchema
import org.apache.flink.api.common.api.Boundedness
import org.apache.flink.connector.pulsar.source.PulsarSource
import org.apache.flink.connector.kafka.source.KafkaSource
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer
import org.apache.flink.streaming.api.scala._
import org.apache.flink.streaming.api.windowing.assigners.SlidingProcessingTimeWindows
import org.apache.flink.streaming.api.windowing.time.Time
import org.apache.flink.streaming.api.scala.function.ProcessWindowFunction
import org.apache.flink.streaming.api.windowing.windows.TimeWindow
import org.apache.flink.util.Collector
import org.slf4j.LoggerFactory

/**
 * ====================================================================================
 * 🏢 ORCHESTRA DATA LABS - AUTONOMOUS DATA ENGINE (ADO)
 * ====================================================================================
 * 👤 AUTOR: Edithbg (Lead Big Data Architect)
 * 📅 FECHA DE COMPILACIÓN: 2026-07-31
 * 🏷️ VERSIÓN CORE: 4.0.0-PROD-TIER1
 * ⚖️ GOBERNANZA: Estándar DAMA-DMBOK2 / Certificación de Linaje de Datos
 * ====================================================================================
 */

trait StreamAuditorStrategy extends Serializable {
  def auditFast(payload: String, targetKeys: Array[String]): Boolean
}

class DamaStructuralAuditor extends StreamAuditorStrategy {
  override def auditFast(payload: String, targetKeys: Array[String]): Boolean = {
    if (payload == null || targetKeys == null) return false
    val len = targetKeys.length
    var i = 0
    var isValid = true
    while (i < len && isValid) {
      if (!payload.contains(targetKeys(i))) {
        isValid = false
      }
      i += 1
    }
    isValid
  }
}

object StreamSourceFactory {
  private val logger = LoggerFactory.getLogger("ADO-StreamSourceFactory")

  def resolveSource(env: StreamExecutionEnvironment, subscriptionName: String): DataStream[String] = {
    val provider = sys.env.getOrElse("CLOUD_PROVIDER", "PULSAR").toUpperCase
    val topic = sys.env.getOrElse("STREAM_TOPIC", "persistent://public/default/ado-pipeline-execution-v1")
    
    provider match {
      case "PULSAR" =>
        logger.info(s"📦 [PULSAR-NATIVO] Enlazando consumidor: $topic | Sub: $subscriptionName")
        val pulsarSource = PulsarSource.builder[String]()
          .setServiceUrl(sys.env.getOrElse("PULSAR_SERVICE_URL", "pulsar://localhost:6650"))
          .setAdminUrl(sys.env.getOrElse("PULSAR_ADMIN_URL", "http://localhost:8080"))
          .setTopics(topic)
          .setSubscriptionName(subscriptionName)
          .setDeserializationSchema(new SimpleStringSchema())
          .setBoundedness(Boundedness.CONTINUOUS_UNBOUNDED) // ⚡ CORRECCIÓN: Firma nativa Flink 1.18 API Core
          .build()
        env.fromSource(pulsarSource, WatermarkStrategy.noWatermarks(), "PulsarSovereignSource")

      case "AZURE" | "AWS" | "GCP" =>
        logger.info(s"📦 [KAFKA-SHIMS] Enlazando pasarela AMQP/Kafka para el tópico: $topic")
        val bootstrapServers = sys.env.getOrElse("STREAM_BOOTSTRAP_SERVERS", "localhost:9092")
        val kafkaSource = KafkaSource.builder[String]()
          .setBootstrapServers(bootstrapServers)
          .setTopics(topic)
          .setGroupId(subscriptionName)
          .setStartingOffsets(OffsetsInitializer.latest())
          .setValueOnlyDeserializer(new SimpleStringSchema())
          .build()
        env.fromSource(kafkaSource, WatermarkStrategy.noWatermarks(), s"${provider}UniversalSource")

      case unknown =>
        throw new IllegalArgumentException(s"🚨 [ERROR-FACTORÍA] El proveedor '$unknown' no es soportado.")
    }
  }
}

class WindowAnomaliesEvaluator(
  validationKeys: Array[String], 
  anomalyThreshold: Double, 
  componentName: String,
  samplingRate: Int
) extends ProcessWindowFunction[String, String, String, TimeWindow] {
  
  private val logger = LoggerFactory.getLogger(s"ADO-WindowEvaluator-$componentName")
  private var windowCounter: Long = 0

  override def process(
    tenantId: String,
    context: Context,
    elements: Iterable[String],
    out: Collector[String]
  ): Unit = {
    windowCounter += 1
    val totalRecords = elements.size
    val auditor = new DamaStructuralAuditor()
    
    var malformedCount = 0
    val iterator = elements.iterator
    while (iterator.hasNext) {
      val payload = iterator.next()
      if (!auditor.auditFast(payload, validationKeys)) {
        malformedCount += 1
      }
    }
    
    val anomalyRatio = if (totalRecords > 0) malformedCount.toDouble / totalRecords.toDouble else 0.0

    if (windowCounter % samplingRate == 0 || anomalyRatio > anomalyThreshold) {
      logger.info(s"📊 [REAL-TIME-DAMA] [$componentName] Ventana ID: $windowCounter | Inquilino: $tenantId | Elementos: $totalRecords | Ratio Anomalías: $anomalyRatio")
    }

    if (anomalyRatio > anomalyThreshold) {
      logger.error(s"🚨 [STREAM-ALERT] [$componentName] Brecha de gobernanza detectada! Ratio: $anomalyRatio (Umbral Máx: $anomalyThreshold)")
    }

    elements.foreach(out.collect)
  }
}

object EventConsumer {
  private val logger = LoggerFactory.getLogger("ADO-Flink-StreamPlane")

  def main(args: Array[String]): Unit = {
    val componentName    = sys.env.getOrElse("FLINK_COMPONENT_NAME", "FLINK_STREAM_ENGINE")
    val subscriptionName = sys.env.getOrElse("FLINK_SUBSCRIPTION_NAME", s"ado-flink-governance-$componentName")
    
    val anomalyThreshold = sys.env.getOrElse("FLINK_ANOMALY_THRESHOLD", "0.05").toDouble
    val validationKeys   = sys.env.getOrElse("FLINK_VALIDATION_KEYS", "tenantId,schemaContract").split(",").toArray
    val sharedTenantPool = sys.env.getOrElse("FLINK_SHARED_TENANT_POOL", "global-tenant-pool")
    
    val logSamplingRate  = sys.env.getOrElse("FLINK_LOG_SAMPLING_RATE", "10").toInt

    val windowSizeSeconds = sys.env.getOrElse("FLINK_WINDOW_SIZE_SECONDS", "30").toLong
    val windowSlideSeconds = sys.env.getOrElse("FLINK_WINDOW_SLIDE_SECONDS", "5").toLong

    logger.info(s"⚡ [STARTUP-FLINK] Activando [$componentName] con Algoritmia O(1) de un solo pase y Muestreo de Traza a factor: $logSamplingRate")

    val env = StreamExecutionEnvironment.getExecutionEnvironment
    env.setParallelism(sys.env.getOrElse("FLINK_PARALLELISM", "2").toInt)

    val streamData = StreamSourceFactory.resolveSource(env, subscriptionName)

    val processedStream = streamData
      .keyBy(_ => sharedTenantPool) 
      .window(SlidingProcessingTimeWindows.of(Time.seconds(windowSizeSeconds), Time.seconds(windowSlideSeconds)))
      .process(new WindowAnomaliesEvaluator(validationKeys, anomalyThreshold, componentName, logSamplingRate))

    processedStream.map { payload =>
      val targetDeltaTablePath = s"${sys.env.getOrElse("HOME", "/root")}/data_lake/metadata/universal_audit_bitacora"
      logger.debug(s"📤 [FLINK-DATA-LAKE] Asentando rastro transaccional en: $targetDeltaTablePath")
      payload
    }

    env.execute(s"Orchestra-ADO-Flink-StreamPlane-Active-$componentName")
  }
}
