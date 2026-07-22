/*
================================================================================
Archivo:       modules/network/outputs.tf
Descripción:   Define las salidas (outputs) del módulo de red. Expone las IDs
               y nombres de la VNet, subnets y asociaciones NSG para que puedan 
               ser consumidas por el módulo de Azure Databricks.
Autor:         Susana Edith Barrientos Galicia / Arquitectura Cloud
Fecha:         Julio 2026
================================================================================
*/

output "vnet_id" {
  value       = azurerm_virtual_network.this.id
  description = "El identificador único (ID de recurso de Azure) de la Red Virtual (VNet) creada."
}

output "public_subnet_id" {
  value       = azurerm_subnet.public.id
  description = "El identificador único (ID) de la subnet pública (Host) delegada a Databricks."
}

output "private_subnet_id" {
  value       = azurerm_subnet.private.id
  description = "El identificador único (ID) de la subnet privada (Container) delegada a Databricks."
}

output "endpoint_subnet_id" {
  value       = azurerm_subnet.endpoints.id
  description = "El identificador único (ID) de la subnet destinada al despliegue de Private Endpoints."
}

output "public_subnet_name" {
  value       = azurerm_subnet.public.name
  description = "El nombre plano de la subnet pública (Host). Requerido por los parámetros personalizados del workspace."
}

output "private_subnet_name" {
  value       = azurerm_subnet.private.name
  description = "El nombre plano de la subnet privada (Container). Requerido por los parámetros personalizados del workspace."
}

output "public_subnet_nsg_association_id" {
  value       = azurerm_subnet_network_security_group_association.public.id
  description = "ID de la asociación del Network Security Group (NSG) con la subnet pública."
}

output "private_subnet_nsg_association_id" {
  value       = azurerm_subnet_network_security_group_association.private.id
  description = "ID de la asociación del Network Security Group (NSG) con la subnet privada."
}