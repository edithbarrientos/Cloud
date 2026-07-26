# ==============================================================================
# ARCHIVO:        infrastructure/main.tf
# DESCRIPCIÓN:    Orquestador principal unificado bajo la rama azurerm v4.x
# AUTOR:          Edith BG
# FECHA:          2026-07-26
# ==============================================================================

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 4.0.0" 
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = "rg-enterprise-genai-prod"
  location = "swedencentral"
}

resource "azurerm_container_registry" "acr" {
  name                = "acrgenaiaudit92f8b9"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Standard"
  admin_enabled       = true
}

module "monitoreo" {
  source              = "./modules/monitoring"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  ambiente            = "prod"
}

module "ia_v2" {
  source              = "./modules/ai_services"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  ambiente            = "prod"
}

resource "azurerm_container_app_environment" "this" {
  name                       = "cae-enterprise-genai-prod-env"
  resource_group_name        = azurerm_resource_group.rg.name
  location                   = azurerm_resource_group.rg.location
  log_analytics_workspace_id = module.monitoreo.log_analytics_workspace_id

  lifecycle {
    ignore_changes = [log_analytics_workspace_id]
  }
}

resource "azurerm_container_app" "agent_api" {
  name                         = "ca-genai-audit-api-prod-v3"
  resource_group_name          = azurerm_resource_group.rg.name
  container_app_environment_id = azurerm_container_app_environment.this.id
  revision_mode                = "Single"

  registry {
    server               = azurerm_container_registry.acr.login_server
    username             = azurerm_container_registry.acr.admin_username
    password_secret_name = "acr-password"
  }

  secret {
    name  = "acr-password"
    value = azurerm_container_registry.acr.admin_password
  }

  secret {
    name  = "appinsights-cs"
    value = "appi-genai-audit-prod-connection-string"
  }

  secret {
    name  = "openai-key"
    value = module.ia_v2.openai_primary_key
  }

  ingress {
    external_enabled = true
    target_port      = 8080
    transport        = "auto"
    
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  template {
    container {
      name   = "enterprise-genai-agent"
      image  = "${azurerm_container_registry.acr.login_server}/enterprise-genai-agent:1.0.3"
      cpu    = "0.5"
      memory = "1.0Gi"

      env {
        name        = "APPLICATIONINSIGHTS_CONNECTION_STRING"
        secret_name = "appinsights-cs"
      }
      env {
        name  = "AZURE_OPENAI_ENDPOINT"
        value = trimsuffix(module.ia_v2.openai_endpoint, "/")
      }
      env {
        name  = "AZURE_OPENAI_DEPLOYMENT_NAME"
        value = "gpt-4o-final-deployment" 
      }
      env {
        name        = "AZURE_OPENAI_API_KEY"
        secret_name = "openai-key"
      }
      env {
        name  = "ERP_API_URL"
        value = "https://internal.net"
      }
      env {
        name  = "ERP_AUTH_TOKEN"
        value = "dummy-token"
      }
    }
  }
}

output "api_public_url" {
  value       = try(azurerm_container_app.agent_api.ingress[0].fqdn, null)
  description = "URL pública de la API del agente o null si el Ingress está deshabilitado."
}