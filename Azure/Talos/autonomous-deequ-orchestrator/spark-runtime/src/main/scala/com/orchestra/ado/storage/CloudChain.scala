package com.orchestra.ado.storage

import org.apache.spark.sql.{DataFrame, SparkSession}
import com.orchestra.ado.models.ElitePipelineContract
import org.slf4j.LoggerFactory

/**
 * Patrón Fábrica de Conectores Pluggable Multi-Cloud (Orchestra Data Labs)
 * Abstrae y unifica la persistencia y lectura atómica sobre almacenamiento de objetos [DAMA].
 */
object CloudChain {
  private val logger = LoggerFactory.getLogger("ADO-CloudChain")

  /**
   * Carga un lote analítico en memoria RAM distributiva desde cualquier nube de forma agnóstica.
   */
  def loadDataFrame(spark: SparkSession, contract: ElitePipelineContract): DataFrame = {
    val provider = contract.executionEngine // Mapeado dinámicamente o por metadatos
    val inputPath = contract.metadata.targetPath // Ruta genérica de abstracción
    
    logger.info(s"🔌 [CLOUD-CHAIN] Abstrayendo lectura elástica para el proveedor: ${contract.executionEngine}")
    
    provider.toUpperCase match {
      case "AWS" =>
        logger.info(s"📦 [AWS-S3A] Cargando set de datos desde Amazon S3: $inputPath")
        spark.read.format("parquet").load(inputPath)
        
      case "AZURE" =>
        logger.info(s"📦 [AZURE-ABFSS] Cargando set de datos desde ADLS Gen2: $inputPath")
        spark.read.format("delta").load(inputPath)
        
      case "GCP" =>
        logger.info(s"📦 [GCP-GS] Cargando set de datos desde Google Cloud Storage: $inputPath")
        spark.read.format("parquet").load(inputPath)
        
      case unknown =>
        throw new IllegalArgumentException(s"🚨 [CLOUD-CHAIN-ERROR] Proveedor de almacenamiento '$unknown' no soportado.")
    }
  }

  /**
   * Persiste el DataFrame limpio aplicando los códecs predictivos calculados por la IA.
   * Resuelve el particionamiento transaccional por tenant_id de forma nativa.
   */
  def persistDataFrame(df: DataFrame, contract: ElitePipelineContract, optimalCodec: String): Unit = {
    val provider = contract.executionEngine
    val targetPath = contract.metadata.targetPath
    val tenantId = contract.metadata.tenantId

    logger.info(s"📤 [CLOUD-CHAIN] Despachando persistencia multi-nube con códec predictivo L1: ${optimalCodec.toUpperCase}")

    // Configuración elástica del particionamiento estructural y compresión en la RAM de Spark
    val writer = df.write
      .mode("append")
      .option("compression", optimalCodec)
      .partitionBy("tenant_id") // Blindaje físico Multi-Tenant mandatorio

    provider.toUpperCase match {
      case "AWS" =>
        logger.info(s"💾 [AWS-S3A] Escribiendo Delta Lake inmutable en S3: $targetPath/tenant_id=$tenantId")
        writer.format("delta").save(targetPath)

      case "AZURE" =>
        logger.info(s"💾 [AZURE-ABFSS] Escribiendo Parquet optimizado en Azure ADLS Gen2: $targetPath/tenant_id=$tenantId")
        writer.format("parquet").save(targetPath)

      case "GCP" =>
        logger.info(s"💾 [GCP-GS] Escribiendo Parquet optimizado en Google Cloud Storage: $targetPath/tenant_id=$tenantId")
        writer.format("parquet").save(targetPath)

      case unknown =>
        throw new IllegalArgumentException(s"🚨 [CLOUD-CHAIN-ERROR] Imposible persistir. Proveedor '$unknown' inválido.")
    }
  }
}
