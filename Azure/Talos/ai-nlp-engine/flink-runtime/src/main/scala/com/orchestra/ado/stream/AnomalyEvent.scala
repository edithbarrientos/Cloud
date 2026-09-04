package com.orchestra.ado.stream

/**
  * Modelo de Transferencia de Datos de Alta Fidelidad (Enterprise DTO / Case Class).
  * 
  * Define el contrato inmutable rígido de 12 campos que unifica el linaje analítico 
  * de extremo a extremo. Este objeto es asimilado por el motor de Apache Flink tras desempacar
  * las tramas JSON entrantes de Apache Pulsar y funciona como la estructura de negocio canónica
  * antes de la serialización binaria comprimida hacia el pipeline de Google Protobuf v3.
  * 
  * Al ser una case class, implementa por defecto los métodos copy, equals, hashCode y 
  * pattern matching, garantizando un rendimiento óptimo de los descriptores de sockets 
  * en el clúster transaccional sin efectos secundarios (*pure functional state*).
  * 
  * @param tenantId      Identificador único e inmutable del inquilino corporativo (Multi-Tenant ID).
  * @param clientId      Identificador del cliente final registrado bajo la cuenta del inquilino.
  * @param customerId    ID único del usuario o cliente final que interactúa de forma viva con el Chatbot.
  * @param sessionId     UUID persistente encargado de indexar y correlacionar la sesión activa del chat.
  * @param messageId     Identificador inmutable único global del mensaje procesado en la factoría de red.
  * @param timestamp     Estampa de tiempo transaccional indexada bajo el estándar de red ISO-8601.
  * @param source        Canal o plataforma omnicanal de origen del tráfico (ej. WhatsApp, Twilio, WebChat).
  * @param message       Texto depurado en lenguaje natural plano sanitizado enviado de forma real por el usuario.
  * @param rawMessage    Carga de datos original cruda (*raw payload*) antes del desempaquetado perimetral.
  * @param issueCategory Categoría taxonómica inicial o intención preliminar reportada por el Gateway perimetral.
  * @param summary       Resumen analítico ejecutivo o título resumido del ticket de atención generado.
  * @param attachment    Flag, metadato o ruta física de archivos adjuntos asociados a la interacción.
  * 
  * @author Enterprise Architecture Team
  * @version 4.0.0
  */
case class AnomalyEvent(
  tenantId: String,
  clientId: String,
  customerId: String,
  sessionId: String,
  messageId: String,
  timestamp: String,
  source: String,
  message: String,
  rawMessage: String,
  issueCategory: String,
  summary: String,
  attachment: String
) extends Serializable