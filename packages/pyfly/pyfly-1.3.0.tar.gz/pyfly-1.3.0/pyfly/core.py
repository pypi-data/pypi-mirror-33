#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@author: yanglei
core of fly:
'''

import gevent
import random
import logging
from gevent.pool import Group
import traceback

logger = logging.getLogger("**pyfly.core**")

def sleep(*args, **kwargs):
    '''
    sleep function 
    the same as gevent.sleep
    '''
    gevent.sleep(*args, **kwargs)

def task(weight=1, timeout=0):
    """
    Used as a convenience decorator to be able to declare tasks for a TaskSet 
    inline in the class. Example::
    
        class ForumPage(TaskSet):
            @task(100)
            def read_thread(self):
                pass
            
            @task(7)
            def create_thread(self):
                pass
    """
    
    def decorator_func(func):
        func.fly_task_weight = weight
        func.fly_task_timeout = timeout
        return func
    
    """
    Check if task was used without parentheses (not called), like this::
    
        @task
        def my_task()
            pass
    """
    if callable(weight):
        func = weight
        weight = 1
        timeout = 0
        return decorator_func(func)
    else:
        return decorator_func
    
def async_task(func):
    '''
    Used as a convenience decorator to be able to declare async_tasks for a TaskSet 
    inline in the class. Example::
    
        class ForumPage(TaskSet):
            @async_task
            def read_thread(self):
                pass
    '''
    func.async_task = True
    return func

class MetaTaskSet(type):
    ''' task set
    '''
    def __new__(cls, classname, bases, classDict):
        new_tasks = []
        new_async_tasks = []
        for base in bases:
            if hasattr(base, "tasks") and base.tasks:
                new_tasks += base.tasks
            
            if hasattr(base, "async_tasks") and base.async_tasks:
                new_async_tasks += base.async_tasks
        
        for item in classDict.values():
            if hasattr(item, "fly_task_weight"):
                for i in range(item.fly_task_weight):
                    new_tasks.append(item)
            
            if hasattr(item, "async_task"):
                new_async_tasks.append(item)
                    
            if hasattr(item, "weight") and item.weight and issubclass(item, TaskSet):
                for i in range(item.weight):
                    new_tasks.append(item)
            
        classDict["tasks"] = new_tasks
        classDict["async_tasks"] = new_async_tasks
        
        return type.__new__(cls, classname, bases, classDict)

class TaskSet(metaclass=MetaTaskSet):
    ''' task set class
        you should not rewrite __init__ function, if you need, must do like this:
            class A(TaskSet):
                def __init__(self, your_argument1, your_argument2, *args, **kwargs):
                    super(A, self).__init__(*args, **kwargs)
                    
        !!! every test function must have a run_data argument, this must be fist argument
    '''
    min_wait = 500 
    max_wait = 1000
    weight = 1
    stop = False
    async_task_group = None # for manage async_tasks
    _async_task_group = []
    error_cont = False


    def __init__(self, run_data=None):
        self.run_data = run_data
        self.async_task_list = []
        
    def kill(self):
        self.stop = True

    def run(self):
        
        self.stop = False
        if hasattr(self, "on_start"):
            self.on_start(self.run_data)
        
        if hasattr(self, "async_tasks") and self.async_tasks:
            for task in self.async_tasks:
                t = self.async_task_group.spawn(task, self, self.run_data)
                self._async_task_group.append(t)
            
        while True:
            
            try:
                if self.stop:
                    if hasattr(self, "on_stop"):
                        self._async_task_group = []
                        self.on_stop(self.run_data)
                    return 

                task = self.schedule_task()
                if hasattr(task, "tasks") and task.tasks:
                    if task.async_tasks:
                        error_log = "async tasks must be defined in topper task_set class"
                        error_log += "\nThis tasks must be put to topper task_set class:\n"
                        for i in task.async_tasks:
                            error_log += "%s\n" % i 
                        raise AttributeError(error_log)
                    else:
                        sub_task = task(self)
                        sub_task.run_data = self.run_data
                        sub_task.run()
                else:
                    task(self, self.run_data)
                
            except ReScheduleException as e:
                if e.self_raise:
                    e.self_raise = False
                    raise e
                else:
                    self._sleep()
            except Exception as e:
                logger.error(traceback.format_exc())
                
                if not self.error_cont:
                    # kill async task when task run fail!
                    for t in self._async_task_group:
                        t.kill(block=True)
                    raise
            else:
                self._sleep()
            
                
    def _sleep(self):
        wait = random.randint(self.min_wait, self.max_wait)
        gevent.sleep(wait/1000.0)
        
    
    def schedule_task(self):
        return random.choice(self.tasks)
    
    def interrupt(self):
        raise ReScheduleException(True)

class ReScheduleException(Exception):
    def __init__(self, self_raise=True):
        self.self_raise = self_raise


class TaskDataQueue(object):
    '''
    Task data queue, it`s a singleton, you can insert data to it use the 'put' function, and you can get data from it use the "get" function
    if queue is empty, get function return None.
    example:
        a = TaskDataQueue()
        a.put({"mac":"000000000000", "ip":"127.0.0.1"})
        while True:
            print(a.get())
        
        >>>
        {"mac":"000000000000", "ip":"127.0.0.1"}
        {"mac":"000000000000", "ip":"127.0.0.1"}
        {"mac":"000000000000", "ip":"127.0.0.1"}
        {"mac":"000000000000", "ip":"127.0.0.1"}
        {"mac":"000000000000", "ip":"127.0.0.1"}
        ...
    '''
    value = []
    _value = []
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls,"_instance"):
            cls._instance = super(TaskDataQueue, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def get(self):
        l = len(self.value)
        if l:
            item = self.value.pop(0)
        else:
            return 
        self.value.append(item)
        return item
    
    def put(self, item):
        self.value.append(item)
        self._value.append(item)
    
    def _zone(self, index1, index2):
        if index1 >= len(self.value):
            index1 = -1
        self.value = self.value[index1: index2]
        
    def _rezone(self, index1, index2):
        if index1 >= len(self._value):
            index1 = -1
        
        self.value = self._value[:]
        self.value = self.value[index1:index2]
        
    def empty(self):
        if len(self.value):
            return False
        else:
            return True
        
        
class FlyQueen(object):
    
    task_set = TaskSet # taskset class or task set subclass
    task_data = TaskDataQueue() # siglone
    work_id = 0 #  slave runner object
    work_count = 0
    zone_oper = True
    rezone_oper = False
    _async_task_group = Group() # for manage async_tasks
    sons = []
    
    def spawn(self):
        if self.work_count:
            logger.debug("work_id of slave is %s, count is %s" %(self.work_id, self.work_count))
            
            if self.task_data and self.zone_oper:
                self.task_data._zone((self.work_id - 1)* self.work_count, self.work_id*self.work_count)
                logger.debug("zone task_data, after zone value is %s" % self.task_data.value)
                self.zone_oper = False
                
            elif self.task_data and self.rezone_oper:
                self.task_data._rezone((self.work_id - 1)* self.work_count, self.work_id*self.work_count)
                logger.debug(" Rezone task_data, after zone value is %s" % self.task_data.value)
                self.zone_oper = False
            else:
                pass
        
        run_data = self.task_data.get()
        son = self.task_set(run_data=run_data)
        logger.debug("fly queen spawn son %s" % run_data)
        if son.async_tasks:
            son.async_task_group = self._async_task_group
        self.sons.append(son)
        return son
    
    def kill_son(self):
        
        for son in self.sons:
            son.kill()  
        self.sons = []
        if len(self._async_task_group):
            
            self._async_task_group.kill(block=True) 
            logger.debug("kill async_tasks len of sync_task_group is %s" %len(self._async_task_group))
        self.sons = []
    

    

if __name__ == "__main__":
    t = TaskDataQueue()
    t.put(1)
    t.put(2)
    print(t.value)
    t._zone(1000,101)
    print(t.value)
#     
#     class A(TaskSet):
#         @task(weight=2)
#         def a(self,data):
#             print("A.a")
#             pass
#     class B(A):
#         @task
#         def b(self,data):
#             print("B.b")
#             pass
#          
#         @task
#         def bb(self,data):
#             print("B.bb")
#             
#         @async_task
#         def tt(self, data):
#             while True:
#                 print("haha")
#                 gevent.sleep(0.5)
#                 
#         @async_task
#         def ttt(self, data):
#             while True:
#                 print("hahaxxx")
#                 gevent.sleep(0.5) 
#          
#         class C(TaskSet):
#             weight=1
#             @task
#             def c(self,data):
#                 print("C.c")
#              
#             @task
#             def exit(self, data):
#                 print("exit")
#                 self.interrupt()
#                 
# #             @async_task
# #             def error(self, data):
# #                 while True:
# #                     print("hahaxxx")
# #                     gevent.sleep(0.5)
# #                     
# #             @async_task
# #             def error2(self, data):
# #                 while True:
# #                     print("hahaxxx")
# #                     gevent.sleep(0.5)
#             
#     z = B()
#     z.async_task_group = Group()
#     print(z.tasks)
#     z.run()
    

    