/*
================================================================================
MÓDULO:        modules/workflows/outputs.tf
DESCRIPCIÓN:   Exportación de variables de estado (Outputs) del orquestador.
               Permite que otros proyectos de Terraform lean las URLs de ejecución.
AUTOR:         Susana Edith Barrientos Galicia / Arquitectura Cloud
FECHA:         Julio 2026
================================================================================
*/

output "job_id" {
  value       = databricks_job.pipeline_rudo.id
  description = "ID único del Job generado por Databricks."
}

output "job_url" {
  value       = databricks_job.pipeline_rudo.url
  description = "Enlace directo URL de la consola de Databricks."
}