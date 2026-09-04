import asyncio
import jwt
import time
import httpx
import random

SECRET_KEY = "orchestra_labs_ultra_secret_key_2026"
ALGORITHM = "HS256"
# 🔗 ENRUTAMIENTO CORRECTO: Le pega al puerto 3000 que expone el contenedor de tu Chatbot
URL = "http://localhost:3000/api/v1/chat/stream"

PROMPTS_POOL = [
    "Auditar de forma urgente la tabla analítica de Tarjetas de Crédito de Banco Alfa",
    "Generar un reporte de control de riesgos y Prevención de Fraudes",
    "Consultar métricas de la infraestructura distribuida CosmosDB",
    "Ejecutar una auditoría forense sobre las cuentas suspendidas del Ledger"
]

# Matriz de negocios que se inyectarán de forma parametrizada al contrato
DOMAINS_POOL = ["CREDIT_CARDS", "FRAUD_PREVENTION", "COSMOS_NOSQL", "GENERAL_LEDGER"]

def header_valido(req_id):
    p = {"sub": f"user_{req_id}", "exp": int(time.time()) + 7200}
    # Genera la cadena Bearer limpia sin comillas internas destructivas
    return {"Content-Type": "application/json", "Authorization": f"Bearer {jwt.encode(p, SECRET_KEY, algorithm=ALGORITHM)}"}

def header_expirado(req_id):
    p = {"sub": "attacker_expired", "exp": int(time.time()) - 3600}
    return {"Content-Type": "application/json", "Authorization": f"Bearer {jwt.encode(p, SECRET_KEY, algorithm=ALGORITHM)}"}

def header_corrupto(req_id):
    p = {"sub": f"user_{req_id}", "exp": int(time.time()) + 7200}
    return {"Content-Type": "application/json", "Authorization": f"Bearer {jwt.encode(p, SECRET_KEY, algorithm=ALGORITHM)}FALSOS_BYTES"}

def header_anonimo(req_id):
    return {"Content-Type": "application/json"}

HEADER_MAPPER = {
    "VALIDO": header_valido,
    "EXPIRADO": header_expirado,
    "CORRUPTO": header_corrupto,
    "ANONIMO": header_anonimo
}

async def send_request(client, request_id, request_type, semaphore):
    async with semaphore:
        selected_prompt = random.choice(PROMPTS_POOL)
        selected_domain = random.choice(DOMAINS_POOL)
        
        current_payload = {
            "user_prompt": selected_prompt,
            "session_id": f"SESS-1K-{request_id}",
            "business_domain": selected_domain  # ◄ Parametrización dinámica del negocio
        }
        headers = HEADER_MAPPER[request_type](request_id)

        try:
            start = time.perf_counter()
            response = await client.post(URL, json=current_payload, headers=headers, timeout=15.0)
            latency = (time.perf_counter() - start) * 1000
            
            if response.status_code == 200:
                print(f"📥 [ID-{request_id:04d}] [{request_type}] ──► ✅ PALOMITA INYECTADA ({selected_domain}) EN {latency:.2f} ms")
                return "SUCCESS"
            elif response.status_code == 401:
                print(f"🔒 [ID-{request_id:04d}] [{request_type}] ──► ❌ TACHE BLOQUEADO (401 Unauthorized) EN {latency:.2f} ms")
                return "BLOCKED"
            return "ERROR"
        except Exception:
            return "NETWORK_FAIL"

async def run_benchmark():
    print("===============================================================================")
    print("🏛️  ORCHESTRA LABS: MEGA BENCHMARK PARAMETRIZADO POR DOMINIO DE NEGOCIO (1K)")
    print("===============================================================================\n")
    
    start_time = time.perf_counter()
    semaphore = asyncio.Semaphore(50)
    limits = httpx.Limits(max_keepalive_connections=50, max_connections=100)
    
    async with httpx.AsyncClient(limits=limits) as client:
        tasks = []
        for i in range(1, 501): tasks.append(send_request(client, i, "VALIDO", semaphore))
        for i in range(501, 667): tasks.append(send_request(client, i, "EXPIRADO", semaphore))
        for i in range(667, 833): tasks.append(send_request(client, i, "CORRUPTO", semaphore))
        for i in range(833, 1001): tasks.append(send_request(client, i, "ANONIMO", semaphore))

        random.shuffle(tasks)
        results = await asyncio.gather(*tasks)
        
    total_duration = time.perf_counter() - start_time
    success_count = results.count("SUCCESS")
    blocked_count = results.count("BLOCKED")
    
    print("\n===============================================================================")
    print("📊 REPORTE DE RESILIENCIA BAJO RED DE CONTENEDORES EXTERSOS")
    print("===============================================================================")
    print(f"✅ Palomitas Exitosas Transmitidas de Contenedor a Contenedor: {success_count}/500")
    print(f"❌ Taches Infiltrados Neutralizados de Forma Segura en Edge : {blocked_count}/500")
    print(f"⏱️ Tiempo de Procesamiento del Enjambre de 1,000 Mensajes   : {total_duration:.2f} segundos")
    print("===============================================================================\n")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
