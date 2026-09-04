# -*- coding: utf-8 -*-
"""
Autor: EdithBG <edithbg@corporativo.internal>
Organización: Plataforma Tecnológica TALOS - Core QA Team
Capa: Capa de Configuración e Infraestructura (Bus de Datos)
Componente: Orquestador y Distribuidor de Tareas Celery (celery_app)
"""

import os

from celery import Celery
from dotenv import load_dotenv

# Inyectar las variables de entorno locales de forma segura
load_dotenv()

# Zero Secrets: La cadena de conexión de Redis se recupera dinámicamente de Azure
REDIS_URL = os.getenv("AZURE_REDIS_QUEUE_URL", "redis://localhost:6379/0")

# Inicializar el orquestador maestro distribuidor de hilos de fondo
celery_orchestrator = Celery(
    "core_qa_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL
)

# Configuración de optimización para el clúster elástico distribuido
celery_orchestrator.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Mexico_City",
    enable_utc=True,

    # ⚙️ PARÁMETROS OPERATIVOS DE ALTA DISPONIBILIDAD
    worker_concurrency=4,          # Hilos concurrentes nativos asignados por Worker efímero
    task_track_started=True,        # Permite al Dashboard Web monitorear el progreso en tiempo real
    worker_prefetch_multiplier=1,   # Distribución equitativa (Fair Distribution) de tareas en Redis
    task_acks_late=True             # Tolerancia a fallas: Re-encola la tarea si el contenedor colapsa
)
