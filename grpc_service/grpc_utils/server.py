import grpc
from concurrent import futures
from grpc_utils import insurance_service_pb2_grpc
from grpc_utils.service import InsuranceServiceServicer

class GRPCServer:
    def __init__(self, port: int = 50051):
        self.port = port
        self.server = None

    def start(self):
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        insurance_service_pb2_grpc.add_InsuranceServiceServicer_to_server(InsuranceServiceServicer(), self.server)
        # Only allow connections from localhost
        self.server.add_insecure_port(f"127.0.0.1:{self.port}")
        self.server.start()
        print(f"[gRPC] Server running on 127.0.0.1:{self.port}")

    def stop(self):
        if self.server:
            self.server.stop(0)
            print("[gRPC] Server stopped")