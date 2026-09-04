import asyncio
import grpc
import chatbot_pb2
import chatbot_pb2_grpc

async def test_streaming_local():
    print("🚀 Iniciando cliente de prueba gRPC Local...")
    
    # Conectarse directo al puerto de tu main.py local
    async with grpc.aio.insecure_channel('127.0.0.1:50051') as channel:
        stub = chatbot_pb2_grpc.ChatServiceStub(channel)
        
        # 🟢 PAYLOAD CORRECTO BAJO CONTRATO .PROTO
        request = chatbot_pb2.ChatRequest(
            raw_message="Hola, responde únicamente con un saludo corto de tres palabras.",
            customer_id="usr-nexus-local-test",
            source="terminal_mac"
        )
        
        print(f"📥 Enviando mensaje validado: '{request.raw_message}'")
        try:
            stream = stub.ProcesarMensajeStream(request)
            async for response in stream:
                if response.chunk_message:
                    # Imprimir los tokens letra por letra en tu pantalla en tiempo real
                    print(response.chunk_message, end="", flush=True)
            print("\n\n✅ Stream finalizado con éxito de forma asíncrona.")
        except grpc.RpcError as e:
            print(f"\n❌ Error en el test gRPC: {e.code()} - {e.details()}")

if __name__ == "__main__":
    asyncio.run(test_streaming_local())
