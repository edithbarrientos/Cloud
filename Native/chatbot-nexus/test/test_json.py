import os
import sys
import asyncio
import json
import time
import psutil

# Configurar rutas para encontrar el módulo src/
RAIZ_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, RAIZ_DIR)
sys.path.insert(0, os.path.join(RAIZ_DIR, "src"))

from src.main import procesar_chat_directo
from src.repository import repository

def obtener_uso_memoria_mb() -> float:
    """Lee el consumo real de RAM del proceso actual del sistema."""
    proceso = psutil.Process(os.getpid())
    return proceso.memory_info().rss / (1024 * 1024)

async def ejecutar_chat_con_telemetria_avanzada():
    os.system("stty sane")
    print("\r🚀 [NEXUS ADVANCED TELEMETRY] Inicializando sondas de Kernel...")
    
    t_start_infra = time.perf_counter()
    repository.start()
    t_infra_ms = (time.perf_counter() - t_start_infra) * 1000
    print(f"\r🟢 Repositorio acoplado. Latencia Handshake: {t_infra_ms:.2f} ms")
    print("\r💬 Escribe tu mensaje para auditar las métricas del clúster (o 'salir'):")
    
    while True:
        try:
            user_input = input("\r\n❯ Tú: ").strip()
            if not user_input: continue
            if user_input.lower() in ["salir", "exit", "quit"]:
                break
                
            # Captura de RAM antes de la inferencia
            ram_inicial = obtener_uso_memoria_mb()
            
            t_start_json = time.perf_counter()
            payload_json = json.dumps({
                "raw_message": user_input,
                "customer_id": "usr-nexus-local-enterprise",
                "source": "telemetry_advanced_session"
            })
            datos_parseados = json.loads(payload_json)
            mensaje_validado = datos_parseados.get("raw_message", "")
            cliente_id = datos_parseados.get("customer_id", "usr-generic")
            t_json_ms = (time.perf_counter() - t_start_json) * 1000

            print("\r🤖 Bot Nexus: ", end="", flush=True)
            
            t_start_ia = time.perf_counter()
            primer_token_recibido = False
            t_ultimo_token = 0.0
            t_ttft_ms = 0.0
            token_count = 0
            tiempos_inter_token = []
            
            async for token in procesar_chat_directo(mensaje_validado, cliente_id):
                t_actual = time.perf_counter()
                
                if not primer_token_recibido:
                    t_ttft_ms = (t_actual - t_start_ia) * 1000
                    primer_token_recibido = True
                    t_generacion_start = t_actual
                else:
                    # Calcular tiempo entre el token anterior y el actual
                    latencia_inter = (t_actual - t_ultimo_token) * 1000
                    tiempos_inter_token.append(latencia_inter)
                    
                t_ultimo_token = t_actual
                
                if "\n" in token:
                    token = token.replace("\n", "\n\r")
                print(token, end="", flush=True)
                token_count += 1
            print()
            
            t_total_ia_sec = time.perf_counter() - t_start_ia
            ram_final = obtener_uso_memoria_mb()
            
            # Calcular promedios algorítmicos de red
            t_generacion_puro_sec = time.perf_counter() - t_generacion_start if primer_token_recibido else 0
            tokens_per_sec_reales = token_count / t_generacion_puro_sec if t_generacion_puro_sec > 0 else 0
            latencia_inter_promedio = sum(tiempos_inter_token) / len(tiempos_inter_token) if tiempos_inter_token else 0
            ram_delta_mb = ram_final - ram_inicial
            
            # PANEL DE TELEMETRÍA AVANZADO EN COLUMNA CERO
            print("\r" + "─"*60)
            print(f"\r📊 [PANEL DE OBSERVABILIDAD ENTERPRISE - METRICAS SRE]")
            print(f"\r🧬 Parseo JSON Contrato .proto : {t_json_ms:.4f} ms")
            print(f"\r⚡ Tiempo al Primer Token (TTFT): {t_ttft_ms:.2f} ms (Latencia de Carga de red)")
            print(f"\r⏱️ Latencia Inter-Token Promedio: {latencia_inter_promedio:.2f} ms/token")
            print(f"\r🚀 Velocidad de Inferencia Neta : {tokens_per_sec_reales:.2f} tokens/seg")
            print(f"\r⏱️ Tiempo Total del Ciclo de IA : {t_total_ia_sec:.2f} seg")
            print(f"\r💾 Consumo del Proceso (RAM Delta): {ram_delta_mb:+.2f} MB")
            print(f"\r📊 Volumen de Respuesta Generada: {token_count} tokens")
            print("\r" + "─"*60)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\r\n❌ Error en sondas: {str(error)}")

    print("\r\n🛑 Desconectando sondas y cerrando hilos...")
    await repository.stop()
    print("\r✅ Saneamiento de telemetría finalizado.")

if __name__ == "__main__":
    asyncio.run(ejecutar_chat_con_telemetria_avanzada())
