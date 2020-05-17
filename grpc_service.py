#! /usr/bin/env python
# -*- coding: utf-8 -*- 
from concurrent import futures
import time
import grpc
from grpc_proto import helloworld_pb2
from grpc_proto import helloworld_pb2_grpc
from grpc_proto import myworld_pb2
from grpc_proto import myworld_pb2_grpc

# 实现 proto 文件中定义的 GreeterServicer


class Greeter(helloworld_pb2_grpc.GreeterServicer):
    # 实现 proto 文件中定义的 rpc 调用
    def SayHello(self, request, context):
        print('SayHello receive %s' % request.name)
        return helloworld_pb2.HelloReply(message = 'hello {msg}'.format(msg = request.name))

    def SayHelloAgain(self, request, context):
        print('SayHelloAgain receive %s' % request.name)
        return helloworld_pb2.HelloReply(message='hello again {msg}'.format(msg = request.name))


class MyGreeter(myworld_pb2_grpc.MyGreeterServicer):
    # 实现 proto 文件中定义的 rpc 调用
    def DoSomething(self, request, context):
        print('SayHello receive %s' % request.name)
        return myworld_pb2.SomeReply(message = 'hello {msg}'.format(msg = request.name))


def serve():
    # 启动 rpc 服务
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    myworld_pb2_grpc.add_MyGreeterServicer_to_server(MyGreeter(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(60*60*24) # one day in seconds
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
