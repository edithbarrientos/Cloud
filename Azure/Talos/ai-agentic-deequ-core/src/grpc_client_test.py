import asyncio
import logging
import sys
import os
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import grpc
import inference_pb2
import inference_pb2_grpc

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] grpc.native: %(message)s")
logger = logging.getLogger("grpc_native_client")

async def send_single_grpc_http2_payload(stub, worker_id: int) -> bool:
    trace_id = f"STRESS-GRPC-TRC-{worker_id}"
    
    metadata_map = {
        "execution_mode": "HTTP2_MULTIPLEXED_STREAM",
        "regulatory_framework": "internal_governance"
    }

    data_content = {
        "sensor_id": "ARM64-M3-STRESS-NODE",
        "metric_value": 0.95 + (worker_id * 0.0001),
        "region": "us-east-2"
    }

    # Inyecciones controladas intermitentes para disparar alertas en el servidor
    if worker_id % 200 == 0:
        metadata_map["regulatory_framework"] = "gdpr"
    if worker_id == 500:
        metadata_map["regulatory_framework"] = "lfpdppp"

    data_content["metadata"] = metadata_map

    # Simulación de quiebre criptográfico de linaje en el paso 300
    forced_previous_hash = "6ec8b75c05847c63227fe8d80c694318cab67509a5e4b8810fdaff5967d742a0"
    if worker_id == 300:
        forced_previous_hash = "" 

    request = inference_pb2.InferenceRequest(
        trace_id=trace_id,
        step_sequence=worker_id,
        previous_hash=forced_previous_hash,
        metadata=metadata_map,
        telemetry=inference_pb2.InferenceRequest.MetricsPayload(
            sensor_id=data_content["sensor_id"],
            metric_value=data_content["metric_value"],
            region=data_content["region"]
        ),
        security_integrity={"expected_json_hash": "6ec8b75c05847c63227fe8d80c694318cab67509a5e4b8810fdaff5967d742a0", "tenant_id": "tenant-retail-beta"}
    )

    try:
        response = await stub.ProcessInference(request, timeout=10.0)
        # Mantener el log descriptivo de la capa RAM solicitado
        logger.info(f"✅ [MAPPED_ACCEPTED] Traza: {response.trace_id} | Status: {response.status} | Layer: BUFFERED_IN_RAM")
        return response.status == "SUCCESS"
    except Exception as e:
        logger.error(f"❌ [gRPC_ERROR] Hilo {worker_id} caído: {str(e)}")
        return False

async def main(concurrency_level: int):
    server_address = "localhost:50051"
    logger.info(f"🔥 [gRPC_INIT] Abriendo canal permanente HTTP/2 hacia {server_address}")
    
    # Abrir descriptores masivos a nivel de socket gRPC para tolerar las 1000 llamadas concurrentes
    options = [
        ('grpc.max_receive_message_length', 100 * 1024 * 1024),
        ('grpc.max_send_message_length', 100 * 1024 * 1024),
        ('grpc.http2.max_pings_without_data', 0),
        ('grpc.http2.max_concurrent_streams', 1000) 
    ]

    async with grpc.aio.insecure_channel(server_address, options=options) as channel:
        stub = inference_pb2_grpc.InferenceEngineStub(channel)
        
        start_time = time.time()
        logger.info(f"⚡ [gRPC_LAUNCH] Disparando {concurrency_level} ráfagas binarias concurrentes de alta densidad...")
        
        tasks = [send_single_grpc_http2_payload(stub, i) for i in range(1, concurrency_level + 1)]
        results = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        success_count = sum(1 for r in results if r)
        failed_count = concurrency_level - success_count
        
        logger.info(f"========================================================================")
        logger.info(f"🏁 RESUMEN CONSOLIDADO DEL TEST DE ESTRÉS BINARIO NATIVO (HTTP/2)")
        logger.info(f"========================================================================")
        logger.info(f"📊 Total Inyecciones Procesadas : {concurrency_level}")
        logger.info(f"✅ Ráfagas Consolidadas Exitosas: {success_count}")
        logger.info(f"❌ Transacciones Caídas/Rechazadas: {failed_count}")
        logger.info(f"⏱️ Tiempo Total de Ejecución    : {total_time:.4f} segundos")
        logger.info(f"🚀 Rendimiento Binario Puro    : {concurrency_level / total_time:.2f} peticiones/seg")
        logger.info(f"========================================================================")

if __name__ == "__main__":
    # 🔥 1,000 PETICIONES SIMULTÁNEAS EN PARALELO ABSOLUTO
    concurrency = 1000
    asyncio.run(main(concurrency))
