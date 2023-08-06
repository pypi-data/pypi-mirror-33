#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@author: yanglei
'''
import time

from pyfly import task, async_task, TaskDataQueue, TaskSet, FlySlave, FlyQueen, task_fail, task_success, sleep, auto_submit_task

    
class MyTest(TaskSet):
    
    min_wait = 100
    max_wait = 200
    
    def on_start(self, run_data):
        print("exec on_start function %s" % run_data)
        
#     @async_task
#     def my_async_task(self, run_data):
#         while True:
#             print("do async_task %s" % run_data)
#             sleep(1)
        
    @task(1)
    def task1(self, run_data):
        s = time.time()
        print("task1 run, run data is %s" %run_data)
        sleep(0.1)
        e = time.time()
        task_success.fire(task_name="task1", response_time=e-s)
        
        
    @task(1)
    def task2(self, run_data):
        s = time.time()
        print("task2 run, run data is %s" %run_data)
        sleep(0.1)
        e = time.time()
        task_success.fire(task_name="task2", response_time=e-s)
        
    @task(1)
    def task3(self, run_data):
        s = time.time()
        print("task3 run, run data is %s" % run_data)
        sleep(0.1)
        e = time.time()
        task_fail.fire(task_name="task3", error_name="something error", response_time=e-s)
    
    @auto_submit_task(1)
    def task4(self, run_data):
        print("task4")
        
    def on_stop(self, run_data):
        print("test stop, exec on_stop function %s" % run_data)


def get_run_data():
    data = TaskDataQueue()
    for i in range(10000):
        data.put(i)
    return data
    
class MyFly(FlyQueen):
    task_data = get_run_data()
    task_set = MyTest

if __name__ == "__main__":
    import logging
    logging.basicConfig(level = logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    s = FlySlave(fly_queen=MyFly(), host="10.86.4.4")
    s.run()
