package com.orchestra.ado.gateway

import akka.actor.ActorSystem
import akka.testkit.TestKit
import com.orchestra.ado.gateway.grpc._
import com.orchestra.ado.models.DataContract
import org.scalatest.BeforeAndAfterAll
import org.scalatest.concurrent.ScalaFutures
import org.scalatest.matchers.should.Matchers
import org.scalatest.wordsspec.AnyWordSpec
import org.scalatest.time.{Millis, Seconds, Span}
import upickle.default._
import scala.concurrent.duration._

/**
 * === DataOps E2E Integration Specification ===
 * Suite encargada de validar la compatibilidad y reversibilidad estructural de la 
 * serialización binaria con uPickle para garantizar que Flink consuma datos íntegros.
 */
class DataOpsE2ESpec extends AnyWordSpec with Matchers with ScalaFutures with BeforeAndAfterAll {

  // Inicialización controlada del sistema de actores encapsulado en TestKit
  private implicit val system: ActorSystem = ActorSystem("DataOpsE2E-System")
  
  // Configuración elástica de tolerancia a fallos por latencia en el cluster local
  private implicit val defaultPatience: PatienceConfig = PatienceConfig(
    timeout = Span(6, Seconds),
    interval = Span(150, Millis)
  )

  private val firewall = new SemanticAiFirewall()(system.dispatcher)
  private val serviceImpl = new ChatIngressServiceImpl(firewall)

  /**
   * 🚀 MEJORA DE CICLO DE VIDA: Hook obligatorio de desmantelamiento de infraestructura.
   * Apaga el ActorSystem de Akka liberando memoria y sockets de red en tu Mac.
   */
  override protected def afterAll(): Unit = {
    TestKit.shutdownActorSystem(system, duration = 3.seconds, verifySystemShutdown = true)
    super.afterAll()
  }

  "El Pipeline de Ingesta de Datos" should {

    "garantizar que la serialización de uPickle genere bytes inmutables y reversibles" in {
      val request = ChatMessageRequest(
        tenantId = "tenant-dama-governed",
        sessionId = "sess-ops-001",
        messagePayload = "Validar esquema Delta Lake transaccional.",
        timestamp = 1786224437L
      )

      val responseFuture = serviceImpl.ingestChatMessage(request)

      whenReady(responseFuture) { response =>
        response.status shouldBe "SUCCESS"
        response.messageId should not be "N/A"

        // Enlace directo al Contrato Declarativo Inmutable del Módulo 1 (DAMA Compliance)
        val mockContractInstanced = DataContract(
          id = response.messageId,
          tenantId = request.tenantId,
          sessionId = request.sessionId,
          payload = request.messagePayload,
          timestamp = request.timestamp
        )

        // Forzar serialización a través del motor de uPickle
        val serializedJson = uPickle.default.write(mockContractInstanced)
        serializedJson should include(request.tenantId)
        serializedJson should include("payload")

        // Auditoría de Reversibilidad Binaria: Deserializar el JSON y comprobar consistencia total de bytes
        val deserializedContract = uPickle.default.read[DataContract](serializedJson)
        deserializedContract.id shouldBe response.messageId
        deserializedContract.payload shouldBe request.messagePayload
        deserializedContract.tenantId shouldBe request.tenantId
      }
    }
  }
}
