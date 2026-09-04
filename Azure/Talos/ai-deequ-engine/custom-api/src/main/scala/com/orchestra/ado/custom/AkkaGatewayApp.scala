package com.orchestra.ado.custom

import akka.actor.ActorSystem
import akka.http.scaladsl.Http
import akka.http.scaladsl.model._
import akka.http.scaladsl.server.Directives._
import akka.stream.Materializer
import com.typesafe.config.{Config, ConfigFactory}
import org.slf4j.LoggerFactory
import org.apache.pulsar.client.api.{PulsarClient, Producer}
import scala.concurrent.ExecutionContextExecutor
import scala.util.{Success, Failure, Try}

object AkkaGatewayApp {
  def main(args: Array[String]): Unit = {
    val config: Config = ConfigFactory.load()
    val interface: String = config.getString("server.interface")
    val port: Int         = config.getInt("server.port")
    val pulsarUrl: String = config.getString("pulsar.broker-url")
    val topicName: String = config.getString("pulsar.topic-name")

    implicit val system: ActorSystem = ActorSystem("AkkaGateway-System")
    implicit val materializer: Materializer = Materializer(system)
    implicit val executionContext: ExecutionContextExecutor = system.dispatcher

    val log = LoggerFactory.getLogger(getClass)
    log.info(s"🔀 [Gateway-Bootstrap] Iniciando AkkaGatewayApp en [$interface:$port]")

    val pulsarClient = PulsarClient.builder().serviceUrl(pulsarUrl).build()
    val producer: Producer[Array[Byte]] = pulsarClient.newProducer()
      .topic(topicName)
      .blockIfQueueFull(true)
      .create()

    sys.addShutdownHook {
      log.warn("⚠️  [Gateway-Shutdown] Interceptando SIGTERM. Cerrando descriptores...")
      Try(producer.close())
      Try(pulsarClient.close())
      system.terminate()
    }

    val route =
      path("v1" / "chatbot" / "ingest") {
        post {
          headerValueByName("X-Tenant-ID") { tenantId =>
            entity(as[Array[Byte]]) { rawJsonBytes =>
              val distributionResult = Try(producer.send(rawJsonBytes).toString)

              distributionResult match {
                case Success(pulsarMsgId) =>
                  val decodedExtract = new String(rawJsonBytes, "UTF-8").replaceAll("[^\\x20-\\x7E]", " ").take(60)
                  log.info(s"📥 [Gateway Akka Ingest] Evento asimilado. Tenant: [$tenantId] | MsgID: [$pulsarMsgId] | Snippet: [$decodedExtract...]")
                  complete(HttpResponse(StatusCodes.Accepted, entity = HttpEntity(ContentTypes.`application/json`, s"""{"status":"ACCEPTED","message":"Inyectado con éxito. MsgID: $pulsarMsgId"}""")))
                case Failure(ex) =>
                  log.error(s"💥 [Gateway Akka Error] Falla en Pulsar: ${ex.getMessage}")
                  complete(HttpResponse(StatusCodes.InternalServerError, entity = HttpEntity(ContentTypes.`application/json`, s"""{"status":"REJECTED","reason":"${ex.getMessage}"}""")))
              }
            }
          }
        }
      }

    val bindingFuture = Http().newServerAt(interface, port).bind(route)
    bindingFuture.onComplete {
      case Success(binding) => log.info(s"🪐 [Gateway-Bootstrap] Servidor Akka HTTP enlazado en http://${binding.localAddress.getHostString}:${binding.localAddress.getPort}/")
      case Failure(ex) => log.error(s"🚨 [Gateway-Catastrophic] Fallo al amarrar puerto: ${ex.getMessage}"); producer.close(); pulsarClient.close(); system.terminate()
    }
  }
}
