import socket
import json
from datetime import datetime

# 🔌 Conexión directa al puerto de pruebas interactivo
HOST = '127.0.0.1'
PORT = 9999

# Payload dinámico contractual de 12 campos que espera tu AnomalyEvent en Scala
data = {
    "tenantId": "tenant_generic",
    "clientId": "client-python-dynamic-888",
    "customerId": "cust-user-606",
    "sessionId": "sess-prod-100",
    "messageId": "msg-dynamic-test-2026",
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "source": "PYTHON_SOCKET_INJECTOR",
    # 🧠 Modifica este mensaje como tú quieras en caliente, Flink lo procesará dinámicamente
    "message": "URGENTE: Me cobraron la factura de la suscripcion anual dos veces y exijo un reembolso.",
    "rawMessage": "RAW_DATA",
    "issueCategory": "BILLING_SUPPORT",
    "summary": "Prueba de enrutamiento dinámico",
    "attachment": "NONE"
}

print(f"🚀 Conectando al socket local en el puerto {PORT}...")

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    
    # Serialización y adición del carácter de salto de línea (\n) requerido por Flink
    payload = json.dumps(data) + "\n"
    s.sendall(payload.encode('utf-8'))
    
    print("📡 [Éxito] ¡JSON dinámico inyectado en el stream de Flink! Cerrando canal.")
    s.close()
except Exception as e:
    print(f"❌ Error de red: {e}. Recuerda encender el comando nc -lk 9999 antes de correr el script.")