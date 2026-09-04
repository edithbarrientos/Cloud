import os
import sys
import asyncio

# Configurar rutas para encontrar el módulo src/ desde la carpeta test/
RAIZ_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, RAIZ_DIR)
sys.path.insert(0, os.path.join(RAIZ_DIR, "src"))

from src.main import procesar_chat_directo
from src.repository import repository

async def ejecutar_test_flujo():
    print("🚀 [TEST FLUJO] Iniciando validación de canales asíncronos...")
    
    # 1. Encender el pool de la base de datos Redis local de tu Mac
    repository.start()
    
    cliente_id = "usr-nexus-local-test"
    mensaje = "Hola, responde únicamente con un saludo corto de tres palabras."
    
    print(f"📥 Mensaje inyectado a main.py: '{mensaje}'")
    print("🤖 Respuesta de DeepSeek-R1 en streaming directo: ")
    
    try:
        # 2. Consumir el generador asíncrono puro de tu lógica
        async for token in procesar_chat_directo(mensaje, cliente_id):
            print(token, end="", flush=True)
            
        print("\n\n✅ Validación de flujo asíncrono completada con éxito.")
    except Exception as e:
        print(f"\n❌ Falló la ejecución del test de flujo: {str(e)}")
    finally:
        # 3. Apagar los hilos de red de Redis de forma segura
        await repository.stop()

if __name__ == "__main__":
    asyncio.run(ejecutar_test_flujo())
