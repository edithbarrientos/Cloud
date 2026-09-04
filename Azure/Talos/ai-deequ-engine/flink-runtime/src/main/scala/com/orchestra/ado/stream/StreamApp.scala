package com.orchestra.ado.stream

import org.apache.flink.api.common.eventtime.WatermarkStrategy
import org.apache.flink.connector.pulsar.source.PulsarSource
import org.apache.flink.connector.pulsar.source.enumerator.cursor.StartCursor
import org.apache.flink.connector.pulsar.source.reader.deserializer.PulsarDeserializationSchema
import org.apache.flink.api.common.typeinfo.TypeInformation
import org.apache.flink.util.Collector
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment
import org.apache.flink.streaming.api.datastream.DataStream
import org.apache.flink.streaming.api.datastream.AsyncDataStream
import org.apache.pulsar.client.api.Message
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.module.scala.DefaultScalaModule
import com.typesafe.config.ConfigFactory
import org.slf4j.LoggerFactory
import java.util.concurrent.TimeUnit
import java.util.UUID

/**
 * 🪐 TOPOLOGÍA PRINCIPAL DE STREAMING (APACHE FLINK)
 * pipeline analítico agnóstico: Consume la configuración elástica de application.conf,
 * administra la succión de Pulsar por DNS de Kubernetes y procesa de forma asíncrona la IA.
 */
object StreamApp {
  
  @transient lazy val log = LoggerFactory.getLogger(getClass)

  def main(args: Array[String]): Unit = {
    // 🛠️ MAPPING DIRECTO DE TU CONFIGURACIÓN (Cero Hardcodeo)
    val conf = ConfigFactory.load()
    
    // Bloque Flink
    val defaultParallelism   = conf.getInt("flink.default-parallelism")
    val checkpointInterval   = conf.getLong("flink.checkpoint-interval-ms")
    
    // Bloque Pulsar
    val pulsarBrokerUrl      = conf.getString("pulsar.broker-url")
    val pulsarAdminUrl       = conf.getString("pulsar.admin-url")
    val subscriptionName     = conf.getString("pulsar.subscription-name")
    val topicChat            = conf.getString("pulsar.topic-chat")
    
    // Bloque AI Service
    val aiApiUrl             = conf.getString("ai-service.api-url")
    val aiTimeoutMs          = conf.getLong("ai-service.timeout-ms")
    val maxConcurrentRequests = conf.getInt("ai-service.max-concurrent-requests")
    val maxRetries           = conf.getInt("ai-service.max-retries")

    log.info("🪐 [StreamApp] Propiedades de Typesafe validadas. Inicializando Dataflow...")
    log.info("--> Broker Pulsar expuesto en DNS: [{}]", pulsarBrokerUrl)
    log.info("--> Backend AI expuesto en DNS: [{}]", aiApiUrl)

    // Inicializamos el entorno de Flink aplicando tus variables del archivo
    val env = StreamExecutionEnvironment.getExecutionEnvironment
    env.setParallelism(defaultParallelism)
    env.getCheckpointConfig.setCheckpointInterval(checkpointInterval)

    val pulsarDeserializer = new PulsarDeserializationSchema[Array[Byte]] {
      override def deserialize(message: Message[Array[Byte]], out: Collector[Array[Byte]]): Unit = {
        out.collect(message.getData)
      }
      override def getProducedType: TypeInformation[Array[Byte]] = TypeInformation.of(classOf[Array[Byte]])
    }

    val pulsarConfig = new org.apache.flink.configuration.Configuration()
    pulsarConfig.setString("flink.pulsar.adminUrl", pulsarAdminUrl)

    val pulsarSource = PulsarSource.builder[Array[Byte]]()
      .setServiceUrl(pulsarBrokerUrl) // 🪐 Acople directo con tu "pulsar://..." de las propiedades
      .setConfig(pulsarConfig)
      .setTopics(topicChat)
      .setStartCursor(StartCursor.latest()) 
      .setSubscriptionName(subscriptionName) 
      .setDeserializationSchema(pulsarDeserializer)
      .build()

    val byteStream: DataStream[Array[Byte]] = env.fromSource(pulsarSource, WatermarkStrategy.noWatermarks(), "Pulsar-Source-Binario")

    val mappedStream: DataStream[AnomalyEvent] = byteStream.map(new org.apache.flink.api.common.functions.MapFunction[Array[Byte], AnomalyEvent] {
      override def map(value: Array[Byte]): AnomalyEvent = {
        val rawText = new String(value, "UTF-8")
        if (rawText.contains("tenantId") || rawText.contains("{")) {
          try {
            val mapper = new ObjectMapper()
            mapper.registerModule(DefaultScalaModule)
            mapper.readValue(rawText, classOf[AnomalyEvent])
          } catch {
            case _: Exception => generateFallback(rawText)
          }
        } else {
          generateFallback(rawText)
        }
      }

      private def generateFallback(content: String): AnomalyEvent = {
        val fallbackId = UUID.randomUUID().toString.take(8)
        AnomalyEvent(
          tenantId = s"dynamic-tenant-$fallbackId",
          sessionId = s"dynamic-sess-$fallbackId",
          payload = content.replaceAll("[^\\x20-\\x7E]", "")
        )
      }
    })

    // Inyectamos las variables dinámicas del bloque ai-service al evaluador asíncrono
    val evaluator = new AsyncAIEvaluator(aiApiUrl, aiTimeoutMs, maxRetries)

    val resultStream = AsyncDataStream.unorderedWait(
      mappedStream, 
      evaluator, 
      aiTimeoutMs, 
      TimeUnit.MILLISECONDS, 
      maxConcurrentRequests // 🪐 Capacidad elástica amarrada a tus propiedades (max-concurrent-requests = 5)
    )

    resultStream.print().name("Sink-Consumo-Analitico")

    env.execute("Omega-QualityMesh-Stream-Protobuf-Nativo")
  }
}
