#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@author: yanglei
fly run state
'''


display_interval = 3.0

class SlaveNode(dict):
    ''' record slave node 
    {
     "slave_id": {
                 "status":"ready",
                 "fly_num": 2,
                 "task_num":1,
                 "fail": 1,
                 'max_response_time':1,
                 "mini_response_time":2  
                 }
                 }
    }
    '''
    
    @property
    def slave_num(self):
        return len(self.keys())
    
    @property
    def fly_num(self):
        r = 0
        for i in self.values():
            r += i.get("fly_num", 0)
        
        return r
    
    @property
    def task_num(self):
        r = 0
        for i in self.values():
            r += i.get("task_num", 0)
        return r
    
    @property
    def ready(self):
        r=0
        for j in self.values():
            if j.get("status", "").lower() == "ready":
                r += 1
        return r
    
    @property
    def stop(self):
        r=0
        for j in self.values():
            if j.get("status", "").lower() == "stop":
                r += 1
        return r 
    
    @property
    def ready_now(self):
        r=0
        for j in self.values():
            if j.get("status", "").lower() == "ready" or j.get("status", "").lower()=="stop":
                r += 1 
        return r
    
    @property
    def fail_dict(self):
        r = {}
        for i, j in self.items():
            r[i] = j.get("fail", 0)
        return r
    
    @property
    def request_num_dict(self):
        r = {}
        for i, j in self.items():
            r[i] = j.get("task_num", 0)
        return r
        
    @property
    def max_response_time_dict(self):
        r = {}
        for i, j in self.items():
            r[i] = j.get("max_response_time", 0)
        return r
    
    @property
    def min_response_time_dict(self):
        r = {}
        for i, j in self.items():
            r[i] = j.get("min_response_time", 0)
        return r
    
class TaskNode(dict):
    ''' record slave node 
    {
     "task1": {
             "task_num":1,
             'max_response_time':1,
             "mini_response_time":2,
             "total_response_time":3,
             "fail" = 1,
             fail_stream=[],
             response_time_stream=[]
             ...
                 }
    }
    '''
    @property
    def request_num_dict(self):
        r = {}
        for i, j in self.items():
            r[i] = j.get("task_num", 0)
        return r
    
    @property
    def total_response_time_dict(self):
        r = {}
        for i, j in self.items():
            r[i] = j.get("total_response_time", 0)
        return r
    
    @property
    def fail_dict(self):
        r = {}
        for i, j in self.items():
            r[i] = j.get("fail", 0)
        return r
            
    @property
    def max_response_time_dict(self):
        r = {}
        for i, j in self.items():
            r[i] = j.get("max_response_time", 0)
        return r
    
    @property
    def min_response_time_dict(self):
        r = {}
        for i, j in self.items():
            r[i] = j.get("min_response_time", 0)
        return r
    
#     @property
#     def response_stream_dict(self):
#         r = {}
#         for i, j in self.items():
#             r[i] = j.get("response_stream", [])
#         return r
#     
#     @property
#     def fail_stream_dict(self):
#         r = {}
#         for i, j in self.items():
#             r[i] = j.get("fail_stream", [])
#         return r
    
class ErrorNode(dict):
    
    def __add__(self, other):
        for i, j in other.items():
            if i in self:
                self[i] += j
            else:
                self[i] = j
        
        return self
    
class ShareData(object):
    distribute_task = False
    slave_num = 0
    client_count = 1
    hatch_rate = 1
    ready_slave = 0
    slave_node = SlaveNode()
    task_node = TaskNode()
    error_node = ErrorNode()
    
    def __new__(cls, *arg, **kwargs):
        if hasattr(cls, "_cls"):
            return cls._cls
        else:
            cls._cls = super(ShareData, cls).__new__(cls, *arg, **kwargs)
            return cls._cls
        
    def reset(self):

        for i, j in self.slave_node.items():
            self.slave_node[i] = {"status": j.get("status", "ready")}
        
        self.task_node = TaskNode()
        self.error_node = ErrorNode()
        

class ShareGraphData(object):

    fly_num_list = []
    task_num_list = []
    tps_list = []
    time_index_list = []
    response_stream_dict = {}
    fail_stream_dict = {}
    last_time_index = 0
    last_task_num = 0
    last_response_dict = {}
    last_task_num_dict = {}
    last_fail_dict = {}
    
    def __new__(cls, *arg, **kwargs):
        if hasattr(cls, "_cls"):
            return cls._cls
        else:
            cls._cls = super(ShareGraphData, cls).__new__(cls, *arg, **kwargs)
            return cls._cls
        
    def update_last_data(self):
        if self.task_num_list:
            self.last_task_num = self.task_num_list[-1]
            
        if self.time_index_list:
            self.last_time_index = self.time_index_list[-1]
            
        
    def reset(self):
        self.fly_num_list = []
        self.task_num_list = []
        self.tps_list = []
        self.time_index_list = []
        self.response_stream_dict = {}
        self.fail_stream_dict = {}
        self.last_time_index = 0
        self.last_task_num = 0
        self.last_response_dict = {}
        self.last_fail_dict = {}
        self.last_task_num_dict = {}


if __name__ == "__main__":
    t =     {
     "slave_id": {
                 "status":"ready",
                 "fly_num":1,
                 "task_num":11,
                 "fail": 10,
                 'max_response_time':1,
                 "mini_response_time":2,
                 },
     "slave_id2": {
                 "status":"ready",
                 "fly_num": 2,
                 "task_num":11,
                 "fail": 10,
                 'max_response_time':1,
                 "mini_response_time":2,
                 }
             
    }
    x = SlaveNode()
    x.update(t)
    print(x.fail_dict)
    print(x.max_response_time_dict)
    print(x.ready)
    print(x.request_num_dict)
    print(x.fly_num)
    
    tt = {
     "task1": {
             "task_num":11,
             "fail":10,
             'max_response_time':12,
             "mini_response_time":2,
             "fail_stream":[1,3,],
             "response_stream":[3],
                 }
    }
    
    y = TaskNode()
    y.update(tt)
    print(y.request_num_dict)
    print(y.max_response_time_dict)
    print(y.fail_dict)
    print(y.fail_stream_dict)
    print(y.response_stream_dict)
    
    print("!!!!")
    x = ErrorNode()
    x.update({1:2,2:3})
    t = x + {2:1, 3:4}
    print(t)
    z = t + {1:-1, 5:6}
    print(z)
    
