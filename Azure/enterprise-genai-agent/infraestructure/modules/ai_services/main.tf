# ==============================================================================
# ARCHIVO:        infrastructure/modules/ai_services/main.tf
# DESCRIPCIÓN:    Aprovisionamiento del servicio cognitivo de Inteligencia Artificial.
# AUTOR:          Edith BG
# FECHA:          2026-07-26
# VERSIÓN:        2.1.0
# ESTADO:         Enterprise Ready / Full Global Architecture Bypass
# ==============================================================================

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 3.100, < 5.0"
    }
  }
}

# ==============================================================================
# 3. CUENTA COGNITIVA GLOBAL ÚNICA (AZURE OPENAI)
# ==============================================================================
# Se cambia el nombre del recurso de "openai" a "openai_global" para desvincular 
# el estado antiguo regional y forzar una cuenta limpia.
resource "azurerm_cognitive_account" "openai_global" {
  name                = "cog-openai-audit-prod-v3" # Nombre físico v3 para evitar la caché de reciclaje de Azure
  location            = "eastus2"                  # Región concentradora para enrutamiento global
  resource_group_name = var.resource_group_name
  kind                = "OpenAI"
  sku_name            = "S0"
}

# ==============================================================================
# 4. DESPLIEGUE DEL MODELO CORE LLM VIGENTE (SOPORTE DE SLOT LIMPIO V4)
# ==============================================================================
resource "azurerm_cognitive_deployment" "gpt5_nano" {
  # Mantenemos el nombre físico del despliegue en Azure para no alterar las variables de la API
  name                 = "gpt-5-nano-deployment" 
  cognitive_account_id = azurerm_cognitive_account.openai_global.id
  
  model {
    format  = "OpenAI"
    name    = var.primary_model.name    
    version = var.primary_model.version 
  }
  
  sku {
    name     = var.primary_model.sku      
    capacity = var.primary_model.capacity
  }
}

# ==============================================================================
# 5. CONTRATOS DE SALIDA (OUTPUTS INTERNOS)
# ==============================================================================
output "openai_endpoint" { 
  value       = azurerm_cognitive_account.openai_global.endpoint 
}

output "openai_primary_key" { 
  value     = azurerm_cognitive_account.openai_global.primary_access_key 
  sensitive = true
}