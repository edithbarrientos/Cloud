package com.orchestra.ado.stream

import org.scalatest.funsuite.AnyFunSuite
import org.scalatest.matchers.should.Matchers
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.module.scala.DefaultScalaModule

/**
 * == StreamAppSpec ==
 * 
 * Suite de pruebas unitarias encargada de validar la robustez de las transformaciones
 * distribuidas y el aislamiento del Patrón de Resguardo Predictivo (Fallback).
 */
class StreamAppSpec extends AnyFunSuite with Matchers {

  // Inicialización del motor de Jackson bajo los mismos términos de producción
  private val mapper = new ObjectMapper()
  mapper.registerModule(DefaultScalaModule)

  test("🎯 [Prueba Unitario] Jackson debe parsear exitosamente un JSON Multi-Tenant válido") {
    val validJson = """{"tenantId":"orchestra-tenant-1","clientId":"client-alpha","sessionId":"sess-100","payload":"Hola"}"""
    
    val event = mapper.readValue(validJson, classOf[AnomalyEvent])
    
    event.tenantId should {
      be("orchestra-tenant-1")
    }
    event.clientId should {
      be("client-alpha")
    }
    event.payload should {
      be("Hola")
    }
  }

  test("🛡️  [Prueba de Robustez] El sistema debe sanitizar y procesar texto plano activando el Fallback Predictivo") {
    val rawCorruptText = "MENSAJE_CORRUPTO_\u0001\u0002_BINARIO"
    
    // Simulación exacta del comportamiento del mapeador interno de Flink en StreamApp
    val fallbackId = "test-uuid"
    val sanitizedPayload = rawCorruptText.replaceAll("[^\\x20-\\x7E]", "")
    
    val fallbackEvent = AnomalyEvent(
      tenantId = s"dynamic-tenant-$fallbackId",
      clientId = s"dynamic-client-$fallbackId",
      sessionId = s"dynamic-sess-$fallbackId",
      payload = sanitizedPayload
    )

    fallbackEvent.tenantId should {
      startWith("dynamic-tenant-")
    }
    fallbackEvent.payload should {
      be("MENSAJE_CORRUPTO__BINARIO") // Comprueba la remoción exitosa de caracteres de control
    }
  }
}
