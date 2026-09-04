package com.orchestra.ado.stream

import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment
import org.apache.flink.streaming.api.datastream.DataStream
import org.apache.flink.streaming.api.datastream.AsyncDataStream
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.module.scala.DefaultScalaModule
import org.slf4j.LoggerFactory
import java.util.concurrent.TimeUnit

object MainTopologySnippet {
  
  @transient lazy val log = LoggerFactory.getLogger(getClass)

  def configureFlow(env: StreamExecutionEnvironment, apiUrl: String, timeoutMs: Long): Unit = {

    val pulsarStream: DataStream[Array[Byte]] = env.fromElements(Array[Byte]()) 

    val mappedStream: DataStream[AnomalyEvent] = pulsarStream.map(new org.apache.flink.api.common.functions.MapFunction[Array[Byte], AnomalyEvent] {
      override def map(value: Array[Byte]): AnomalyEvent = {
        val jsonStr = new String(value, "UTF-8")
        try {
          val mapper = new ObjectMapper()
          mapper.registerModule(DefaultScalaModule)
          mapper.readValue(jsonStr, classOf[AnomalyEvent])
        } catch {
          case ex: Exception =>
            log.warn(s"🚨 [MainTopology] Error Causa: ${ex.getMessage}")
            AnomalyEvent("orchestra-tenant-bypass-test", "sess-999", jsonStr)
        }
      }
    })

    val asyncStream = AsyncDataStream.unorderedWait(
      mappedStream,
      new AsyncAIEvaluator(apiUrl, timeoutMs, 1),
      timeoutMs,
      TimeUnit.MILLISECONDS,
      100
    )
  }
}
