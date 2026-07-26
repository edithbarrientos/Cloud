# ==============================================================================
# ARCHIVO:        infrastructure/variables.tf
# DESCRIPCIÓN:    Definición de variables globales para parametrizar el entorno
#                 sin necesidad de alterar el código base de Terraform.
# AUTOR:          Edith BG
# FECHA:          2026-07-24
# VERSIÓN:        1.0.0
# ==============================================================================

variable "location" {
  type        = string
  description = "Región de Azure donde se desplegarán los recursos."
  default     = "eastus2"
}

variable "ambiente" {
  type        = string
  description = "Ambiente de despliegue actual (dev, qa, prod)."
  default     = "prod"
}