"""
Autor: EdithBG <edithbg@corporativo.internal>
Organización: Gobierno de Datos - Plataforma Transversal Core
Componente: Middleware de Anonimización Dinámica y Enmascaramiento PII (PiiMiddleware)
Descripción: Componente perimetral de ciberseguridad. Analiza el linaje del inquilino 
             (Tenant) y aplica máscaras de datos en tiempo real sobre la RAM antes de 
             escupir el JSON hacia la red, cumpliendo con las directrices del CISO.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
import json

class PiiMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # 🪐 1. Capturar la respuesta web del flujo de FastAPI en el hilo principal
        response = await call_next(request)
        
        # Extraer de forma segura el identificador único del inquilino desde los headers
        tenant_id = request.headers.get("X-Tenant-Client-Id", "").strip().lower()
        
        # Si la respuesta no es un JSON válido o es una redirección/archivo, se libera el flujo intacto
        if not response.headers.get("content-type", "").startswith("application/json"):
            return response

        # 🪐 2. Extraer el cuerpo binario de la respuesta y deserializarlo a diccionario de Python
        body_bytes = b""
        async for chunk in response.body_iterator:
            body_bytes += chunk
            
        try:
            payload_json = json.loads(body_bytes.decode('utf-8'))
        except Exception:
            # Mecanismo Fail-Safe: Si el parseo de bytes truena, reconstruye la respuesta original
            return Response(content=body_bytes, status_code=response.status_code, headers=dict(response.headers))

        # 🪐 3. GOBERNANZA DE MÁSCARAS: Evaluar si el perfil del consumidor exige anonimización
        # Si el consumidor es el Chatbot público, se alteran los datos sensibles en la RAM
        if tenant_id == "talos-chatbot" and "data" in payload_json:
            datos_cliente = payload_json["data"]
            
            if isinstance(datos_cliente, dict):
                # Enmascarar números de tarjeta de crédito/débito corporativas
                if "numeroTarjeta" in datos_cliente:
                    tarjeta = str(datos_cliente["numeroTarjeta"])
                    datos_cliente["numeroTarjeta"] = f"{tarjeta[:4]}-XXXX-XXXX-{tarjeta[-4:]}" if len(tarjeta) >= 8 else "XXXX-XXXX-XXXX"
                
                # Anonimizar saldos financieros para canales públicos masivos
                if "saldoGlobalConsolidado" in datos_cliente:
                    datos_cliente["saldoGlobalConsolidado"] = "CONFIDENCIAL_PERMISO_DENIEGADO"
                
                # Inyectar indicador de auditoría perimetral de seguridad
                datos_cliente["piiMaskingAplicado"] = True

        # 🪐 4. Re-empaquetar el payload modificado a bytes y retornar la respuesta cifrada en red
        nuevo_contenido = json.dumps(payload_json).encode('utf-8')
        
        # Reconstruir las cabeceras actualizando la longitud exacta de la nueva carga útil
        cabeceras = dict(response.headers)
        cabeceras["content-length"] = str(len(nuevo_contenido))
        
        return Response(content=nuevo_contenido, status_code=response.status_code, headers=cabeceras)