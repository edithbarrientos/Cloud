"""
Autor: EdithBG <edithbg@corporativo.internal>
Organización: Gobierno Corporativo de Datos - Plataforma Transversal Core
Componente: API Gateway Multi-Inquilino Agnóstico con Operaciones CRUD (src/main.py)
Descripción: Punto de entrada único y centralizado para la ingesta, mutación y 
             extracción de perfiles unificados de la compañía. Atiende a N clientes 
             institucionales en paralelo bajo aislamiento perimetral estricto.
"""
import os
from fastapi import FastAPI, Header, HTTPException, Body
from src.config.env_config import env_config
from src.domain.data_orchestrator import DataOrchestrator
from src.infrastructure.web.pii_middleware import PiiMiddleware # Middleware de Máscaras PII

# 🪐 1. INICIALIZACIÓN DEL MOTOR CORE (Agnóstico, Transversal y Multi-Tenant)
app = FastAPI(
    title="Core Data Access Product Engine",
    description="Plataforma Transversal para el Acceso, Mutación y Gobierno de Datos Corporativos Globales",
    version="1.0.0"
)

# Inyectar la Aduana de Ciberseguridad PII en el ciclo de vida de FastAPI
app.add_middleware(PiiMiddleware)

# Acoplamiento del Orquestador de Datos leyendo la variable elástica de la infraestructura
orquestador_datos = DataOrchestrator(env_config.TARGET_ENGINE)

@app.on_event("startup")
async def startup_event():
    """Gatilla la apertura y conexión de todos los pools de hilos, sockets y drivers de la red"""
    await orquestador_datos.inicializar_infraestructura()

@app.on_event("shutdown")
async def shutdown_event():
    """Aplica un cierre controlado (Graceful Shutdown) liberando la memoria RAM del servidor"""
    await orquestador_datos.liberar_infraestructura()

# ==============================================================================
# 🪐 ADUANA CRUD: ENDPOINTS CORE MULTI-INQUILINO (MULTI-TENANT ENDPOINTS)
# ==============================================================================

@app.post("/api/v1/core/customer/{cliente_id}", status_code=201)
async def crear_perfil_cliente(
    cliente_id: str, 
    datos: dict = Body(...), 
    x_tenant_client_id: str = Header(..., description="Firma identificadora obligatoria del Inquilino Consumidor")
):
    """
    [C - CREATE]: Inserta un nuevo registro, fila SQL, documento NoSQL o archivo JSON 
    en el motor físico activo de la organización (Postgres, Snowflake, S3, Azure Blobs).
    """
    print(f"📡 [DATA-PRODUCT-CREATE]: Inquilino [{x_tenant_client_id}] solicita inserción para: {cliente_id}")
    exito = await orquestador_datos.ejecutar_create(cliente_id, datos)
    
    if not exito:
        raise HTTPException(status_code=500, detail="CORE_DATABASE_INSERT_OPERATION_FAILED")
        
    return {
        "status": "CREATED",
        "transaccionId": f"TX-C-{cliente_id}",
        "tenantProcesador": x_tenant_client_id
    }

@app.get("/api/v1/core/customer/{cliente_id}")
async def leer_perfil_cliente(
    cliente_id: str, 
    x_tenant_client_id: str = Header(..., description="Firma identificadora obligatoria del Inquilino Consumidor")
):
    """
    [R - READ]: Recupera el perfil analítico o transaccional unificado normalizado 
    al formato camelCase corporativo desde la caché RAM de Redis o la capa física.
    """
    print(f"📡 [DATA-PRODUCT-READ]: Inquilino [{x_tenant_client_id}] solicita extracción para: {cliente_id}")
    
    # El orquestador central se encarga de revisar la caché Redis, aplicar el CRUD y jalar del motor activo
    perfil_unificado = await orquestador_datos.procesar_petición_inteligente(cliente_id, x_tenant_client_id)
    
    if not perfil_unificado:
        raise HTTPException(status_code=404, detail="CUSTOMER_PROFILE_NOT_FOUND_IN_ENTERPRISE_STORAGE")
        
    return {
        "status": "SUCCESS",
        "tenantProcesador": x_tenant_client_id,
        "data": perfil_unificado
    }

@app.put("/api/v1/core/customer/{cliente_id}")
async def actualizar_perfil_cliente(
    cliente_id: str, 
    datos_nuevos: dict = Body(...), 
    x_tenant_client_id: str = Header(..., description="Firma identificadora obligatoria del Inquilino Consumidor")
):
    """
    [U - UPDATE]: Aplica mutaciones, parches de saldos o actualizaciones semánticas 
    sobre los registros vigentes de la empresa, invalidando la caché RAM de forma automática.
    """
    print(f"📡 [DATA-PRODUCT-UPDATE]: Inquilino [{x_tenant_client_id}] solicita parche para: {cliente_id}")
    exito = await orquestador_datos.ejecutar_update(cliente_id, datos_nuevos)
    
    if not exito:
        raise HTTPException(status_code=400, detail="CORE_DATABASE_UPDATE_OPERATION_FAILED")
        
    return {
        "status": "UPDATED",
        "transaccionId": f"TX-U-{cliente_id}",
        "tenantProcesador": x_tenant_client_id
    }

@app.delete("/api/v1/core/customer/{cliente_id}")
async def borrar_perfil_cliente(
    cliente_id: str, 
    x_tenant_client_id: str = Header(..., description="Firma identificadora obligatoria del Inquilino Consumidor")
):
    """
    [D - DELETE]: Remueve de forma física o lógica un expediente de datos. 
    Aplica políticas rígidas de auditoría perimetral y purga instantánea en Redis RAM.
    """
    print(f"🚨 [DATA-PRODUCT-DELETE]: Inquilino [{x_tenant_client_id}] solicita eliminación de: {cliente_id}")
    exito = await orquestador_datos.ejecutar_delete(cliente_id)
    
    if not exito:
        raise HTTPException(status_code=500, detail="CORE_DATABASE_DELETE_OPERATION_FAILED")
        
    return {
        "status": "DELETED",
        "tenantProcesador": x_tenant_client_id
    }