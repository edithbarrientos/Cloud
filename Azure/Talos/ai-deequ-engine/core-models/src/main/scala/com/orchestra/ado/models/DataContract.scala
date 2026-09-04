package com.orchestra.ado.models

import upickle.default.{ReadWriter, macroRW}

/**
 * === DAMA Governance DataContract ====================================================================================
 * Representación inmutable y tipada que unifica el esquema estructural de los mensajes de chat enriquecidos.
 * Incorpora variables métricas analíticas de IA consumidas por Akka, Flink y los algoritmos de Amazon Deequ.
 * =====================================================================================================================
 *
 * @param id             Identificador único global (UUID) asignado perimetralmente al mensaje.
 * @param tenantId       Identificador inmutable de aislamiento de datos corporativos (X-Tenant-ID).
 * @param sessionId      Identificador de la sesión activa del canal de conversación de IA.
 * @param payload        Contenido textual o string plano enviado por el usuario en la interfaz.
 * @param timestamp      Marca de tiempo estricta de la ingesta en milisegundos Unix.
 * @param estimatedTokens Estimación matemática perimetral del volumen de tokens consumidos por el string plano.
 * @param charCount      Cantidad absoluta de caracteres físicos presentes en el mensaje de chat (Métrica base de Deequ).
 */
case class DataContract(
  id: String,
  tenantId: String,
  sessionId: String,
  payload: String,
  timestamp: Long,
  estimatedTokens: Int,
  charCount: Int
)

object DataContract {
  implicit val rw: ReadWriter[DataContract] = macroRW

  /**
   * 🚀 ALGORITMO COMPLEMENTARIO DE IA: Estimador elástico de tokens perimetral.
   * Utiliza la constante de densidad lingüística (4 caracteres por token promedio) para calcular de forma lineal 
   * el peso cognitivo del texto plano de chat sin generar sobrecarga ni latencia en los hilos de Akka.
   *
   * @param text String plano extraído de la petición del chat.
   * @return Cantidad entera estimada de tokens reflejada en el metadato del contrato.
   */
  def estimateTokens(text: String): Int = {
    Option(text).map(_.trim) match {
      case Some(t) if t.isEmpty => 0
      case Some(t) =>
        val chars = t.length
        // Algoritmo base: Techo matemático de dividir caracteres entre el ratio de compresión estándar
        Math.ceil(chars.toDouble / 4.0).toInt
      case None => 0
    }
  }
}

/**
 * === Quality Metrics Stamp ===========================================================================================
 * Estructura declarativa utilizada para el timbrado y persistencia de los resultados de calidad
 * calculados por el motor de Amazon Deequ sobre los tópicos distribuidos.
 * =====================================================================================================================
 */
case class QualityStamp(
  messageId: String,
  tenantId: String,
  ruleName: String,
  status: String,
  value: Double
)

object QualityStamp {
  implicit val rw: ReadWriter[QualityStamp] = macroRW
}
