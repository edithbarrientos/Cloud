# -*- coding: utf-8 -*-
"""
Autor: EdithBG <edithbg@corporativo.internal>
Componente: Servidor de Inferencia Lingüística API (main)
"""

import os

import uvicorn
from fastapi import FastAPI, HTTPException, status

from src.domain.contracts import AIEngineRequest, AIEngineResponse
from src.factory.ai_factory import AIEngineFactory

# Inicializar el servidor FastAPI de alto rendimiento para el bus interno
app = FastAPI(
    title="TALOS IA Engine Microservice",
    description="Motor lógico probabilístico de procesamiento de lenguaje nativo en Python",
    version="1.0.0"
)


@app.post(
    "/api/v1/compute/language",
    response_model=AIEngineResponse,
    status_code=status.HTTP_200_OK,
    summary="Procesa el cómputo lingüístico asíncrono con control de resiliencia distribuida"
)
async def compute_language(request: AIEngineRequest) -> AIEngineResponse:
    """
    Endpoint privado expuesto exclusivamente dentro de la subred interna.
    Recibe el payload canónico, inyecta las variables y orquesta el puerto de inferencia.
    """
    try:
        # Resolver la instancia de forma dinámica dentro de la petición para evitar bloqueos globales
        motor_ia = AIEngineFactory.obtener_instancia_motor()

        # Ejecución polimórfica asíncrona real sin bloqueo del bucle de eventos
        return await motor_ia.procesar_computo_linguistico(request)

    except Exception as error:
        # [TEST QA-03-NEG]: Si el adaptador productivo falla o agota reintentos, se fuerza el disyuntor manual
        print(f"🚨 [CIRCUIT BREAKER ABIERTO]: Conmutando de urgencia al fallback local: {str(error)}")

        try:
            from src.adapter.mock_fallback_adapter import MockFallbackAdapter
            contingencia = MockFallbackAdapter()
            return await contingencia.procesar_computo_linguistico(request)

        except Exception as error_fatal:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error crítico en la capa de contingencia: {str(error_fatal)}"
            )


if __name__ == "__main__":
    port_env = int(os.getenv("PORT", "8000"))
    uvicorn.run("src.main:app", host="0.0.0.0", port=port_env, reload=True)
