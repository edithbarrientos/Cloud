package com.orchestra.ado.stream

import org.apache.flink.configuration.Configuration
import org.apache.flink.streaming.api.functions.async.{RichAsyncFunction, ResultFuture}
import org.slf4j.LoggerFactory
import java.io.ByteArrayOutputStream
import java.net.{URL, HttpURLConnection}
import java.util.concurrent.CompletableFuture
import scala.io.Source

class AsyncAIEvaluator(apiUrl: String, timeoutMs: Long, maxRetries: Int) 
    extends RichAsyncFunction[AnomalyEvent, String] {

  @transient lazy val log = LoggerFactory.getLogger(getClass)

  override def open(parameters: Configuration): Unit = {}
  override def close(): Unit = {}

  /**
   * Escribe un entero en formato Varint de Base 128 requerido por la especificación de Protobuf
   */
  private def writeVarint(out: ByteArrayOutputStream, value: Int): Unit = {
    var v = value
    while ((v & ~0x7F) != 0) {
      out.write((v & 0x7F) | 0x80)
      v >>>= 7
    }
    out.write(v & 0x7F)
  }

  override def asyncInvoke(input: AnomalyEvent, resultFuture: ResultFuture[String]): Unit = {
    
    CompletableFuture.supplyAsync(new java.util.function.Supplier[String] {
      override def get(): String = {
        var conn: HttpURLConnection = null
        try {
          val dynamicTenant  = input.tenantId
          val dynamicSession = input.sessionId
          val cleanPayload   = input.payload
          
          log.info("==> [AsyncAIEvaluator] Enviando -> Tenant: [{}], Session: [{}]", Array[AnyRef](dynamicTenant, dynamicSession): _*)
          
          val tenantBytes  = dynamicTenant.getBytes("UTF-8")
          val sessionBytes = dynamicSession.getBytes("UTF-8")
          val payloadBytes = cleanPayload.getBytes("UTF-8")

          val out = new ByteArrayOutputStream()
          
          // Tag 1 (10) -> tenant_id (Escribiendo Tag + Longitud en Varint legítimo)
          out.write(10)
          writeVarint(out, tenantBytes.length)
          out.write(tenantBytes, 0, tenantBytes.length)
          
          // Tag 2 (18) -> session_id (Escribiendo Tag + Longitud en Varint legítimo)
          out.write(18)
          writeVarint(out, sessionBytes.length)
          out.write(sessionBytes, 0, sessionBytes.length)
          
          // Tag 3 (26) -> message_payload (Escribiendo Tag + Longitud en Varint legítimo)
          out.write(26)
          writeVarint(out, payloadBytes.length)
          out.write(payloadBytes, 0, payloadBytes.length)
          
          val rawBytes = out.toByteArray

          val url = new URL(apiUrl)
          conn = url.openConnection().asInstanceOf[HttpURLConnection]
          conn.setRequestMethod("POST")
          conn.setRequestProperty("Content-Type", "application/x-protobuf")
          conn.setRequestProperty("X-Tenant-ID", dynamicTenant) 
          
          conn.setConnectTimeout(timeoutMs.toInt)
          conn.setReadTimeout(timeoutMs.toInt)
          conn.setDoOutput(true)

          conn.setFixedLengthStreamingMode(rawBytes.length)

          val os = conn.getOutputStream
          os.write(rawBytes, 0, rawBytes.length)
          os.flush()
          os.close()

          val responseCode = conn.getResponseCode
          val stream = if (responseCode == 200) conn.getInputStream else conn.getErrorStream
          val responseText = Source.fromInputStream(stream, "UTF-8").mkString
          
          log.info("<== [AsyncAIEvaluator] API Status [{}]. Respuesta: {}", Array[AnyRef](responseCode.toString, responseText): _*)
          
          responseText
        } catch {
          case ex: Exception => 
            log.error(s"!!! [AsyncAIEvaluator] Error: ${ex.getMessage}", ex)
            s"""{"status":"ERROR","reason":"${ex.getMessage}"}"""
        } finally {
          if (conn != null) conn.disconnect()
        }
      }
    }).thenAccept(new java.util.function.Consumer[String] {
      override def accept(response: String): Unit = {
        resultFuture.complete(java.util.Collections.singletonList(response))
      }
    })
  }
}
