package com.orchestra.ado.custom

import akka.http.scaladsl.model._
import akka.http.scaladsl.testkit.ScalatestRouteTest
import com.orchestra.ado.models.DataContract
import org.scalatest.matchers.should.Matchers
import org.scalatest.wordspec.AnyWordSpec
import org.slf4j.LoggerFactory
import upickle.default._

/**
 * === Custom API Mock Specification ===
 * Suite de pruebas perimetral encargada de auditar la lógica del validador personalizado
 * mediante el uso de inyecciones sintéticas (Mocks) sin requerir hilos de red físicos.
 */
class CustomApiSpec extends AnyWordSpec with Matchers with ScalatestRouteTest {

  private val logger = LoggerFactory.getLogger(this.getClass)
  private val testRoute = CustomApiApp.route

  "Tu API Personalizada (Custom Validation Endpoint)" should {

    "aprobar con éxito y dictaminar un mensaje de chat corporativo legítimo" in {
      // 1. Fabricar el Mock del contrato inmutable del Módulo 1 (DAMA Compliance)
      val mockContract = DataContract(
        id = "mock-msg-uuid-001",
        tenantId = "enterprise-tenant-omega",
        sessionId = "session-token-active-123",
        payload = "Requiero procesar la conciliación de esquemas en la malla.",
        timestamp = System.currentTimeMillis(),
        estimatedTokens = 12,
        charCount = 55
      )

      val jsonPayload = write(mockContract)

      // 2. Disparar una petición POST simulada inyectando las cabeceras de telemetría requeridas
      Post("/v1/validate-chat", jsonPayload) ~> 
        addHeader("X-Tenant-ID", mockContract.tenantId) ~> 
        testRoute ~> check {
          
          // 3. Auditar el estatus HTTP y el cuerpo de respuesta deserializado
          status shouldBe StatusCodes.OK
          contentType shouldBe ContentTypes.`application/json`
          
          val responseStr = responseAs[String]
          logger.info(s"🟢 [MOCK TEST PASSED] API Response: $responseStr")
          
          responseStr should include("APPROVED")
          responseStr should include(mockContract.id)
      }
    }

    "detectar y marcar de manera correcta una anomalía si el payload contiene palabras clave prohibidas" in {
      val mockAnomalyContract = DataContract(
        id = "mock-msg-uuid-002",
        tenantId = "enterprise-tenant-omega",
        sessionId = "session-token-active-123",
        payload = "CRITICAL ERROR: OutOfMemoryException detected in task slot.",
        timestamp = System.currentTimeMillis(),
        estimatedTokens = 10,
        charCount = 59
      )

      val jsonPayload = write(mockAnomalyContract)

      Post("/v1/validate-chat", jsonPayload) ~> 
        addHeader("X-Tenant-ID", mockAnomalyContract.tenantId) ~> 
        testRoute ~> check {
          
          status shouldBe StatusCodes.OK
          val responseStr = responseAs[String]
          logger.warn(s"⚠️ [MOCK TEST ANOMALY DETECTED] API Response: $responseStr")
          
          // Verificar que tu regla personalizada de negocio conmute el veredicto analítico
          responseStr should include("ANOMALY_DETECTED")
          responseStr should include(mockAnomalyContract.id)
      }
    }

    "rechazar la transacción con un código HTTP 400 Bad Request si el JSON de entrada está corrupto" in {
      val jsonCorruptoBypass = "{ malformed_json: true, "

      Post("/v1/validate-chat", jsonCorruptoBypass) ~> 
        addHeader("X-Tenant-ID", "hacked-tenant") ~> 
        testRoute ~> check {
          
          // Certificar el short-circuit reactivo ante bytes malformados
          status shouldBe StatusCodes.BadRequest
          responseAs[String] should include("MALFORMED_JSON")
          logger.info("🔒 [MOCK TEST SHORT-CIRCUIT] Payload malformado bloqueado con éxito.")
      }
    }
  }
}
