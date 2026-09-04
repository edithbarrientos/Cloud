/**
 * Plataforma Nexus Mesh - Cliente Web de Telemetría e Inferencia
 * Administra el streaming asíncrono de tokens gRPC/HTTP hacia el BFF corporativo.
 */

// Configuración del endpoint público mapeado a través del balanceador de carga de Kubernetes
const API_URL = "http://localhost:8501/api/chat";

async function enviarMensaje() {
    const inputMensaje = document.getElementById("message-input");
    const contenedorChat = document.getElementById("chat-container");
    const textoMensaje = inputMensaje.value.trim();

    // Validar que el campo no se encuentre vacío antes de procesar el JSON
    if (!textoMensaje) return;

    // Pintar el mensaje del usuario en la interfaz gráfica
    contenedorChat.innerHTML += `<div class="user-message"><b>Tú:</b> ${textoMensaje}</div>`;
    inputMensaje.value = "";

    // Crear la burbuja de la IA en estado de carga efímera
    const respuestaBotDiv = document.createElement("div");
    respuestaBotDiv.className = "bot-message";
    respuestaBotDiv.innerHTML = "<b>Bot:</b> <span class='loading'>⏳ Pensando...</span>";
    contenedorChat.appendChild(respuestaBotDiv);
    contenedorChat.scrollTop = contenedorChat.scrollHeight;

    try {
        // Inicializar la petición HTTP POST hacia el servidor FastAPI asíncrono
        const respuesta = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: textoMensaje,
                customer_id: "usr-nexus-enterprise-01"
            })
        });

        // Validar el estatus de red antes de abrir el flujo de sockets
        if (!respuesta.ok) {
            throw new Error(`Error de red en el clúster: ${respuesta.status}`);
        }

        // Limpiar el estado de carga para comenzar a escribir los tokens en vivo
        respuestaBotDiv.innerHTML = "<b>Bot:</b> ";

        // ⚠️ OPERACIÓN CRÍTICA NATIVA: Leer el cuerpo de la respuesta como un flujo binario continuo
        const lectorStream = respuesta.body.getReader();
        const decodificadorTexto = new TextDecoder("utf-8");

        while (true) {
            // Leer el fragmento del búfer de red asíncronamente
            const { value: fragmentoBinario, done: flujoTerminado } = await lectorStream.read();
            
            if (flujoTerminado) {
                break; // El canal gRPC del backend cerró la transmisión con éxito
            }

            // Transformar los bytes binarios a texto plano legible (tokens)
            const tokenTexto = decodificadorTexto.decode(fragmentoBinario, { stream: true });
            
            // Inyectar el token letra por letra en la interfaz web de forma fluida
            respuestaBotDiv.innerHTML += tokenTexto;
            
            // Deslizar automáticamente el scroll hacia abajo para acompañar la escritura de la IA
            contenedorChat.scrollTop = contenedorChat.scrollHeight;
        }

    } catch (error) {
        console.error("❌ Fallo en el puente de transmisión web:", error);
        respuestaBotDiv.innerHTML = "<b>Bot:</b> <span style='color: #f38ba8;'>❌ Error de comunicación con la malla de Kubernetes. Revisa tus puentes de red.</span>";
    }
}

// Escuchar el evento de la tecla Enter para agilizar el chat en la consola gráfica
document.getElementById("message-input").addEventListener("keypress", function(evento) {
    if (evento.key === "Enter") {
        enviarMensaje();
    }
});
