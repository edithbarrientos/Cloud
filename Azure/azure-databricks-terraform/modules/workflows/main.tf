/*
================================================================================
MÓDULO:        modules/workflows/main.tf
DESCRIPCIÓN:   Motor de orquestación y aprovisionamiento nativo de Databricks Jobs.
               Implementa una arquitectura Medallón (Bronze-Silver-Gold)
               mediante el uso de clústeres eficientes de Spark (Job Clusters).
AUTOR:         Susana Edith Barrientos Galicia / Arquitectura Cloud
FECHA:         Julio 2026
================================================================================
*/

# ==============================================================================
# CONFIGURACIÓN LOCAL (PLANTILLA DE CÓMPUTO SPARK)
# ==============================================================================
locals {
  job_cluster_config = {
    spark_version = "14.3.x-scala2.12" # Versión LTS con Spark 3.5+ y Delta Lake integrado.
    node_type_id  = "Standard_D4ds_v5" # Instancias de Azure con discos NVMe para Shuffling veloz.
    num_workers   = 2                  # Nodos trabajadores asignados para el paralelismo de tareas.
    
    spark_conf = {
      "spark.databricks.delta.preview.enabled" = "true" 
      "spark.sql.shuffle.partitions"           = "auto" 
    }
  }
}

# ==============================================================================
# RECURSO PRINCIPAL: ORQUESTADOR DE WORKFLOWS
# ==============================================================================
resource "databricks_job" "pipeline_rudo" {
  name = var.job_name

  email_notifications {
    on_failure = [var.alert_email]
  }

  # ----------------------------------------------------------------------------
  # TAREA 1: Capa Bronze (Ingesta en Crudo / Raw Data Appending)
  # ----------------------------------------------------------------------------
  task {
    task_key = "ingesta_bronze"

    new_cluster {
      spark_version = local.job_cluster_config.spark_version
      node_type_id  = local.job_cluster_config.node_type_id
      num_workers   = local.job_cluster_config.num_workers
      spark_conf    = local.job_cluster_config.spark_conf
    }

    notebook_task {
      notebook_path = "/Production/Pipelines/01_Ingest_Bronze"
    }
  }

  # ----------------------------------------------------------------------------
  # TAREA 2: Capa Silver (Limpieza, Deduplicación y Reglas de Calidad)
  # ----------------------------------------------------------------------------
  task {
    task_key = "transformacion_silver"
    
    depends_on {
      task_key = "ingesta_bronze"
    }

    new_cluster {
      spark_version = local.job_cluster_config.spark_version
      node_type_id  = local.job_cluster_config.node_type_id
      num_workers   = local.job_cluster_config.num_workers
      spark_conf    = local.job_cluster_config.spark_conf
    }

    notebook_task {
      notebook_path = "/Production/Pipelines/02_Clean_Silver"
    }
  }

  # ----------------------------------------------------------------------------
  # TAREA 3: Capa Gold (Agregaciones de Negocio, KPIs y Data Products)
  # ----------------------------------------------------------------------------
  task {
    task_key = "agregacion_gold"
    
    depends_on {
      task_key = "transformacion_silver"
    }

    new_cluster {
      spark_version = local.job_cluster_config.spark_version
      node_type_id  = local.job_cluster_config.node_type_id
      num_workers   = local.job_cluster_config.num_workers
      spark_conf    = local.job_cluster_config.spark_conf
    }

    notebook_task {
      notebook_path = "/Production/Pipelines/03_Metrics_Gold"
    }
  }

  # ----------------------------------------------------------------------------
  # PLANIFICADOR CRON
  # ----------------------------------------------------------------------------
  schedule {
    quartz_cron_expression = "0 0 2 * * ?"
    timezone_id            = "America/Mexico_City"
  }

  tags = var.tags
}