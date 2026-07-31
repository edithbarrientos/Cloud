package com.orchestra.ado.persistence

import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions.{current_timestamp, lit, year, month, dayofmonth}
import java.util.UUID

object MetadataWriter {

  /**
    * Asienta el rendimiento analítico de Deequ en las tres tablas DAMA Delta Lake centrales.
    */
  def writeGovernanceMetadata(
    spark: SparkSession,
    datasetName: String,
    alertLevel: String,
    targetPath: String,
    govMetadataPath: String,
    quarantinePath: String,
    statusResult: String
  ): Unit = {
    import spark.implicits._

    val executionId = UUID.randomUUID().toString
    val contractId = UUID.nameUUIDFromBytes(datasetName.getBytes).toString
    println(s"📝 [METADATA-WRITE] Registrando ejecución DAMA '$executionId' para el contrato '$contractId'...")

    // 1. Insertar fila en la Tabla de Catálogo Central (data_contracts_catalogue)
    val catalogueDf = Seq((contractId, datasetName, "1.0.0", "Finance_Team", "Auditoría Financiera Automatizada", alertLevel))
      .toDF("contract_id", "dataset_name", "version", "data_owner", "business_kpi_target", "alert_level")
      .withColumn("registered_at", current_timestamp())

    catalogueDf.write
      .mode("append")
      .format("delta")
      .save(s"$govMetadataPath/data_contracts_catalogue")

    // 2. Insertar fila en la Tabla Histórica de Métricas (data_quality_metrics_history)
    val ratio = if (statusResult == "Success") 1.0 else 0.0
    val metricsDf = Seq((executionId, contractId, "Completitud", "transaction_id", 1.0, ratio, statusResult))
      .toDF("execution_id", "contract_id", "dama_dimension", "column_name", "passing_threshold", "actual_ratio", "status")
      .withColumn("execution_time", current_timestamp())
      .withColumn("exec_year", year(current_timestamp()))
      .withColumn("exec_month", month(current_timestamp()))
      .withColumn("exec_day", dayofmonth(current_timestamp()))

    metricsDf.write
      .mode("append")
      .format("delta")
      .partitionBy("exec_year", "exec_month", "exec_day")
      .save(s"$govMetadataPath/data_quality_metrics_history")

    // 3. Si el lote falla, asentar el Incidente de Cuarentena (governance_quarantine_log)
    if (statusResult != "Success") {
      println(s"🔒 [METADATA-QUARANTINE] Registrando alerta de desvío físico en la bitácora Delta...")
      val incidentId = UUID.randomUUID().toString
      val quarantineDf = Seq((incidentId, executionId, quarantinePath, "PENDING", "SYSTEM_ALERT", "Lote corrupto desviado de forma automática por Deequ"))
        .toDF("incident_id", "execution_id", "quarantine_path", "status", "reviewed_by", "justification")
        .withColumn("resolved_at", current_timestamp())

      quarantineDf.write
        .mode("append")
        .format("delta")
        .save(s"$govMetadataPath/governance_quarantine_log")
    }
  }
}
