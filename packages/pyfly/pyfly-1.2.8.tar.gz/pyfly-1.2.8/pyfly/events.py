#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@author: yanglei
'''
import traceback
import time
import logging

logger = logging.getLogger("pyfly.events")

class EventHook(object):
    """
    Simple event class used to provide hooks for different types of events

    Here's how to use the EventHook class::

        my_event = EventHook()
        def on_my_event(a, b, **kw):
            print "Event was fired with arguments: %s, %s" % (a, b)
        my_event += on_my_event
        my_event.fire(a="foo", b="bar")
    """

    def __init__(self):
        self._handlers = []

    def __iadd__(self, handler):
        self._handlers.append(handler)
        return self

    def __isub__(self, handler):
        self._handlers.remove(handler)
        return self

    def fire(self, *args,**kwargs):
        for handler in self._handlers:
            handler(*args, **kwargs)

task_success = EventHook()
task_fail = EventHook()

def auto_submit_task(weight=1, task_name=None, raise_err=False, debug=False):
    '''
    
    '''
    func = None
    if callable(weight):
        func = weight
        raise_err = False
        weight = 1
        task_name = None
        
    def wapper(func):
        
        def inner(*args, **kwargs):
            if not task_name:
                tn = func.__name__
            else:
                tn = task_name
            try:
                s = time.time()
                re = func(*args, **kwargs)
                e = time.time()
                task_success.fire(task_name=tn, response_time=e-s)
                return re
            except Exception as ex:
                e = time.time()
                run_data = kwargs.get("run_data", None) or (args[1] if len(args) > 1 else None)
                web_enter = ">>>>>"
                log_enter = "\n"
                if debug:
                    error_name = traceback.format_exc()
                else:
                    error_name = str(ex)
                    
                error_info = error_name + log_enter + ("run_data = %s" % str(run_data))
                error_name = error_name + web_enter + ("run_data = %s" % str(run_data))
                logger.error(error_info)
                task_fail.fire(task_name=tn, error_name=error_name, response_time=e-s)
                if raise_err:
                    raise
        inner.fly_task_weight = weight
        
        return inner
    
    if func:
        return wapper(func)
    else:
        return wapper



if __name__ == "__main__":
    
    @auto_submit_task
    def xx(y):
        if y:
            time.sleep(3)
        else:
            time.sleep(1)
            raise RuntimeError("haha")
    
    @auto_submit_task
    def yy(y):
        if y:
            time.sleep(3)
        else:
            time.sleep(1)
            raise RuntimeError("haha")
    xx(0)
    yy(1)
    

    
