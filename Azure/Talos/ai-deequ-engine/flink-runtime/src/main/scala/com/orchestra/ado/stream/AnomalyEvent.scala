package com.orchestra.ado.stream

/**
 * Entidad de dominio que representa un evento de anomalía tipado dentro del dataflow de Flink.
 * 
 * Este caso de clase (Case Class) actúa como un Objeto de Transferencia de Datos (DTO) 
 * intermedio para eliminar el uso de buffers de bytes crudos (`Array[Byte]`) entre operadores, 
 * permitiendo una manipulación limpia y fuertemente tipada de las variables de negocio.
 *
 * @param tenantId  Identificador único del inquilino (Tenant) que originó el evento.
 * @param sessionId Identificador de la sesión activa del flujo analítico.
 * @param payload   Contenido textual o JSON crudo de la anomalía que será evaluado por la IA.
 */
case class AnomalyEvent(
    tenantId: String,
    sessionId: String,
    payload: String
)
