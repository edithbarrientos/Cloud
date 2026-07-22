/*
================================================================================
Archivo:       variables.tf (Raíz)
Descripción:   Definición exclusiva de variables globales con valores por defecto 
               para automatizar el despliegue y mitigar bloqueos interactivos.
================================================================================
*/

variable "workspace_name" {
  type        = string
  description = "Nombre del workspace de Databricks"
  default     = "dbw-secure-prod"
}

variable "resource_group_name" {
  type        = string
  description = "Nombre del grupo de recursos"
  default     = "rg-cloud-seguro-prod"
}

variable "location" {
  type        = string
  description = "Región de Azure"
  default     = "eastus2"
}

variable "vnet_id" {
  type        = string
  description = "ID de la VNet principal"
  default     = "vnet-backend-prod-eastus2"
}

variable "public_subnet_name" {
  type        = string
  description = "Nombre de la subnet pública"
  default     = "snet-dbw-public"
}

variable "private_subnet_name" {
  type        = string
  description = "Nombre de la subnet privada"
  default     = "snet-dbw-private"
}

variable "endpoint_subnet_id" {
  type        = string
  description = "ID de la subnet de endpoints"
  default     = "snet-private-links"
}

variable "public_subnet_nsg_association_id" {
  type        = string
  description = "ID de asociación NSG pública"
  default     = "nsg-link-public"
}

variable "private_subnet_nsg_association_id" {
  type        = string
  description = "ID de asociación NSG privada"
  default     = "nsg-link-private"
}

variable "access_vnet_id" {
  type        = string
  description = "ID de la VNet de acceso secundaria para el puente DNS"
  default     = "vnet-hub-access-eastus"
}

variable "tags" {
  type        = map(string)
  description = "Etiquetas obligatorias de auditoría y cumplimiento de seguridad"
  default     = {
    Environment = "Production"
    ManagedBy   = "Terraform"
    Security    = "Strict-Aisle"
  }
}
