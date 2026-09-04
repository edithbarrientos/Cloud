"""
Autor: EdithBG <edithbg@corporativo.internal>
Organización: Gobierno de Datos - Plataforma Transversal Core
Componente: Suite de Certificación CRUD con Mocks e Inquilinos (test_gateway)
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.infrastructure.factories.test_data_factory import TestDataFactory

# 🪐 ESCUDO SRE: Desactivamos las llamadas físicas a bases de datos reales durante el test
# Forzamos a que el orquestador responda usando la fábrica sintética TestDataFactory
@pytest.fixture(autouse=True)
def blindar_infraestructura_real(monkeypatch):
    from src.domain.data_orchestrator import DataOrchestrator
    
    async def mock_inicializar(self):
        self.is_redis_active = True
        print("🔧 [TEST-MOCK-REDIS]: Simulación elástica en RAM activada para pruebas.")
        
    async def mock_create(self, llave_id, datos):
        return True
        
    async def mock_read(self, cliente_id, tenant_id):
        return TestDataFactory.simular_respuesta_read(cliente_id)
        
    async def mock_update(self, llave_id, datos_nuevos):
        return True
        
    async def mock_delete(self, llave_id):
        return True

    # Inyectar las funciones de simulación analítica en la memoria RAM del proceso activo
    monkeypatch.setattr(DataOrchestrator, "inicializar_infraestructura", mock_inicializar)
    monkeypatch.setattr(DataOrchestrator, "ejecutar_create", mock_create)
    monkeypatch.setattr(DataOrchestrator, "procesar_petición_inteligente", mock_read)
    monkeypatch.setattr(DataOrchestrator, "ejecutar_update", mock_update)
    monkeypatch.setattr(DataOrchestrator, "ejecutar_delete", mock_delete)

transport = ASGITransport(app=app)

@pytest_asyncio.fixture
async def cliente_api():
    async with AsyncClient(transport=transport, base_url="http://test") as cliente:
        yield cliente

@pytest.mark.asyncio
async def test_crear_perfil_exito(cliente_api: AsyncClient):
    """🏆 Debe insertar exitosamente un perfil y retornar HTTP 201"""
    cliente_id = "CLI-521555"
    payload_sintetico = {"nombre": "Edith BG", "saldoPendiente": 0.0}
    
    cabeceras = {
        "X-Tenant-Client-Id": "talos-chatbot",
        "Content-Type": "application/json"
    }
    
    response = await cliente_api.post(
        f"/api/v1/core/customer/{cliente_id}",
        json=payload_sintetico,
        headers=cabeceras
    )
    
    assert response.status_code == 201
    assert response.json()["status"] == "CREATED"
    assert response.json()["tenantProcesador"] == "talos-chatbot"

@pytest.mark.asyncio
async def test_leer_perfil_con_mascara_pii(cliente_api: AsyncClient):
    """🔐 Debe aplicar el middleware de ciberseguridad PII ante inquilinos públicos"""
    cliente_id = "CLI-999888"
    cabeceras = {"X-Tenant-Client-Id": "talos-chatbot"}
    
    response = await cliente_api.get(
        f"/api/v1/core/customer/{cliente_id}",
        headers=cabeceras
    )
    
    assert response.status_code == 200
    json_out = response.json()
    assert json_out["status"] == "SUCCESS"
    
    # Certificar que el PiiMiddleware interceptó el mock e inyectó las máscaras del CISO
    assert json_out["data"]["piiMaskingAplicado"] is True
    assert json_out["data"]["saldoGlobalConsolidado"] == "CONFIDENCIAL_PERMISO_DENIEGADO"

@pytest.mark.asyncio
async def test_actualizar_perfil_exito(cliente_api: AsyncClient):
    """🏆 Debe actualizar las particiones físicas y retornar HTTP 200"""
    cliente_id = "CLI-521555"
    datos_actualizados = {"nombre": "Edith BG Actualizada", "saldoPendiente": 0.0}
    cabeceras = {"X-Tenant-Client-Id": "fraud-analytics-engine"}
    
    response = await cliente_api.put(
        f"/api/v1/core/customer/{cliente_id}",
        json=datos_actualizados,
        headers=cabeceras
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "UPDATED"

@pytest.mark.asyncio
async def test_borrar_perfil_exito(cliente_api: AsyncClient):
    """🚨 Debe purgar el expediente físico del cliente de forma segura"""
    cliente_id = "CLI-EFIMERO"
    cabeceras = {"X-Tenant-Client-Id": "admin-governance-portal"}
    
    response = await cliente_api.delete(
        f"/api/v1/core/customer/{cliente_id}",
        headers=cabeceras
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "DELETED"
