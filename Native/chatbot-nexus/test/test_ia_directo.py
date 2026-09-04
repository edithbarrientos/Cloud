import json
import httpx

def construir_prompt_corporativo(mensaje_usuario: str) -> list:
    prompt_sistema = (
        "Eres el asistente virtual inteligente de Chatbot Nexus. Responde de forma clara y profesional.\n"
        "Utiliza la siguiente información verídica de la empresa para formular tu respuesta:\n"
        "== CONTEXTO CONOCIMIENTO COMPAÑÍA ==\n"
        "No hay documentos empresariales adicionales disponibles para esta consulta.\n"
        "====================================="
    )
    return [
        {"role": "system", "content": prompt_sistema},
        {"role": "user", "content": mensaje_usuario}
    ]

def probar_ia_local_directo():
    url_ollama = "http://127.0.0"
    mensaje = "Hola, responde únicamente con un saludo corto de tres palabras."
    
    payload = {
        "model": "deepseek-r1:1.5b",
        "messages": construir_prompt_corporativo(mensaje),
        "stream": True,
        "options": {
            "temperature": 0.0,
            "top_p": 0.9
        }
    }

    print("🚀 [TEST OLLAMA DIRECTO] Evaluando salud del motor de IA local...")
    print(f"📥 Payload estructurado enviado al puerto 11434")
    print("🤖 Respuesta cruda del modelo: ")

    try:
        with httpx.stream("POST", url_ollama, json=payload, timeout=60.0) as response:
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        token = data.get("message", {}).get("content", "")
                        print(token, end="", flush=True)
            else:
                print(f"\n❌ Error de red en Ollama: Código HTTP {response.status_code}")
        print("\n\n✅ Validación directa de Ollama finalizada con éxito.")
    except Exception as e:
        print(f"\n❌ Falló la conexión local: {str(e)}")

if __name__ == "__main__":
    probar_ia_local_directo()
