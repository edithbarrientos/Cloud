document.getElementById('send-btn').addEventListener('click', enviarMensaje);
document.getElementById('user-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter' || e.keyCode === 13) {
        e.preventDefault();
        enviarMensaje();
    }
});

async function enviarMensaje() {
    const input = document.getElementById('user-input');
    const msgText = input.value.trim();
    if (!msgText) return;

    input.value = '';
    appendMessage(msgText, 'user-msg');

    const botMessageDiv = appendMessage('⏳ Pensando...', 'bot-msg');

    try {
        const response = await fetch('/api/chat/stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: msgText,
                customer_id: 'usr-nexus-web-ui',
                source: 'web-browser'
            })
        });

        if (!response.ok) {
            let detalleError = `HTTP ${response.status} (${response.statusText})`;
            try {
                const errorJson = await response.json();
                detalleError += ` - Detalle: ${JSON.stringify(errorJson.detail || errorJson)}`;
            } catch (e) {
                const textoPlano = await response.text();
                if (textoPlano) detalleError += ` - Raw: ${textoPlano.substring(0, 150)}...`;
            }
            throw new Error(detalleError);
        }

        botMessageDiv.innerText = '';
        botMessageDiv.classList.add('streaming-cursor');

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        const chatBox = document.getElementById('chat-box');

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            const chunkText = decoder.decode(value, { stream: true });
            botMessageDiv.appendChild(document.createTextNode(chunkText));
            chatBox.scrollTop = chatBox.scrollHeight;
        }

    } catch (error) {
        console.error(`[NEXUS-UI-STREAM-ERROR] ${new Date().toISOString()} - Falló la comunicación con el backend:`, error);
        botMessageDiv.innerHTML = `<div>❌ <strong>Error en el flujo de la IA:</strong></div><pre style="white-space: pre-wrap; margin: 5px 0 0 0; font-family: monospace; font-size: 11px; background: rgba(0,0,0,0.2); padding: 5px; border-radius: 4px;">${error.message}</pre>`;
        botMessageDiv.style.color = '#f38ba8';
    } finally {
        botMessageDiv.classList.remove('streaming-cursor');
    }
}

function appendMessage(text, className) {
    const chatBox = document.getElementById('chat-box');
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', className);
    msgDiv.innerText = text;
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    return msgDiv;
}

window.addEventListener('error', function(event) {
    console.error(`[GLOBAL-UI-FATAL] Error en ejecución: ${event.message} en ${event.filename}:${event.lineno}`);
});
window.addEventListener('unhandledrejection', function(event) {
    console.error('[UNHANDLED-PROMISE-ERROR] Promesa rota sin control:', event.reason);
});
