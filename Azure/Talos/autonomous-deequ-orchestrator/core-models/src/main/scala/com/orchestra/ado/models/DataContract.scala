package com.orchestra.ado.models

import upickle.default.{ReadWriter, macroRW}

// ====================================================================================
// 🏛️ ESQUEMAS DECLARATIVOS ESTRICTOS (DAMA-DMBOK2 STANDARD)
// ====================================================================================

case class FieldDefinition(
  name: String,
  `type`: String,
  pii: Boolean = false
)
object FieldDefinition {
  implicit val rw: ReadWriter[FieldDefinition] = macroRW
}

case class SchemaContract(
  version: String,
  fields: Seq[FieldDefinition]
)
object SchemaContract {
  implicit val rw: ReadWriter[SchemaContract] = macroRW
}

case class QualityExpectation(
  damaDimension: String,
  rule: String,
  columns: Seq[String],
  passingThreshold: Double = 1.0
)
object QualityExpectation {
  implicit val rw: ReadWriter[QualityExpectation] = macroRW
}

// ====================================================================================
// 🧠 METADATOS COMPLEMENTARIOS PARA LA CAPA DE INFERENCIA DE IA Y CONMUTACIÓN
// ====================================================================================

case class AdaptiveMetadata(
  datasetName: String,
  dataOwner: String,
  businessKpiTarget: String,
  targetPath: String,
  quarantinePath: String,
  governanceMetadataPath: String,
  checkpointPath: Option[String] = None,
  triggerTime: String = "10 seconds",
  estimatedBatchSizeBytes: Long = 0L,
  tenantId: String = "shared",
  executionId: String = ""
)
object AdaptiveMetadata {
  implicit val rw: ReadWriter[AdaptiveMetadata] = macroRW
}

// ====================================================================================
// 👑 MANIFIESTO MAESTRO DE INGESTA (CONTRATO UNIFICADO ADO)
// ====================================================================================

case class ElitePipelineContract(
  executionEngine: String,
  executionMode: String,
  alertLevel: String = "Error",
  schemaContract: SchemaContract,
  qualityExpectations: Seq[QualityExpectation],
  genaiSemanticValidationColumn: Option[String] = None,
  metadata: AdaptiveMetadata
)
object ElitePipelineContract {
  implicit val rw: ReadWriter[ElitePipelineContract] = macroRW
}
