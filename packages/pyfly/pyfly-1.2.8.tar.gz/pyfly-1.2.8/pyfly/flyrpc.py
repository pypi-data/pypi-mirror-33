#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@author: yanglei
'''

from gevent import monkey; monkey.patch_all()
import msgpack
import logging

import zmq.green as zmq
logger = logging.getLogger("**pyfly.rpc**")

class Message(object):
    def __init__(self, message_type, data, node_id):
        self.type = message_type#.decode() if hasattr(message_type, "decode") else message_type
        self.data = data
        self.node_id = node_id#.decode() if hasattr(node_id, "decode") else node_id
    
    def serialize(self):
        return msgpack.dumps((self.type, self.data, self.node_id))
    
    @classmethod
    def unserialize(cls, data):
        msg = cls(*msgpack.loads(data, encoding='utf-8'))
        return msg
    
class BaseSocket(object):

    def send(self, msg):
        self.sender.send(msg.serialize())
    
    def recv(self):
        data = self.receiver.recv()
        try:
            return Message.unserialize(data)    
        except Exception as ex:
            logger.error(str(ex))
            logger.error("data = %s\n" % data)

    
class Server(BaseSocket):
    def __init__(self, host="127.0.0.1", port=6666):
        context = zmq.Context()
        self.receiver = context.socket(zmq.PULL)
        self.receiver.bind("tcp://%s:%i" % (host, port))
         
        self.sender = context.socket(zmq.PUSH)
        self.sender.bind("tcp://%s:%i" % (host, port+1))
     
 
class Client(BaseSocket):
    def __init__(self, host="127.0.0.1", port=6666):
        context = zmq.Context()
        self.receiver = context.socket(zmq.PULL)
        self.receiver.connect("tcp://%s:%i" % (host, port+1))
         
        self.sender = context.socket(zmq.PUSH)
        self.sender.connect("tcp://%s:%i" % (host, port))
    

if __name__ == "__main__":
    import gevent
    from gevent.pool import Group
    from locust.rpc.zmqrpc import Server, Client
    def test_server():
        s = Server("10.86.4.4", 8888)
        i = 0
        while True:
            i += 1
            data = Message(1,{"a":1, "b":2},i)
            gevent.sleep(1)
            s.send(data)
            print("s:send")
            r_data = s.recv()
            print("receive:", r_data.type, r_data.data, r_data.node_id, type(r_data.type), type(r_data.node_id))
            print(r_data.data["a"], r_data.data["b"], type(r_data.data["a"]), type(r_data.data["b"]))
            gevent.sleep(1)
    
    def test_client():
        c = Client("10.86.4.4", 8888)
        while True:
            gevent.sleep(1)
            data = Message("c",{"a":1, "b":"2"},2)
            c.send(data)
            print("c, send")
            r_data = c.recv()
            print("c rec:",r_data.type, r_data.data, r_data.node_id)

            gevent.sleep(1)
            
    def test_client2():
        c = Client("10.86.4.4", 8888)
        while True:
            gevent.sleep(0)
            data = Message("c2",3,5)
            c.send(data)
            print("c2, send")
            
            r_data = c.recv()
            print("c2 rec:",r_data.type, r_data.data, r_data.node_id)

            gevent.sleep(1)
    def testtest():
        while True:
            print(1)
            gevent.sleep(1)
    
    group = Group()
    
    group.spawn(test_client)
    # group.spawn(test_client2)
    group.spawn(test_server)
    # group.spawn(testtest)
    
    group.join()
            


