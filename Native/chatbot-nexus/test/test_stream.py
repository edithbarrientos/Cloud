import httpx
import json
import sys

URL = "http://localhost:8080/api/chat/stream"
PAYLOAD = {
    "raw_message": "Hola, ejecuta un diagnóstico corto.",
    "customer_id": "usr-nexus-mac-intel",
    "source": "python-harness"
}

print("📡 Lanzando disparo masivo HTTP hacia la superautopista del clúster...")

# ⚡ SIN CACHEO DE ERRORES: Dejamos que cualquier fallo de red o HTTP explote en la consola
with httpx.stream("POST", URL, json=PAYLOAD, timeout=60.0) as response:
    # Si la respuesta no es un código exitoso (2xx), forzamos la excepción cruda de HTTPX
    response.raise_for_status()
        
    print("🟢 [STREAMING ACTIVO] ──► ", end="", flush=True)
    for chunk in response.iter_text():
        print(chunk, end="", flush=True)
    print("\n\n✅ Diagnóstico de flujo finalizado con éxito total.")
