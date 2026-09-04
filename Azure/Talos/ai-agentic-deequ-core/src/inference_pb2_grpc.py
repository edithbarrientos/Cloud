# 🪄 STUB DE CONEXIÓN MULTIPLEXADA NATIVA POR FLUJO DE BYTES (HTTP/2 ENGINE)
import grpc
import inference_pb2

class InferenceEngineStub(object):
    def __init__(self, channel):
        self.ProcessInference = channel.unary_unary(
            '/inference.InferenceEngine/ProcessInference',
            # 🪄 Forzar el empaquetado y desempaquetado de bytes nativos sin pasar por Google Protoc
            request_serializer=lambda x: x.SerializeToString(),
            response_deserializer=inference_pb2.InferenceResponse.FromString,
        )

class InferenceEngineServicer(object):
    def ProcessInference(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

def add_InferenceEngineServicer_to_server(servicer, server):
    rpc_method_handlers = {
        'ProcessInference': grpc.unary_unary_rpc_method_handler(
            servicer.ProcessInference,
            # 🪄 Sincronización de des-serialización en el lado del servidor
            request_deserializer=inference_pb2.InferenceRequest.FromString,
            response_serializer=lambda x: x.SerializeToString(),
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        'inference.InferenceEngine', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
