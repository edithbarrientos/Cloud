package com.orchestra.ado.stream

import com.orchestra.ado.models.DataContract
import org.apache.flink.api.common.serialization.DeserializationSchema
import org.apache.flink.api.common.typeinfo.TypeInformation
import org.apache.flink.connector.pulsar.source.PulsarSource
import org.apache.flink.connector.pulsar.source.enumerator.cursor.StopCursor
import org.slf4j.LoggerFactory
import upickle.default._
import java.nio.charset.StandardCharsets

class EventConsumer extends Serializable {
  @transient private lazy val logger = LoggerFactory.getLogger(this.getClass)

  def createPulsarSource(
    brokerUrl: String,
    topic: String,
    subscription: String,
    maxFetchRecords: Int
  ): PulsarSource[DataContract] = {

    val customSchema = new DeserializationSchema[DataContract] {
      override def deserialize(message: Array[Byte]): DataContract = {
        try {
          val rawJson = new String(message, StandardCharsets.UTF_8)
          read[DataContract](rawJson)
        } catch {
          case ex: Exception =>
            DataContract("CORRUPT","MALFORMED","N/A",ex.getClass.getSimpleName,System.currentTimeMillis(),0,0)
        }
      }
      override def isEndOfStream(nextElement: DataContract): Boolean = false
      override def getProducedType: TypeInformation[DataContract] = TypeInformation.of(classOf[DataContract])
    }

    // 🚀 CORRECCIÓN CONECTOR 4.1.0: Métodos unmanaged alineados
    PulsarSource.builder[DataContract]()
      .setServiceUrl(brokerUrl)
      .setTopics(topic)
      .setSubscriptionName(subscription)
      .setDeserializationSchema(customSchema)
      .setUnboundedStopCursor(StopCursor.never()) // Método oficial unbounded
      .build()
  }
}
