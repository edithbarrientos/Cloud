# -*- coding: utf-8 -*-
"""
Suite de Pruebas de Integración de Alta Escala - Servidor FastAPI
Componente de Calidad de la Plataforma TALOS
"""

import json
import os
import pytest
from httpx import ASGITransport, AsyncClient
from src.main import app
from src.config.env_config import EnvConfig

# Localizar la ruta física de la carpeta de integración para cargar los archivos JSON
BASE_TEST_DIR = os.path.dirname(__file__)


# 🚨 CORRECCIÓN: Configurar el scope del bucle de eventos para evitar que la terminal se pasme
@pytest.mark.asyncio(scope="module")
async def test_endpoint_debe_procesar_whatsapp_happy_path_exitosamente():
    """
    [QA-01-POS]: Certifica que la API REST recibe el payload canónico de WhatsApp,
    lo valida con Pydantic y procesa la inferencia asíncrona de forma correcta.
    """
    # 1. Configurar entorno controlado de simulación
    EnvConfig.ENVIRONMENT = "offline_testing"
    
    # 2. Cargar el Dummy JSON del disco
    with open(os.path.join(BASE_TEST_DIR, "mock_ingress_whatsapp.json"), "r", encoding="utf-8") as f:
        payload_dummy = json.load(f)

    # 3. Levantar el cliente virtual asíncrono sobre la app de FastAPI usando ASGITransport
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Ejecutar la llamada HTTP POST al endpoint privado
        response = await client.post("/api/v1/compute/language", json=payload_dummy)
        
        # 4. Validar los criterios de aceptación e integridad del contrato de salida
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["correlation_id"] == "TRANS-2026-HAPPY-PATH-01"
        assert "canal_usuario_id" in response_json
        assert "telemetria_consumo" in response_json


# 🚨 CORRECCIÓN: Configurar el scope del bucle de eventos para evitar que la terminal se pasme
@pytest.mark.asyncio(scope="module")
async def test_endpoint_debe_activar_fallback_ante_crisis_o_falla_de_ia():
    """
    [QA-03-NEG]: Certifica que si el sistema procesa una entrada y el motor truena,
    el bloque try/except de main.py activa el Circuit Breaker de contingencia a costo $0.
    """
    EnvConfig.ENVIRONMENT = "offline_testing"
    
    with open(os.path.join(BASE_TEST_DIR, "mock_ingress_furia.json"), "r", encoding="utf-8") as f:
        payload_dummy = json.load(f)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/compute/language", json=payload_dummy)
        
        assert response.status_code == 200
        response_json = response.json()
        # Verificar que el Circuit Breaker inyectó la telemetría de contingencia local
        assert response_json["telemetria_consumo"]["modelo_utilizado"] == "CIRCUIT_BREAKER_LOCAL_FALLBACK"

@pytest.mark.asyncio(scope="module")
async def test_endpoint_debe_activar_contingencia_si_el_adaptador_principal_truena_en_produccion():
    """
    [NUEVO - QA-03-NEG] Simula un fallo crítico o timeout en el adaptador de OpenAI 
    durante un entorno de producción, forzando la ejecución de las líneas 39-49 de main.py.
    """
    # 1. Configurar el entorno en producción para activar la ruta principal
    EnvConfig.ENVIRONMENT = "production"
    
    with open(os.path.join(BASE_TEST_DIR, "mock_ingress_whatsapp.json"), "r", encoding="utf-8") as f:
        payload_dummy = json.load(f)

    # 2. Inyección de Falla (Mocking): Forzar a que cualquier llamada de OpenAI lance un error de red
    from unittest.mock import patch
    from src.adapter.openai_adapter import OpenAiAdapter
    
    # Parcheamos el método del adaptador para que lance una excepción de inmediato
    with patch.object(OpenAiAdapter, "procesar_computo_linguistico", side_effect=Exception("Fallo total de conexión API OpenAI")):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            
            # Ejecutar la llamada HTTP POST
            response = await client.post("/api/v1/compute/language", json=payload_dummy)
            
            # 3. Validar Criterio de Aceptación: El servidor responde 200 porque el Circuit Breaker
            # interceptó el error en las líneas 39-49 y desvió el flujo al fallback local inmutable.
            assert response.status_code == 200
            response_json = response.json()
            assert response_json["telemetria_consumo"]["modelo_utilizado"] == "CIRCUIT_BREAKER_LOCAL_FALLBACK"
