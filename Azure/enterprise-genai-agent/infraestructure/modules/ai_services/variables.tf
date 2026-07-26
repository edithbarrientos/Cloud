# ==============================================================================
# ARCHIVO:        infrastructure/modules/ai_services/variables.tf
# DESCRIPCIÓN:    Definición de variables de entrada para el submódulo de IA.
# AUTOR:          Edith BG
# FECHA:          2026-07-26
# VERSIÓN:        1.2.0
# ESTADO:         Enterprise Ready / Clean Modular Architecture (Mapped Models)
# ==============================================================================

# ==============================================================================
# 1. MAPA DE CONFIGURACIÓN DEL MODELO CORE (ESTRUCTURA DE FLUJO FLEXIBLE)
# ==============================================================================
variable "primary_model" {
  type = object({
    name     = string
    version  = string
    sku      = string
    capacity = number
  })
  default = {
    name     = "gpt-4o-mini"     # <-- SOLUCIÓN INMEDIATA: Modelo rápido abierto en todas las suscripciones
    version  = "2024-07-18"      # Versión GA universal activa
    sku      = "DataZoneStandard" # Mantiene el bypass de red exitoso de tu cuenta v3
    capacity = 10               
  }
}

# ==============================================================================
# 2. VARIABLES DE HERENCIA PERIMETRAL (CONTRATOS OBLIGATORIOS DESDE LA RAÍZ)
# ==============================================================================
variable "location" {
  type        = string
  description = "Región de Azure (ej: eastus2) heredada del RG raíz."
}

variable "resource_group_name" {
  type        = string
  description = "Nombre del Grupo de Recursos contenedor."
}

variable "ambiente" {
  type        = string
  description = "Entorno de despliegue actual (dev, qa, prod)."
}