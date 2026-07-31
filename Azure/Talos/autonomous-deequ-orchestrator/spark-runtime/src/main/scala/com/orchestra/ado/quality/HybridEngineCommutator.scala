package com.orchestra.ado.quality

import com.orchestra.ado.models.ElitePipelineContract
import org.slf4j.LoggerFactory

/**
 * Motor de Conmutación Dinámica Híbrida (Orchestra Data Labs)
 * Evalúa las firmas de telemetría de los contratos en microsegundos y decide la ruta óptima.
 */
object HybridEngineCommutator {
  private val logger = LoggerFactory.getLogger("ADO-HybridEngineCommutator")

  // Umbral empresarial crítico Tier-1: 50 MB expressed in bytes
  private val MAX_STREAMING_THRESHOLD_BYTES: Long = 50 * 1024 * 1024 

  /**
   * Analiza el contrato declarativo y conmuta el motor de ejecución en caliente.
   * Evita el desperdicio de recursos de clústeres Big Data para ráfagas ligeras.
   * 
   * @param contract El manifiesto de ingesta fuertemente tipado proveniente de Event Hubs o Pulsar.
   * @return El nombre del motor asignado de forma autónoma (SPARK o FLINK).
   */
  def resolveOptimalEngine(contract: ElitePipelineContract): String = {
    val dataset = contract.metadata.datasetName
    val tenantId = contract.metadata.tenantId
    val estimatedBytes = contract.metadata.estimatedBatchSizeBytes

    logger.info(s"🎛️ [CONMUTADOR-JVM] Evaluando telemetría para Tenant: $tenantId | Dataset: $dataset")
    logger.info(s"📊 [CONMUTADOR-JVM] Peso estimado del lote analítico: $estimatedBytes bytes (Umbral: $MAX_STREAMING_THRESHOLD_BYTES bytes)")

    val dynamicEngine = if (estimatedBytes > MAX_STREAMING_THRESHOLD_BYTES) {
      logger.info(s"🚀 [CONMUTADOR-SPARK] Volumen masivo detectado. Conmutando de forma transparente hacia Apache Spark Catalyst Native.")
      "SPARK"
    } else {
      logger.info(s"⚡ [CONMUTADOR-FLINK] Ráfaga ligera de alta frecuencia detectada. Delegando flujo al Stream Plane de Apache Flink.")
      "FLINK"
    }

    dynamicEngine
  }
}
