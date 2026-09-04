package com.orchestra.ado.gateway

import org.slf4j.LoggerFactory
import scala.concurrent.{ExecutionContext, Future, Promise}
import java.util.regex.Pattern
import org.apache.pulsar.client.api.{Producer, MessageId}
import java.util.UUID
import com.orchestra.ado.gateway.grpc.ChatMessageRequest

class SemanticAiFirewall(producer: Producer[Array[Byte]])(implicit ec: ExecutionContext) {
  private val logger = LoggerFactory.getLogger(this.getClass)

  private val obfuscationPattern = Pattern.compile("[\\_\\-\\*\\/\\|\\p{Punct}]")
  private val whitespacePattern = Pattern.compile("\\s+")

  private val aiGuardrailTokens = Set(
    "ignore previous", "system override", "bypass rules", 
    "sudo", "dan mode", "developer mode", "jailbreak",
    "act as", "you are now", "new instructions"
  )

  def inspectMessage(payload: String, tenantId: String): Future[Boolean] = {
    val safeTenant = Option(tenantId).map(_.trim).getOrElse("")
    val safePayload = Option(payload).map(_.trim).getOrElse("")

    if (safeTenant.isEmpty) {
      logger.error("🚨 [VIOLACIÓN DE SEGURIDAD IA]: Intento de acceso perimetral bloqueado: Falta X-Tenant-ID.")
      Future.successful(false)
    } else if (safePayload.isEmpty) {
      logger.warn(s"⚠️ [ANOMALÍA RECHAZADA]: Intento de envío de payload de chat vacío por el Tenant: $safeTenant")
      Future.successful(false)
    } else {
      val textCleaned = obfuscationPattern.matcher(safePayload.toLowerCase).replaceAll("")
      val textNormalized = whitespacePattern.matcher(textCleaned).replaceAll(" ").trim

      val guardrailTriggered = aiGuardrailTokens.exists(token => textNormalized.contains(token))

      if (guardrailTriggered) {
        logger.error(s"🔒 [AI GUARDRAIL DETECTADO]: Intento de Prompt Injection bloqueado en el Tenant: $safeTenant.")
        Future.successful(false)
      } else {
        logger.info(s"🔒 [AI GUARDRAIL VERDE]: Contexto cognitivo aprobado de forma segura para el Tenant: $safeTenant")

        val promise = Promise[Boolean]()

        try {
          val sesionDinamica = s"sess-${UUID.randomUUID().toString.take(8)}"

          // 🚀 MEJORA DE ASIGNACIÓN EXPLÍCITA DE SCALAPB:
          // Mapeamos los campos por nombre de propiedad exacto mediante el patrón Builder.
          // Esto rompe la inversión del constructor posicional de una vez por todas.
          val protobufMessage = ChatMessageRequest.defaultInstance
            .withTenantId(safeTenant)
            .withSessionId(sesionDinamica)
            .withMessagePayload(safePayload)

          val rawProtobufBytes = protobufMessage.toByteArray

          producer.newMessage()
            .value(rawProtobufBytes)
            .sendAsync()
            .thenAccept(new java.util.function.Consumer[MessageId] {
              override def accept(msgId: MessageId): Unit = {
                logger.info(s"🔥 [GATEWAY-ÉXITO] Protobuf inyectado de forma explícita. Tenant: $safeTenant")
                promise.success(true)
              }
            }).exceptionally(new java.util.function.Function[Throwable, Void] {
              override def apply(err: Throwable): Void = {
                logger.error(s"❌ [ERROR GATEWAY] Falló el despacho de red: ${err.getMessage}")
                promise.success(true)
                null
              }
            })

        } catch {
          case ex: Exception =>
            logger.error(s"❌ [ERROR PERÍMETRO] Falla en empaquetado Protobuf: ${ex.getMessage}")
            promise.success(true)
        }

        promise.future
      }
    }
  }
}
