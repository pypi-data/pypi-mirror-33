#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@author: yanglei
'''
from gevent import monkey;monkey.patch_all()
import gevent
from gevent.pool import Group
import logging
import time
import random
from copy import deepcopy
import signal

from pyfly.flyrpc import Server, Client, Message
from pyfly.events import task_fail, task_success
from pyfly.flystate import display_interval, ShareData, ShareGraphData
import socket
logger = logging.getLogger("**pyfly.runners**")



class FlyMaster(object):
    def __init__(self, server_ip="127.0.0.1", server_port=5555):
        self.server = Server(server_ip, server_port)
        self.greenlet = Group()
        self.share_data = ShareData()
        self.work_status = "stop" # stop , running, stopping
        self.work_start_time = None
       
    @property
    def slave_node(self):
        return self.share_data.slave_node
    
    @property
    def task_node(self):
        return self.share_data.task_node
    
    @property
    def error_info_node(self):
        return self.share_data.error_node
    
    @property
    def slave_num(self):
        return self.share_data.slave_num
    
    @property
    def client_count(self):
        return self.share_data.client_count
    
    @property
    def hatch_rate(self):
        return self.share_data.hatch_rate
    
    @property
    def ready_slave(self):
        return self.share_data.ready_slave
        
    def distribute_work(self):
        logger.debug("Send test work to slave")
        slave_num = self.slave_num
        ready_slave_num = self.ready_slave
        
        if slave_num != ready_slave_num:
            logger.warning("Some slaves is not ready now! wait a moment ,or give a stop command.")
            return
        
        if slave_num == 0:
            logger.warning("Slave num is 0, you need to create some slaves!")
            return
        
        client_count = self.client_count
        hatch_rate = self.hatch_rate
        slave_num_clients = client_count // slave_num
        remainders = client_count % slave_num
        slave_hatch_rate = hatch_rate / slave_num
        work_id = 1

        for i in range(self.slave_num):  
            data = {
                "hatch_rate":slave_hatch_rate,
                "count":slave_num_clients,
                "work_id": work_id
            }
            if remainders:
                data["count"] += 1
                remainders -= 1
            work_id += 1
            if data["count"] == 0:
                break
            logger.debug("To slave%d :msg type = hatch, msg data = %s" % (i, data))
            self.server.send(Message("hatch", data, None))
        self.work_status = "running"
        self.work_start_time = 0
        self.get_run_graph_data()
    
    def stop_task(self):
        self.work_status = "stopping"
        for i in range(self.slave_num):
            logger.debug("To slave%d :msg type = stop, msg data = None" % i)
            self.server.send(Message("stop", None, None))
        
    def quit_slaves(self):
        for i in range(self.slave_num):
            logger.debug("To slave%d :msg type = quit, msg data = None" % i)
            self.server.send(Message("quit", None, None))
    
    def handle_message(self):
        while True:
            msg = self.server.recv()
            logger.debug("Recv msg, msg.type=%s, msg.data=%s, msg.node_id=%s" % (msg.type, msg.data, msg.node_id))
            
            if msg.type.lower() == "run_info":
                self.handle_run_info_msg(msg)

            # update slave status    
            else:
                sd = ShareData()
                sn = self.slave_node
                if msg.type.lower() == "quit":
                    if msg.node_id in sn:
                        sn.pop(msg.node_id)
                
                if msg.type.lower() == "ready":
                    if msg.node_id in sn:
                        sn[msg.node_id]["status"] = "ready"
                    else:
                        sn[msg.node_id] = {"status": "ready"}
    
                if msg.type.lower() == "stop":
                    sd = ShareData()
                    sn = self.slave_node
                    if msg.node_id in sn:
                        sn[msg.node_id]["status"] = "stop"
                    else:
                        sn[msg.node_id] = {"status": "stop"}
                    
                if msg.type.lower() == "hatch":
                    sd = ShareData()
                    sn = self.slave_node
                    if msg.node_id in sn:
                        sn[msg.node_id]["status"] = "hatch"
                    else:
                        sn[msg.node_id] = {"status": "hatch"}

                sd.slave_num = sn.slave_num
                sd.ready_slave = sn.ready_now
                sd.slave_node = sn
                    

    
    def handle_run_info_msg(self, msg):
        if not msg.data:
            return
        run_info = msg.data
        _slave = msg.node_id
        _fly_num = run_info.get("fly_num", 0)
        _index = run_info.get("index", 0)
        self.work_start_time = run_info.get("start_time", 0)
        
        # update slave_node
        sn = self.slave_node
        tn = self.task_node
        en = self.error_info_node
        sn.setdefault(_slave, {})
        sn[_slave]["fly_num"] = _fly_num
            
        for i, j in run_info.items():
            
            # task info handle
            if isinstance(j, dict) and "task_num" in j:
                _task_num = j.get("task_num", 0)
                _fail_num = sum(j.get("error_info", {}).values())
                _max_response_time = j.get("max_response_time", 0)
                _min_response_time = j.get("min_response_time", 0)
                _total_response_time = j.get("total_response_time", 0)
                
                # update error_info_node
                en = en + j.get("error_info", {})
                
                # update task_node
                tn.setdefault(i, {})
                tn[i]["task_num"] = _task_num + tn[i].get("task_num", 0)
                tn[i]["fail"] = _fail_num + tn[i].get("fail", 0)
                tn[i]["total_response_time"] = _total_response_time + tn[i].get("total_response_time", 0)
                now_max = tn[i].get("max_response_time", 0)
                tn[i]["max_response_time"] = _max_response_time if _max_response_time > now_max else now_max
                
                now_min = tn[i].get("min_response_time", 0)
                
                if _min_response_time != 0:
                    if now_min == 0:
                        tn[i]["min_response_time"] = _min_response_time
                    else:
                        tn[i]["min_response_time"] = _min_response_time if _min_response_time < now_min else now_min

                
                # update slave node
                sn[_slave]["task_num"] = sn[_slave].get("task_num", 0) + _task_num
                sn[_slave]["fail"] = sn[_slave].get("fail", 0) + _fail_num
                
                
                s_now_max = sn[_slave].get("max_response_time", 0)
                sn[_slave]["max_response_time"] = _max_response_time if _max_response_time > s_now_max else s_now_max

                s_now_min = sn[_slave].get("min_response_time", 0)
                
                if _min_response_time != 0:
                    if s_now_min == 0:
                        sn[_slave]["min_response_time"] = _min_response_time
                    else:
                        sn[_slave]["min_response_time"] = _min_response_time if _min_response_time < s_now_min else s_now_min
                
        self.share_data.slave_node = sn
        self.share_data.task_node = tn
        self.share_data.error_node = en

        logger.debug("Slave_node is %s" % self.slave_node)
        logger.debug("Task_node is %s" % self.task_node)
        logger.debug("Error_node is %s" % self.error_info_node)
                
    def get_run_graph_data(self):
        sgd = ShareGraphData()
        sd = ShareData()
        sgd.reset()
        interval = display_interval
        while True:
            if self.work_status == "stop":
                logger.info("Test stop, get_run_graph_data loop break!")
                return
            
            if not self.work_start_time:
                gevent.sleep(0.001)
                continue               
            logger.debug("sd.task_node=%s" % sd.task_node)
            logger.debug("sd.slave_node=%s" % sd.slave_node)
            time_index_list = sgd.time_index_list
            fly_num_list = sgd.fly_num_list
            task_num_list = sgd.task_num_list
            tps_list = sgd.tps_list
            
            now = time.time()
            
            # fist data
            if not sgd.last_time_index:
                sgd.last_time_index = now - self.work_start_time            
             
            time_index = now - self.work_start_time
            fly_num = sd.slave_node.fly_num
            task_num = sd.slave_node.task_num

            # update fly_num_list task_num_list tps_num_list, time_index_list
            fly_num_list.append(fly_num)
            task_num_list.append(task_num)
            
            tps_list.append(task_num/(now - self.work_start_time))
            time_index_list.append(time_index)
            
            # update response_stream fail_stream
            tn = sd.task_node
            for i, j in tn.items():
                
                #update response_stream
                last_response_time = sgd.last_response_dict.get(i, 0)
                last_task_num = sgd.last_task_num_dict.get(i, 0)
                _task_num = j.get("task_num", 0)
                _total_response_time = j.get("total_response_time", 0)
                
                add_task_num = _task_num - last_task_num
                sgd.response_stream_dict.setdefault(i, [])
                
                # padding if no data before
                if len(sgd.response_stream_dict[i]) < (len(sgd.time_index_list) - 1):
                    padding_data = 0

                    sgd.response_stream_dict[i].extend(
                            [padding_data]*(len(sgd.time_index_list) - 1 - len(sgd.response_stream_dict[i])))
                
                if add_task_num:
                    sgd.response_stream_dict[i].append((_total_response_time - last_response_time)/add_task_num)
                else:
                    no_add_task_data = 0
                    sgd.response_stream_dict[i].append(no_add_task_data)
                
                sgd.last_response_dict[i] = _total_response_time
                sgd.last_task_num_dict[i] = _task_num
                
                #update fail_stream
                last_fail_num = sgd.last_fail_dict.get(i, 0)
                _fail_num = j.get("fail", 0)
                
                sgd.fail_stream_dict.setdefault(i, [])
                
                if len(sgd.fail_stream_dict[i]) < (len(sgd.time_index_list) - 1):
                    padding_data = 0
                        
                    sgd.fail_stream_dict[i].extend(
                            [padding_data]*(len(sgd.time_index_list) - 1 - len(sgd.fail_stream_dict[i])))
                
                sgd.fail_stream_dict[i].append(_fail_num - last_fail_num)
                sgd.last_fail_dict[i] = _fail_num
                
            sgd.update_last_data()
            
            if self.work_status == "stopping" and self.slave_node.fly_num == 0:
                self.work_status = "stop"
                continue
            logger.debug("sgd.response_stream_dict=%s" % sgd.response_stream_dict)
            logger.debug("sgd.fail_steam_dict=%s" % sgd.fail_stream_dict)
            gevent.sleep(interval)

    def _debug(self):
        self.greenlet.spawn(self.handle_message)
        def a():
            gevent.sleep(10)
            print("start")
            self.distribute_work()
        self.greenlet.spawn(a)
        self.greenlet.join()



class FlySlave(object):
    '''
    arguments:
        host(str): ip of master, like "127.0.0.1"
        zmqport(int): zmqport of master like 5555
        fly_queen(FlyQueen object): like FlyQueen()
    '''
    
    START = "start"
    RUN = "run"
    STOP = "stop"
    READY = "ready"
    INIT = "init"
    STOPPING = "stopping"
    QUIT = "quit"
     
    def __init__(self, host="127.0.0.1", zmqport=5555, fly_queen=None):
        '''
        submit_data
            |
            task1
                |
                max_response_time
                |
                min_response_time
                |
                total_response_time
                ...
            |
            ...
            |
            taskn
            |
            fly_count
            |
            error_info
                |
                "error1": num
                |
                "error2": num
                |
                ...
                
        like this:
        {'fly_num':1,
        "index": 1, 
        'task2': {'task_num': 1, 'min_response_time': 3, 'total_response_time': 3, 'max_response_time': 3}, 
        'task': {'task_num': 3, 'min_response_time': 2, 'total_response_time': 2.5, 'error_info': {'fail1': 1}, 'max_response_time': 3}}

        '''
        self.greenlet = Group()
        self.task_group = Group()
        self.client = Client(host=host, port=zmqport)
        self.fly_queen = fly_queen # FlyQueen object
        self.count = 0
        self.hatch_rate = 1.0
        self.work_id = 1
        self.status = self.INIT
        self.slave_id = socket.gethostname() + "_" + str(int(time.time()) + random.randint(1, 20000))
        self.start_time = None
        self.submit_data = {}
        
        global task_success 
        task_success += self.on_task_success
        
        global task_fail
        task_fail += self.on_task_fail

    def run(self):  
        signal.signal(signal.SIGINT, self.slave_exit)  
        signal.signal(signal.SIGTERM, self.slave_exit)  
        self.greenlet.spawn(self.handle_message)
        self.status = self.READY
        self.client.send(Message(self.status, None, self.slave_id))
        self.greenlet.join()
    
    def slave_exit(self, signum, frame):
        self.status = self.QUIT
        logger.debug("Send quit info to master")
        self.client.send(Message("quit", None, self.slave_id))
        exit()
    

    def on_task_success(self, task_name, response_time):
        
        task_run_info = self.submit_data.get(task_name, {})
        task_run_info["task_num"] = task_run_info.get("task_num", 0) + 1
        if not task_run_info.get("total_response_time", None):
            task_run_info["total_response_time"] = response_time
            task_run_info["max_response_time"] = response_time
            task_run_info["min_response_time"] = response_time
        else:
            task_run_info["total_response_time"] = response_time + task_run_info["total_response_time"]
            task_run_info["max_response_time"] = response_time if response_time > task_run_info["max_response_time"] else task_run_info["max_response_time"]
            task_run_info["min_response_time"] = response_time if response_time < task_run_info["min_response_time"] else task_run_info["min_response_time"]
        self.submit_data[task_name] = task_run_info
    
    def on_task_fail(self, task_name, error_name, response_time):
        task_run_info = self.submit_data.get(task_name, {})
        task_run_info["task_num"] = task_run_info.get("task_num", 0) + 1
        
        # update response time
        if not task_run_info.get("total_response_time", None):
            task_run_info["total_response_time"] = response_time
            task_run_info["max_response_time"] = response_time
            task_run_info["min_response_time"] = response_time
        else:
            task_run_info["total_response_time"] = response_time + task_run_info["total_response_time"]
            task_run_info["max_response_time"] = response_time if response_time > task_run_info["max_response_time"] else task_run_info["max_response_time"]
            task_run_info["min_response_time"] = response_time if response_time < task_run_info["min_response_time"] else task_run_info["min_response_time"]
        
        task_error_info = task_run_info.get("error_info", {})
        if error_name in task_error_info:
            task_error_info[error_name] += 1
        else:
            task_error_info[error_name] = 1
        task_run_info["error_info"] = task_error_info
            
        self.submit_data[task_name] = task_run_info
    
    
    def handle_message(self):

        while True:
            msg = self.client.recv() # ******switch to hub*******
            logger.info("recv: type=%s, data=%s, node_id=%s" %(msg.type, msg.data, msg.node_id))
            if msg.type.lower() == "hatch":
                if self.status == self.READY or self.status == self.STOP:
                    try:
                        self.count = msg.data["count"]
                        self.work_id = msg.data["work_id"] # slave work id
                        self.hatch_rate=msg.data["hatch_rate"]
                        self.status = self.START
                        self.fly_queen.work_id = self.work_id
                        self.fly_queen.work_count = self.count
                        
                        self.greenlet.spawn(self.run_task)
                        self.greenlet.spawn(self.submit_run_info)
                        self.client.send(Message("hatch", None, self.slave_id))
                    except:
                        logger.error("Hatch msg data error! check server code please!")
                else:
                    logger.warning("I`m hatching now, but get a new work again, this work will be throw away")
                    continue
            
            if msg.type.lower() == "stop":
                self.fly_queen.zone_oper = False
                self.fly_queen.rezone_oper = True
                # add for stop task free cach of slave
                self.status = self.STOPPING
                logger.debug("Stopping slaves...")
                self.fly_queen.kill_son()
                s = time.time()
                while (time.time()-s) <((self.fly_queen.task_set.max_wait/1000) + 10):
                    logger.debug("task num is %s" % len(self.task_group))
                    if len(self.task_group) == 0:
                        break
                    gevent.sleep(0.5)
                else:
                    self.task_group.kill(block=True)
                
                self.client.send(Message("stop", None, self.slave_id))
                
                # for next test
                self.status = self.STOP
                
            if msg.type.lower() == "status":
                self.client.send(Message(self.status, None, self.slave_id))
    
    def run_task(self):
        assert self.fly_queen.task_set, "You should give a task_set class to fly queen!"
        self.status = self.RUN
        wait = 1.0/self.hatch_rate
        self.start_time = time.time()
        for i in range(self.count):
            if i >0:
                self.fly_queen.zone_oper = False
                self.fly_queen.rezone_oper = False
            fly = self.fly_queen.spawn()
            self.task_group.spawn(fly.run)
            logger.debug("spawn fly son %s" % i)
            gevent.sleep(wait)
            
    
    def submit_run_info(self):
        '''
        '''
        index = 0
        while True:
            
            gevent.sleep(display_interval)
            index += 1
            sub_data = deepcopy(self.submit_data)
            logger.debug("Submit data:%s" % sub_data)
            self.submit_data = {}
            sub_data["index"] = index
            sub_data["fly_num"] = len(self.task_group)
#             sub_data["submit_time"] = time.time()
            sub_data["start_time"] = self.start_time
            self.client.send(Message("run_info", sub_data, self.slave_id))
            
            if self.status == self.STOP and sub_data["fly_num"]==0:
                logger.info("Test stopped, submit run_info loop break.")
                return



if __name__ == "__main__":

    x = FlySlave()
    
    

