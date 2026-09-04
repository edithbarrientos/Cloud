package com.orchestra.ado.gateway

import akka.actor.ActorSystem
import akka.http.scaladsl.Http
import akka.http.scaladsl.model._
import akka.http.scaladsl.server.Directives._
import org.apache.pulsar.client.api.{PulsarClient, Schema}
import org.slf4j.LoggerFactory
import scala.concurrent.ExecutionContext
import scala.util.{Success, Failure}
import java.net.InetAddress

object AkkaGatewayApp {
  private val logger = LoggerFactory.getLogger(this.getClass)

  def main(args: Array[String]): Unit = {
    implicit val system: ActorSystem = ActorSystem("Gateway-System")
    implicit val executionContext: ExecutionContext = system.dispatcher

    logger.info("📡 [GATEWAY-INICIO] Resolviendo DNS local del Pod de Pulsar de forma dinámica...")
    
    // 🚀 MEJORA DE RESILIENCIA ABSOLUTA EN EL GATEWAY:
    // Intentamos resolver el host corto. Si CoreDNS falla, inyectamos el salvavidas IP real.
    val pulsarIp = try {
      InetAddress.getByName("pulsar-standalone-broker").getHostAddress
    } catch {
      case ex: Exception =>
        logger.warn(s"⚠️ [DNS-LOCAL-WARN] Falla de CoreDNS: ${ex.getMessage}. Activando salvavidas IP real: 10.42.0.2")
        "10.42.0.2"
    }

    logger.info(s"🔌 [GATEWAY-PULSAR] Conectando de forma rígida a la IP: $pulsarIp. Abriendo canales...")

    val pulsarClient = PulsarClient.builder()
      .serviceUrl(s"pulsar://$pulsarIp:6650")
      .build()

    val bytesProducer = pulsarClient.newProducer(Schema.BYTES)
      .topic("persistent://public/default/chat-messages-raw")
      .enableBatching(false) // Deshabilitamos batching para inmediatez extrema
      .blockIfQueueFull(true)
      .create()

    val firewall = new SemanticAiFirewall(bytesProducer)

    val route =
      path("v1" / "ingest") {
        post {
          headerValueByName("X-Tenant-ID") { tenantId =>
            entity(as[String]) { jsonBody =>
              logger.info(s"📥 [GATEWAY] Payload recibido para inyección elástica - Tenant: $tenantId")
              
              onComplete(firewall.inspectMessage(jsonBody, tenantId)) {
                case Success(isValid) if isValid =>
                  complete(HttpEntity(ContentTypes.`application/json`, """{"status":"ACCEPTED_AND_FIRED"}"""))
                case Success(_) =>
                  complete(StatusCodes.BadRequest, HttpEntity(ContentTypes.`application/json`, """{"status":"REJECTED_BY_AI_GUARDRAIL"}"""))
                case Failure(ex) =>
                  logger.error(s"❌ [GATEWAY-FALLO] Error en la malla: ${ex.getMessage}")
                  complete(StatusCodes.InternalServerError, HttpEntity(ContentTypes.`application/json`, s"""{"status":"ERROR","reason":"${ex.getMessage}"}"""))
              }
            }
          }
        }
      }

    val interface = "0.0.0.0"
    val port = 50051

    Http().newServerAt(interface, port).bind(route)
    logger.info(s"🚀 Ingress Gateway activo en http://$interface:$port/v1/ingest")
  }
}
