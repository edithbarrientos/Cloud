import urllib.request
import json

# 🧠 Conexión directa al puerto de tu Inteligencia Artificial (FastAPI)
url = "http://127.0.0"
headers = {"Content-Type": "application/json"}

# Golden Dataset con tus 15 épocas configuradas
payload = {
  "tenantId": "tenant_generic",
  "epochs": 15,
  "targetLoss": 0.0001,
  "dataset": [
    {"text": "Tengo un problem urgente con mi pasarela de cobro y factura.", "categories": {"BILLING_SUPPORT": 1.0, "TECH_SUPPORT": 0.0, "GREETING": 0.0}},
    {"text": "No paso el pago de mi tarjeta de credito mensual.", "categories": {"BILLING_SUPPORT": 1.0, "TECH_SUPPORT": 0.0, "GREETING": 0.0}},
    {"text": "Exijo una devolucion por un cobro doble en mi cuenta.", "categories": {"BILLING_SUPPORT": 1.0, "TECH_SUPPORT": 0.0, "GREETING": 0.0}},
    {"text": "La aplicacion no conecta, dice token invalido y el servidor se cayo.", "categories": {"BILLING_SUPPORT": 0.0, "TECH_SUPPORT": 1.0, "GREETING": 0.0}},
    {"text": "El sistema se quedo colgado arrojando un error critico 500.", "categories": {"BILLING_SUPPORT": 0.0, "TECH_SUPPORT": 1.0, "GREETING": 0.0}},
    {"text": "Tengo problemas con las credenciales de acceso a la plataforma.", "categories": {"BILLING_SUPPORT": 0.0, "TECH_SUPPORT": 1.0, "GREETING": 0.0}},
    {"text": "Hola buenos dias, hay algun asesor disponible en el chat?", "categories": {"BILLING_SUPPORT": 0.0, "TECH_SUPPORT": 0.0, "GREETING": 1.0}}
  ]
}

print("🪐 Transmitiendo dataset de ráfagas para re-entrenamiento del modelo spaCy CNN...")

try:
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    with urllib.request.urlopen(req) as response:
        print(f"\n📡 Estatus del Re-entrenamiento: {response.status}")
        print(json.dumps(json.loads(response.read().decode("utf-8")), indent=4, ensure_ascii=False))
except Exception as e:
    print(f"❌ Error de red: {e}")
