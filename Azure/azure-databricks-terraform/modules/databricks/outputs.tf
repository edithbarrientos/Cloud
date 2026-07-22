/*
================================================================================
Archivo:       modules/databricks/outputs.tf
Descripción:   Define las salidas (outputs) del módulo de Azure Databricks.
               Expone los datos del espacio de trabajo necesarios tanto para el
               proveedor de Databricks en la raíz como para el equipo de DevOps.
Autor:         Susana Edith Barrientos Galicia/ Arquitectura Cloud
Fecha:         Julio 2026
================================================================================
*/

output "workspace_url" {
  value       = azurerm_databricks_workspace.this.workspace_url
  description = "La URL de administración segura del espacio de trabajo de Databricks (ej: adb-xxx.azuredatabricks.net). Se utiliza para inicializar dinámicamente el proveedor de Databricks."
}

output "workspace_id" {
  value       = azurerm_databricks_workspace.this.workspace_id
  description = "El ID de recurso único asignado por Azure al espacio de trabajo de Databricks. Útil para automatizaciones avanzadas y políticas de gobernanza."
}