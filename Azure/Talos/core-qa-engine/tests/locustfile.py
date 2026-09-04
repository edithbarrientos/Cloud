# -*- coding: utf-8 -*-
"""
Autor: EdithBG <edithbg@corporativo.internal>
Capa de Infraestructura: Inyector de Carga Multi-Proyecto con Escudo de Sandboxing
"""

import os
import json
import random
from uuid import uuid4
from locust import HttpUser, task, between
from jinja2 import Template

def cargar_contexto_testing_puro() -> tuple[list, dict]:
    """Carga los vectores sintéticos de la IA y el mapa de configuración del Job en memoria RAM."""
    ruta_json = "data/payloads.json"
    ruta_config = "data/job_config.json"
    pool_datos, config_job = [], {}
    
    if os.path.exists(ruta_json):
        with open(ruta_json, "r", encoding="utf-8") as f:
            pool_datos = json.load(f).get("datos_sinteticos", [])
    if os.path.exists(ruta_config):
        with open(ruta_config, "r", encoding="utf-8") as f:
            config_job = json.load(f)
            
    return pool_datos, config_job

# Pool global indexado al arrancar para evitar bloqueos de disco (I/O) durante ráfagas concurrentes
POOL_DATOS, CONFIG_JOB = cargar_contexto_testing_puro()

class UniversalPythonStressUser(HttpUser):
    """Simula un agente virtual elástico políglota para N proyectos de la corporación."""
    # Simula pausas humanas realistas de lectura/escritura en milisegundos
    wait_time = between(0.2, 1.0)

    @task
    def inyectar_carga_agnostica_por_plantilla(self):
        """Toma un caso sintético, renderiza la plantilla Jinja2 y ametralla la red externa."""
        if not POOL_DATOS or not CONFIG_JOB:
            return
            
        # 1. Muestreo: Seleccionar de forma aleatoria un vector conversacional del pool
        caso_variables = random.choice(POOL_DATOS)
        
        # 2. Renderizado Jinja2: Reconstruye el JSON nativo amoldándose al contrato del proyecto objetivo
        template_raw = json.dumps(CONFIG_JOB["body_template"])
        json_renderizado_str = Template(template_raw).render(**caso_variables)
        payload_final_json = json.loads(json_renderizado_str)
        
        # 3. Cláusula CISO (Data Sandboxing Protocol): Inyección inmutable de cabeceras de control
        headers = CONFIG_JOB.get("headers_requeridos", {"Content-Type": "application/json"}).copy()
        headers["X-TALOS-QA-SANDBOX"] = "true"  # Ordena al ERP/Base de datos desviar la persistencia a zonas Mock
        headers["X-Correlation-ID"] = f"QA-STRESS-VOLATILE-{uuid4() if 'uuid4' in locals() else random.randint(10000, 99999)}"
        
        method = CONFIG_JOB.get("method", "POST")
        endpoint = CONFIG_JOB.get("target_endpoint", "/")
        
        # 4. Disparo Asíncrono: Invoca el socket perimetral del microservicio bajo prueba
        self.client.request(
            method=method,
            url=endpoint,
            json=payload_final_json,
            headers=headers
        )