package com.orchestra.ado

import org.apache.spark.sql.{DataFrame, SaveMode}
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import java.util.UUID

/**
  * Caso de uso e interfaz inmutable global para las decisiones del almacenamiento autonomo por IA.
  */
case class StorageDecision(compressionCodec: String, partitionColumns: Seq[String], useBucketing: Boolean)

/**
  * ====================================================================================
  * 🎻 ORCHESTRA DATA LABS - ADUANA UNIVERSAL DE PERSISTENCIA TRANSACCIONAL (FASE 4 CORE)
  * ====================================================================================
  */
object GovernedSaveStrategy extends Serializable {

  def save(
      df: DataFrame,
      tenantId: String,
      datasetName: String,
      statusResult: String,
      targetPath: String,
      quarantinePath: String,
      decision: StorageDecision
  ): Unit = {
    
    val currentTimestamp = LocalDateTime.now()
    val yearStr = currentTimestamp.format(DateTimeFormatter.ofPattern("yyyy"))
    val monthStr = currentTimestamp.format(DateTimeFormatter.ofPattern("MM"))
    val dayStr = currentTimestamp.format(DateTimeFormatter.ofPattern("dd"))

    println(s"💾 [GOVERNED-SAVE] Inicializando ciclo de cierre ACID para el cliente: $tenantId")
    println(s"📊 [GOVERNED-SAVE] Estatus Analitico: $statusResult | Optimizador IA Codec: ${decision.compressionCodec.toUpperCase}")

    val enrichedDf = df
      .withColumn("tenant_id", org.apache.spark.sql.functions.lit(tenantId))
      .withColumn("ingest_year", org.apache.spark.sql.functions.lit(yearStr.toInt))
      .withColumn("ingest_month", org.apache.spark.sql.functions.lit(monthStr.toInt))
      .withColumn("ingest_day", org.apache.spark.sql.functions.lit(dayStr.toInt))
      .withColumn("orchestra_execution_uuid", org.apache.spark.sql.functions.lit(UUID.randomUUID().toString))

    val compactDf = if (decision.useBucketing) {
      println("⚡ [GOVERNED-SAVE] Alta Cardinalidad detectada. Aplicando repartition() por hash virtual.")
      enrichedDf.repartition(org.apache.spark.sql.functions.col("orchestra_execution_uuid"))
    } else {
      println("⚡ [GOVERNED-SAVE] Optimizando descriptores de archivos. Forzando coalesce(1) para archivo sano.")
      enrichedDf.coalesce(1)
    }

    val finalWritePath = if (statusResult.toUpperCase == "SUCCESS") {
      println(s"🟢 [ADUANA-PASSED] Lote limpio. Escribiendo de forma federada en Produccion: $targetPath")
      targetPath
    } else {
      println(s"🔴 [ADUANA-FAILED] Brecha de Calidad detectada. Desviando archivo a Cuarentena: $quarantinePath")
      quarantinePath
    }

    try {
      var writer = compactDf.write
        .mode(SaveMode.Append)
        .option("compression", decision.compressionCodec)
        .option("mergeSchema", "false")
        
      if (decision.partitionColumns.nonEmpty) {
        writer = writer.partitionBy(decision.partitionColumns: _*)
      }

      writer.save(finalWritePath)
      println(s"🏆 [GOVERNED-SAVE-SUCCESS] Escritos guardados con exito. Particionado: ${decision.partitionColumns.mkString("/")}")
      
    } catch {
      case ex: Exception =>
        println(s"🚨 [GOVERNED-SAVE-CRITICAL] Colapso de persistencia en la malla CloudChain: ${ex.getMessage}")
        throw ex
    }
  }
}
