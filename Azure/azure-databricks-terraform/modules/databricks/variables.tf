/*
================================================================================
Archivo:       variables.tf (Raíz)
Descripción:   Definición exclusiva de variables globales con URIs completas
               de Azure para mitigar errores de parsing en los segmentos de red.
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

# ==============================================================================
# CORRECCIÓN DE SEGMENTOS: IDs oficiales y largos de Azure (Sustituye por tu UUID de suscripción real)
# ==============================================================================

variable "vnet_id" {
  type        = string
  description = "URI larga oficial de la Red Virtual principal de Azure"
  default     = "/subscriptions/92f8b9d3-e52d-4f27-9ec4-f1720263567c/resourceGroups/rg-cloud-seguro-prod/providers/Microsoft.Network/virtualNetworks/vnet-backend-prod-eastus2"
}

variable "access_vnet_id" {
  type        = string
  description = "URI larga oficial de la Red Virtual de acceso (Jumpbox)"
  default     = "/subscriptions/92f8b9d3-e52d-4f27-9ec4-f1720263567c/resourceGroups/rg-cloud-seguro-prod/providers/Microsoft.Network/virtualNetworks/vnet-hub-access-eastus"
}

variable "endpoint_subnet_id" {
  type        = string
  description = "URI larga oficial de la subred para Private Endpoints"
  default     = "/subscriptions/92f8b9d3-e52d-4f27-9ec4-f1720263567c/resourceGroups/rg-cloud-seguro-prod/providers/Microsoft.Network/virtualNetworks/vnet-backend-prod-eastus2/subnets/snet-private-links"
}

variable "public_subnet_nsg_association_id" {
  type        = string
  description = "URI larga oficial de la asociación NSG pública"
  default     = "/subscriptions/92f8b9d3-e52d-4f27-9ec4-f1720263567c/resourceGroups/rg-cloud-seguro-prod/providers/Microsoft.Network/virtualNetworks/vnet-backend-prod-eastus2/subnets/snet-dbw-public"
}

variable "private_subnet_nsg_association_id" {
  type        = string
  description = "URI larga oficial de la asociación NSG privada"
  default     = "/subscriptions/92f8b9d3-e52d-4f27-9ec4-f1720263567c/resourceGroups/rg-cloud-seguro-prod/providers/Microsoft.Network/virtualNetworks/vnet-backend-prod-eastus2/subnets/snet-dbw-private"
}

# ==============================================================================
# PARÁMETROS TEXTUALES (SE QUEDAN COMO NOMBRES CORTOS)
# ==============================================================================

variable "public_subnet_name" {
  type        = string
  description = "Nombre simple de la subnet pública"
  default     = "snet-dbw-public"
}

variable "private_subnet_name" {
  type        = string
  description = "Nombre simple de la subnet privada"
  default     = "snet-dbw-private"
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
Usa el código con precaución.Ejecución de Control finalAl guardar estas rutas largas en tu archivo de variables, Azure podrá leer los 8 segmentos correspondientes de forma nativa sin generar problemas de URI. Corre los comandos para aplicar la solución:bashterraform validate
terraform apply -lock=false
Usa el código con precaución.¿El proceso de terraform apply logró pasar el análisis de red y comenzó a crear tu espacio de trabajo de forma exitosa?