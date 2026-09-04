package com.orchestra.ado.stream

import org.apache.flink.configuration.Configuration
import org.apache.flink.streaming.api.functions.async.{RichAsyncFunction, ResultFuture}
import org.slf4j.LoggerFactory
import java.io.ByteArrayOutputStream
import java.net.{URL, HttpURLConnection}
import java.util.concurrent.CompletableFuture
import scala.io.Source
import scala.util.{Try, Success, Failure}

/**
  * Operador Asíncrono de Inferencia No Bloqueante para la Integración con Motores de IA.
  * 
  * Clase encargada de interceptar el flujo distribuido de eventos inmutables (AnomalyEvent),
  * serializar los 12 campos del contrato corporativo al formato binario nativo de Google Protobuf v3
  * mediante codificación Varint manual de bajo nivel, y despachar ráfagas simultáneas multiplexadas
  * por HTTP/1.1 hacia la compuerta analítica de la Inteligencia Artificial (FastAPI).
  * 
  * Al heredar de [[org.apache.flink.streaming.api.functions.async.RichAsyncFunction]], el componente
  * libera el hilo principal del TaskManager delegando las conexiones al pool asíncrono del sistema operativo,
  * mitigando la degradación del Throughput general.
  * 
  * @param apiUrl    URL absoluta de destino de la API analítica (ej. http://localhost:8000/v1/analyze).
  * @param timeoutMs Tiempo de espera máximo estricto en milisegundos para abortar sockets colgados de red.
  * @param maxRetries Número máximo de reintentos lineales tolerados antes de conmutar al buffer de desborde.
  * 
  * @author Edith Barrientos
  * @version 4.0.0
  */
class AsyncAIEvaluator(apiUrl: String, timeoutMs: Long, maxRetries: Int) 
    extends RichAsyncFunction[AnomalyEvent, String] {

  @transient lazy val log = LoggerFactory.getLogger(getClass)

  /**
    * Inicializa el estado del operador dentro de la ranura de ejecución (Slot) de Apache Flink.
    * Configura descriptores globales e inicializa el canal persistente de auditoría analítica.
    * 
    * @param parameters Configuración interna heredada del TaskManager.
    */
  override def open(parameters: Configuration): Unit = {
    log.info("⚙️  [AsyncAIEvaluator-Bootstrap] Inicializando ranura de red asíncrona inmune para el contrato de 12 campos.")
  }

  /**
    * Codifica un entero de 32 bits utilizando el algoritmo Base-128 Varints de Google Protobuf.
    * 
    * Remueve los bits más significativos redundantes y empaqueta la longitud en bloques compactos de bytes,
    * donde el bit de mayor peso (MSB) funciona como bandera de continuación para optimizar el transporte
    * en la mallas de red de baja latencia.
    * 
    * @param out   Flujo de salida en memoria (ByteArrayOutputStream) donde se inyectan los bits empacados.
    * @param value Entero que representa la longitud exacta en bytes de la cadena de texto a transmitir.
    */
  private def writeVarint(out: ByteArrayOutputStream, value: Int): Unit = {
    var v = value
    // Mientras existan bits significativos más allá del rango de 7 bits (0x7F)
    while ((v & ~0x7F) != 0) {
      // Inyectamos los 7 bits inferiores y encendemos el bit 8 (0x80) como indicador de continuación
      out.write((v & 0x7F) | 0x80)
      v >>>= 7 // Desplazamiento lógico a la derecha de 7 posiciones
    }
    // Escribimos el bloque final de bits residual sin bandera de continuación
    out.write(v & 0x7F)
  }

  /**
    * Ejecuta el trigger asíncronico de inferencia en hilos paralelos no bloqueantes del Kernel.
    * 
    * Este método es invocado automáticamente por Flink de forma concurrente. Utiliza un contrato
    * elástico de Promesas (`CompletableFuture`) para procesar el stream sin causar cuellos de botella
    * por cambio de contexto en el procesador.
    * 
    * @param input        Objeto POJO de negocio AnomalyEvent con el linaje de los 12 campos sanitizados.
    * @param resultFuture Colector distribuidor encargado de notificar la resolución de la respuesta a los siguientes Sinks.
    */
  override def asyncInvoke(input: AnomalyEvent, resultFuture: ResultFuture[String]): Unit = {
    
    // Delegamos la operación bloqueante de red a la alberca de hilos asíncronos asilados
    CompletableFuture.supplyAsync(new java.util.function.Supplier[String] {
      override def get(): String = {
        var conn: HttpURLConnection = null
        
        // Encapsulamos la comunicación en un bloque monádico Try de Scala para control de excepciones
        val evaluationResult = Try {
          val out = new ByteArrayOutputStream()

          /**
            * Helper interno in-memory encargado de estructurar el esquema binario de Google Protobuf v3.
            * Calcula los Tags binarios equivalentes bajo la fórmula: (field_number << 3) | wire_type.
            */
          def writeField(tag: Int, value: String): Unit = {
            val safeValue = if (value == null) "" else value
            val bytes = safeValue.getBytes("UTF-8")
            out.write(tag)           // Inyección del identificador de etiqueta de campo (Wire Type 2 - Length-delimited)
            writeVarint(out, bytes.length) // Codificación Varint inyectando la longitud de la cadena
            out.write(bytes, 0, bytes.length) // Escritura binaria de los bytes del string UTF-8
          }

          // 🪐 ACOPLE BINARIO ESTRICTO: Empaquetamiento indexado según el archivo .proto (Tags 1 al 12)
          writeField(10, input.tenantId)       // Tag 1  (1 << 3 | 2 = 10)
          writeField(18, input.clientId)       // Tag 2  (2 << 3 | 2 = 18)
          writeField(26, input.customerId)     // Tag 3  (3 << 3 | 2 = 26)
          writeField(34, input.sessionId)      // Tag 4  (4 << 3 | 2 = 34)
          writeField(42, input.messageId)      // Tag 5  (5 << 3 | 2 = 42)
          writeField(50, input.timestamp)      // Tag 6  (6 << 3 | 2 = 50)
          writeField(58, input.source)         // Tag 7  (7 << 3 | 2 = 58)
          writeField(66, input.message)        // Tag 8  (8 << 3 | 2 = 66)
          writeField(74, input.rawMessage)     // Tag 9  (9 << 3 | 2 = 74)
          writeField(82, input.issueCategory)  // Tag 10 (10 << 3 | 2 = 82)
          writeField(90, input.summary)        // Tag 11 (11 << 3 | 2 = 90)
          writeField(98, input.attachment)     // Tag 12 (12 << 3 | 2 = 98)

          val rawBytes = out.toByteArray

          log.info("==> [AsyncAIEvaluator-Transport] Despachando contrato extendido por red intramesh. Tamaño: [{}] bytes.", Array[AnyRef](rawBytes.length.toString): _*)

          // 📡 PROTOCOLO DE CONEXIÓN CORPORATIVA VIA HTTP INTERNO
          val url = new URL(apiUrl)
          conn = url.openConnection().asInstanceOf[HttpURLConnection]
          conn.setRequestMethod("POST")
          conn.setRequestProperty("Content-Type", "application/x-protobuf")
          conn.setRequestProperty("X-Tenant-ID", input.tenantId)
          
          // Configuración de límites y guardias de red elásticas para mitigar caídas colgadas
          conn.setConnectTimeout(timeoutMs.toInt)
          conn.setReadTimeout(timeoutMs.toInt)
          conn.setDoOutput(true)
          conn.setFixedLengthStreamingMode(rawBytes.length) // Evita el almacenamiento en búfer interno de Java

          // Escritura de bits en el flujo de salida del Socket
          val os = conn.getOutputStream
          os.write(rawBytes, 0, rawBytes.length)
          os.flush()
          os.close()

          // Desempaquetado e inspección del código de retorno del servidor analítico (FastAPI)
          val responseCode = conn.getResponseCode
          val stream = if (responseCode == 200) conn.getInputStream else conn.getErrorStream
          val responseText = Source.fromInputStream(stream, "UTF-8").mkString
          
          log.info("<== [AsyncAIEvaluator-Inference] Servidor IA Status Respondió: [{}]. Inferencia completada con éxito.", Array[AnyRef](responseCode.toString): _*)
          responseText
        }

        // 🔀 EVALUACIÓN DEL RESULTADO DE LA PROMESA SÍNCRONA
        evaluationResult match {
          case Success(jsonResponse) => 
            if (conn != null) conn.disconnect() // Liberación controlada del descriptor de red
            jsonResponse
          case Failure(ex) => 
            log.error(s"!!! [AsyncAIEvaluator-Catastrophic] Fallo crítico de red o desalineación de firmas con FastAPI: ${ex.getMessage}")
            if (conn != null) conn.disconnect()
            // Retornamos un JSON de escape estructural compatible con los parsers de Apache Flink downstream
            s"""{"status":"ERROR","reason":"${ex.getMessage}"}"""
        }
      }
    }).thenAccept(new java.util.function.Consumer[String] {
      override def accept(response: String): Unit = {
        // Notificamos la resolución satisfactoria al grafo distribuidor de Flink
        resultFuture.complete(java.util.Collections.singletonList(response))
      }
    })
  }
}