# FILENAME: talos-service-chatbot-core/run_core.py
import os
import uvicorn

if __name__ == "__main__":
    print("\n================================================================================")
    print("🚀 [TALOS CHATBOT-CORE]: Servidor FastAPI Python inicializado con éxito al 100%.")
    print("📡 [ESTADO]: Escuchando tráfico transaccional en http://localhost:3000")
    print("================================================================================\n")

    # Calculamos la ruta física absoluta de la carpeta src
    project_root = os.path.dirname(os.path.abspath(__file__))
    src_folder = os.path.join(project_root, "src")

    # ⚠️ MEJORA DE RENDIMIENTO: Usamos app_dir para forzar a los 4 workers hijos 
    # a nacer dentro de 'src/'. Así importan "main:app" de manera nativa sin fallas.
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=3000, 
        log_level="warning", 
        workers=4, 
        loop="asyncio",
        app_dir=src_folder
    )
