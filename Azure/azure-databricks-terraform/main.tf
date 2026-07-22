/*
================================================================================
Archivo:       modules/databricks/main.tf
Descripción:   Máxima optimización corporativa: Triple Private Endpoint,
               aislamiento de DBFS y control perimetral total.
               CORRECCIÓN: Remoción de parámetro inválido en host y cambio de sufijo RG.
Autor:         Susana Edith Barrientos Galicia / Arquitectura Cloud
Fecha:         Julio 2026
================================================================================
*/

# ==============================================================================
# 1. INFRAESTRUCTURA DE RED BASE
# ==============================================================================
resource "azurerm_resource_group" "this" {
  name     = "rg-cloud-seguro-prod"
  location = "eastus2"
}

resource "azurerm_virtual_network" "this" {
  name                = "vnet-backend-prod-eastus2"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  address_space       = ["10.0.0.0/16"]
}

resource "azurerm_virtual_network" "jumpbox_vnet" {
  name                = "vnet-hub-access-eastus"
  location            = "eastus"
  resource_group_name = azurerm_resource_group.this.name
  address_space       = ["10.1.0.0/16"]
}

resource "azurerm_subnet" "public" {
  name                 = "snet-dbw-public"
  resource_group_name  = azurerm_resource_group.this.name
  virtual_network_name = azurerm_virtual_network.this.name
  address_prefixes     = ["10.0.1.0/24"]

  delegation {
    name = "databricks-delegation-public"
    service_delegation {
      name    = "Microsoft.Databricks/workspaces"
      actions = ["Microsoft.Network/virtualNetworks/subnets/join/action", "Microsoft.Network/virtualNetworks/subnets/prepareNetworkPolicies/action"]
    }
  }
}

resource "azurerm_subnet" "private" {
  name                 = "snet-dbw-private"
  resource_group_name  = azurerm_resource_group.this.name
  virtual_network_name = azurerm_virtual_network.this.name
  address_prefixes     = ["10.0.2.0/24"]

  delegation {
    name = "databricks-delegation-private"
    service_delegation {
      name    = "Microsoft.Databricks/workspaces"
      actions = ["Microsoft.Network/virtualNetworks/subnets/join/action", "Microsoft.Network/virtualNetworks/subnets/prepareNetworkPolicies/action"]
    }
  }
}

resource "azurerm_subnet" "endpoints" {
  name                 = "snet-private-links"
  resource_group_name  = azurerm_resource_group.this.name
  virtual_network_name = azurerm_virtual_network.this.name
  address_prefixes     = ["10.0.3.0/24"]
}

resource "azurerm_network_security_group" "db_nsg" {
  name                = "nsg-databricks-seguro"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
}

resource "azurerm_subnet_network_security_group_association" "public" {
  subnet_id                 = azurerm_subnet.public.id
  network_security_group_id = azurerm_network_security_group.db_nsg.id
}

resource "azurerm_subnet_network_security_group_association" "private" {
  subnet_id                 = azurerm_subnet.private.id
  network_security_group_id = azurerm_network_security_group.db_nsg.id
}

# ==============================================================================
# 2. ESPACIO DE TRABAJO DE DATABRICKS
# ==============================================================================
resource "azurerm_databricks_workspace" "this" {
  name                        = "dbw-secure-prod"
  resource_group_name         = azurerm_resource_group.this.name
  location                    = azurerm_resource_group.this.location
  sku                         = "premium"
  managed_resource_group_name = "dbw-secure-prod-managed-v2-rg"

  public_network_access_enabled         = true  
  network_security_group_rules_required = "AllRules" 
  customer_managed_key_enabled          = true

  custom_parameters {
    no_public_ip        = true 
    virtual_network_id  = azurerm_virtual_network.this.id
    public_subnet_name  = azurerm_subnet.public.name
    private_subnet_name = azurerm_subnet.private.name
    
    public_subnet_network_security_group_association_id  = azurerm_subnet_network_security_group_association.public.id
    private_subnet_network_security_group_association_id = azurerm_subnet_network_security_group_association.private.id
  }
}

# ==============================================================================
# 3. ARQUITECTURA DE PRIVATE ENDPOINTS (ÚNICOS, SIN REPETIR)
# ==============================================================================

# ENDPOINT PRINCIPAL: UI, APIs y canal de Datos unificado
resource "azurerm_private_endpoint" "ui_api" {
  name                = "pe-dbw-secure-prod-ui"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  subnet_id           = azurerm_subnet.endpoints.id

  private_service_connection {
    name                           = "databricks-ui-connection"
    private_connection_resource_id = azurerm_databricks_workspace.this.id
    is_manual_connection           = false
    subresource_names              = ["databricks_ui_api"] 
  }
}

# ENDPOINT COMPLEMENTARIO: Autenticación Web Aislada y SSO Nivel Portal
resource "azurerm_private_endpoint" "web_auth" {
  name                = "pe-dbw-secure-prod-auth"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  subnet_id           = azurerm_subnet.endpoints.id

  private_service_connection {
    name                           = "databricks-auth-connection"
    private_connection_resource_id = azurerm_databricks_workspace.this.id
    is_manual_connection           = false
    subresource_names              = ["browser_authentication"] 
  }
}

# ==============================================================================
# 4. RESOLUCIÓN DE NOMBRES (PRIVATE DNS ZONE)
# ==============================================================================
resource "azurerm_private_dns_zone" "databricks" {
  name                = "privatelink.azuredatabricks.net"
  resource_group_name = azurerm_resource_group.this.name
}

resource "azurerm_private_dns_zone_virtual_network_link" "this" {
  name                  = "db-dns-link"
  resource_group_name   = azurerm_resource_group.this.name
  private_dns_zone_name = azurerm_private_dns_zone.databricks.name
  virtual_network_id    = azurerm_virtual_network.this.id
}

resource "azurerm_private_dns_zone_virtual_network_link" "access" {
  name                  = "db-dns-link-access"
  resource_group_name   = azurerm_resource_group.this.name
  private_dns_zone_name = azurerm_private_dns_zone.databricks.name
  virtual_network_id    = azurerm_virtual_network.jumpbox_vnet.id
}

# ==============================================================================
# 5. REGISTROS DNS TIPO A (SOLO DOS COMPONENTES)
# ==============================================================================
resource "azurerm_private_dns_a_record" "this" {
  name                = "dbw-secure-prod"
  zone_name           = azurerm_private_dns_zone.databricks.name
  resource_group_name = azurerm_resource_group.this.name
  ttl                 = 3600
  records             = [azurerm_private_endpoint.ui_api.private_service_connection[0].private_ip_address]
}

resource "azurerm_private_dns_a_record" "auth" {
  name                = "dbw-secure-prod-auth"
  zone_name           = azurerm_private_dns_zone.databricks.name
  resource_group_name = azurerm_resource_group.this.name
  ttl                 = 3600
  records             = [azurerm_private_endpoint.web_auth.private_service_connection[0].private_ip_address]
}

# ==============================================================================
# 6. SECCIÓN ADICIONADA: ORQUESTACIÓN DE SPARK DIRECTA (WORKFLOW MEDIO RUDO)
# ==============================================================================
resource "databricks_job" "pipeline_rudo" {
  name = "wf-analytics-ventas-rudo-prod"

  email_notifications {
    on_failure = ["correo"]
  }

  # TAREA 1: Ingesta (Bronze Layer)
  task {
    task_key = "ingesta_bronze"

    new_cluster {
      spark_version = "14.3.x-scala2.12"
      node_type_id  = "Standard_D4ds_v5"
      num_workers   = 2
      spark_conf = {
        "spark.databricks.delta.preview.enabled" = "true"
        "spark.sql.shuffle.partitions"           = "auto"
      }
    }

    notebook_task {
      notebook_path = "/Production/Pipelines/01_Ingest_Bronze"
    }
  }

  # TAREA 2: Limpieza (Silver Layer)
  task {
    task_key = "transformacion_silver"
    depends_on {
      task_key = "ingesta_bronze"
    }

    new_cluster {
      spark_version = "14.3.x-scala2.12"
      node_type_id  = "Standard_D4ds_v5"
      num_workers   = 2
      spark_conf = {
        "spark.databricks.delta.preview.enabled" = "true"
        "spark.sql.shuffle.partitions"           = "auto"
      }
    }

    notebook_task {
      notebook_path = "/Production/Pipelines/02_Clean_Silver"
    }
  }

  # TAREA 3: Métricas (Gold Layer)
  task {
    task_key = "agregacion_gold"
    depends_on {
      task_key = "transformacion_silver"
    }

    new_cluster {
      spark_version = "14.3.x-scala2.12"
      node_type_id  = "Standard_D4ds_v5"
      num_workers   = 2
      spark_conf = {
        "spark.databricks.delta.preview.enabled" = "true"
        "spark.sql.shuffle.partitions"           = "auto"
      }
    }

    notebook_task {
      notebook_path = "/Production/Pipelines/03_Metrics_Gold"
    }
  }

  schedule {
    quartz_cron_expression = "0 0 2 * * ?"
    timezone_id            = "America/Mexico_City"
  }

  tags = {
    Layer       = "Orchestration"
    DataProduct = "Commercial-Intelligence"
    Developer   = "Susana Edith Barrientos Galicia"
  }
}