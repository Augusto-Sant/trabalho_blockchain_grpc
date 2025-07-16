from grpc_utils.server import GRPCServer

if __name__ == "__main__":
    server = GRPCServer(port=50051)
    server.start()
    print("gRPC server started, waiting for termination...")
    server.server.wait_for_termination()
