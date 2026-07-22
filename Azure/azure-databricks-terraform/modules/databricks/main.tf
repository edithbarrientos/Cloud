/*
================================================================================
Archivo:       main.tf (Raíz)
Descripción:   Arquitectura base de conectividad de red y llamada unificada al
               módulo seguro de Azure Databricks.
Autor:         Susana Edith Barrientos Galicia / Arquitectura Cloud
Fecha:         Julio 2026
================================================================================
*/

# ==============================================================================
# 1. GRUPO DE RECURSOS PRINCIPAL
# ==============================================================================
resource "azurerm_resource_group" "this" {
  name     = var.resource_group_name
  location = var.location
}

# ==============================================================================
# 2. REDES VIRTUALES (VNET PRINCIPAL Y ACCESO HÍBRIDO)
# ==============================================================================
resource "azurerm_virtual_network" "this" {
  name                = var.vnet_id
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  address_space       = ["10.0.0.0/16"]
}

# VNet Secundaria para cumplir con el puente DNS (Jumpbox / Tránsito)
resource "azurerm_virtual_network" "jumpbox_vnet" {
  name                = var.access_vnet_id
  location            = "eastus"
  resource_group_name = azurerm_resource_group.this.name
  address_space       = ["10.1.0.0/16"]
}

# ==============================================================================
# 3. SUBREDES REQUERIDAS PARA LA INYECCIÓN DE DATABRICKS
# ==============================================================================

# Subred Pública (Host)
resource "azurerm_subnet" "public" {
  name                 = var.public_subnet_name
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

# Subred Privada (Container)
resource "azurerm_subnet" "private" {
  name                 = var.private_subnet_name
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

# Subred Dedicada a los Private Endpoints
resource "azurerm_subnet" "endpoints" {
  name                 = var.endpoint_subnet_id
  resource_group_name  = azurerm_resource_group.this.name
  virtual_network_name = azurerm_virtual_network.this.name
  address_prefixes     = ["10.0.3.0/24"]
}

# ==============================================================================
# 4. SEGURIDAD PERIMETRAL (NSG Y ASOCIACIONES OBLIGATORIAS)
# ==============================================================================
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
# 5. LLAMADA INTEGRADA AL MÓDULO SEGURO
# ==============================================================================
module "databricks" {
  source = "./modules/databricks"

  workspace_name      = var.workspace_name
  resource_group_name = azurerm_resource_group.this.name
  location            = azurerm_resource_group.this.location

  vnet_id            = azurerm_virtual_network.this.id
  public_subnet_id   = azurerm_subnet.public.id
  private_subnet_id  = azurerm_subnet.private.id
  endpoint_subnet_id = azurerm_subnet.endpoints.id

  public_subnet_name  = azurerm_subnet.public.name
  private_subnet_name = azurerm_subnet.private.name

  public_subnet_nsg_association_id  = azurerm_subnet_network_security_group_association.public.id
  private_subnet_nsg_association_id = azurerm_subnet_network_security_group_association.private.id

  access_vnet_id = azurerm_virtual_network.jumpbox_vnet.id
  tags           = var.tags
}