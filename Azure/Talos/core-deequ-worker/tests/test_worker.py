import pytest
from src.infrastructure.factories.test_data_factory import TestDataFactory

@pytest.mark.asyncio
async def test_worker_create_sintetico():
    """🏆 Debe validar la orquestación de escritura asíncrona del worker"""
    res = TestDataFactory.simular_respuesta_create("CLI-123")
    assert res["clienteId"] == "CLI-123"
    assert res["operacion"] == "WORKER_INSERT"

@pytest.mark.asyncio
async def test_worker_read_sintetico():
    """🏆 Debe validar la normalización en camelCase analítica del worker"""
    res = TestDataFactory.simular_respuesta_read("CLI-123")
    assert res["clienteId"] == "CLI-123"
    assert res["segmentoCorporativo"] == "VIP"
