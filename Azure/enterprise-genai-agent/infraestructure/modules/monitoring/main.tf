# ==============================================================================
# ARCHIVO:        infrastructure/modules/monitoring/main.tf
# DESCRIPCIÓN:    Aprovisionamiento de los sistemas de observabilidad.
# AUTOR:          Edith BG
# FECHA:          2026-07-26
# VERSIÓN:        1.0.0
# ==============================================================================

variable "location" { type = string }
variable "resource_group_name" { type = string }
variable "ambiente" { type = string }

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 4.0.0" 
    }
  }
}

resource "azurerm_log_analytics_workspace" "this" {
  name                = "log-genai-audit-prod"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "PerGB2018"
}

resource "azurerm_application_insights" "this" {
  name                = "appi-genai-audit-prod"
  location            = var.location
  resource_group_name = var.resource_group_name
  workspace_id        = azurerm_log_analytics_workspace.this.id
  application_type    = "web"
}

output "log_analytics_workspace_id" {
  value = azurerm_log_analytics_workspace.this.id
}