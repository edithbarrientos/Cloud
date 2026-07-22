/*
================================================================================
Archivo:       providers.tf
Descripción:   Configuración global de Terraform, requerimientos de proveedores
               (AzureRM, Databricks y HTTP) con autenticación federada y segura
               para mitigar colisiones de identidades (Tuta/Microsoft).
Autor:         Susana Edith Barrientos Galicia / Arquitectura Cloud
Fecha:         Julio 2026
================================================================================
*/

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.0"
    }
    # ADICIÓN DE SEGURIDAD: Requerimiento del proveedor HTTP para descubrir tu IP pública
    http = {
      source  = "hashicorp/http"
      version = "~> 3.0"
    }
  }
}

# Inicialización del proveedor nativo de Azure
provider "azurerm" {
  features {}
}

# Inicialización del proveedor HTTP de automatización perimetral
provider "http" {}

# MEJORA DE SEGURIDAD: Autenticación nativa y aislada de Databricks
# Rompe la dependencia del navegador web inyectando directamente el host del espacio de trabajo
provider "databricks" {
  # CORRECCIÓN DE REFERENCIA: Se cambia '.databricks.id' por '.this.id' para alinearse con el main.tf
  azure_workspace_resource_id = azurerm_databricks_workspace.this.id
}