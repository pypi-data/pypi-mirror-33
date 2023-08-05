#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@author: yanglei
'''

from gevent import monkey;monkey.patch_all()
import gevent
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import logging

from pyfly.flystate import display_interval, ShareData, ShareGraphData
from pyfly.runners import FlyMaster


logger = logging.getLogger("**pyfly.web**")
app = dash.Dash(__name__)
app.title = "pyfly"
SD = ShareData()
SGD = ShareGraphData()
APP_STATUS = "INIT"
fly_master = None# FlyMaster()
icon_url = "http://www.runwalkcrawl.com/wp-content/uploads/NatureBlackFlies-01-BlackFlies.jpg"
'''
"http://www.runwalkcrawl.com/wp-content/uploads/NatureBlackFlies-01-BlackFlies.jpg"
'''

def create_operation_div(): 
    
    r = html.Div([
        html.Div(dcc.Input(id='flynum-input-box', placeholder='虚拟用户数', style={'width': '80%', 'top':"50%","left":"50%", "height":"80%"}) ,
                 style={"height":"40px", "width": "20%", "display": "inline-block","margin": "auto"}),
        html.Div(dcc.Input(id='hatchrate-input-box', placeholder='虚拟用户生成速率（个/s）', style={'width': '80%', 'top':"50%","left":"50%","height":"80%"}) ,
                 style={"height":"40px", "width": "20%", "display": "inline-block",
                        "margin": "auto"}),
        html.Div(html.Button('开始', id='start-button', style={"text-align": "center", "font-size": "12px", 'width': '80%', "height":"80%"}),
                 style={"height":"40px", "width": "15%", "display": "inline-block",
                        "margin": "auto"}),
        html.Div(html.Button('停止', id='stop-button', style={"text-align": "center", "font-size": "12px", 'width': '80%', "height":"80%"}),
                 style={"height":"40px", "width": "15%", "display": "inline-block",
                        "margin": "auto"}),
        html.Div(html.P('总slave：', id='slavenum-item', style={"text-align": "right", "font-size": "16px", 
                                                                             'width': '100%', "height":"100%", "font-family":"Arial"}),
                 style={"height":"40px", "width": "10%", "display": "inline-block",
                        "margin": "auto"}),
        html.Div(html.P('0', id='slavenum-value', style={"text-align": "left", "font-size": "16px", 'width': '100%', "height":"100%",
                                                           "font-family":"Arial"}),
                 style={"height":"40px", "width": "5%", "display": "inline-block",
                        "margin": "auto"}),
        html.Div(html.P('可用slave：', id='readyslavenum-item', style={"text-align": "right", "font-size": "16px", 
                                                                             'width': '100%', "height":"100%", "font-family":"Arial"}),
                 style={"height":"40px", "width": "10%", "display": "inline-block",
                        "margin": "auto"}),
        html.Div(html.P('0', id='readyslavenum-value', style={"text-align": "left", "font-size": "16px", 'width': '100%', "height":"100%",
                                                           "font-family":"Arial"}),
                 style={"height":"40px", "width": "5%", "display": "inline-block",
                        "margin": "auto"}),
                  
        ],
        style={"margin-top":"2%",
               "margin-bottom":"2%",
                "margin-right":"5%",
                "margin-left":"5%",
                }
        )
    
    return r

def create_img_div():
    r = html.Div([html.Img(src=icon_url, 
                          alt="fly", width=str(214), height=str(209), 
                          style={"display": "block", "margin": "auto"}),
                  html.H4("——by杨磊" , style={"text-align": "right", "margin-right":"500px"})
                  ],
                 
                 style={"margin": "auto"})
    return r

def create_graph_flys():
    r = html.Div(
        [
        dcc.Graph(
            figure=go.Figure(),
            id = "fly-num-graph"
            )
            ],
        style={"margin-top":"2%",
               "margin-bottom":"2%",
               "margin-right":"5%",
               "margin-left":"5%",
        }
        )
    return r

def create_graph_total_tasks():
    r = html.Div(
        [
        dcc.Graph(
            figure=go.Figure(),
            id = "task-num-graph"
            )
            ],
        style={"margin-top":"2%",
               "margin-bottom":"2%",
               "margin-right":"5%",
               "margin-left":"5%",
        }
        )
    return r

def create_graph_tps():
    r = html.Div(
        [
        dcc.Graph(
            figure=go.Figure(),
            id = "tps-graph"
            )
            ],
        style={"margin-top":"2%",
               "margin-bottom":"2%",
               "margin-right":"5%",
               "margin-left":"5%",
        }
        )
    return r

def create_graph_average_response():
    r = html.Div(
        [
        dcc.Graph(
            figure=go.Figure(),
            id = "average-response-graph"
            )
            ],
        style={"margin-top":"2%",
               "margin-bottom":"2%",
               "margin-right":"5%",
               "margin-left":"5%",
        }
        )
    return r

def create_graph_fail():
    r = html.Div(
        [
        dcc.Graph(
            figure=go.Figure(),
            id = "fail-graph"
            )
            ],
        style={"margin-top":"2%",
               "margin-bottom":"2%",
               "margin-right":"5%",
               "margin-left":"5%",
        }
        )
    return r

def create_task_pie():
    r = html.Div(
        [
        dcc.Graph(
            figure=go.Figure(),
            id = "task-pie"
            )
            ],
        style={"margin-top":"2%",
               "margin-bottom":"2%",
               "margin-right":"5%",
               "margin-left":"5%",
        }
        )
    return r

def create_slave_pie():
    r = html.Div(
        [
        dcc.Graph(
            figure=go.Figure(),
            id = "slave-pie"
            )
            ],
        style={"margin-top":"2%",
               "margin-bottom":"2%",
               "margin-right":"5%",
               "margin-left":"5%",
        }
        )
    return r

def create_task_bar():
    r = html.Div(
        [
        dcc.Graph(
            figure=go.Figure(),
            id = "task-bar"
            )
            ],
        style={"margin-top":"2%",
               "margin-bottom":"2%",
               "margin-right":"5%",
               "margin-left":"5%",
               }
        )
    return r

def create_slave_bar():
    r = html.Div(
        [
        dcc.Graph(
            figure=go.Figure(),
            id = "slave-bar"
            )
            ],
        style={"margin-top":"2%",
               "margin-bottom":"2%",
               "margin-right":"5%",
               "margin-left":"5%",
        }
        )
    return r

def create_error_info_table():
    r = html.Div([html.Table(
                            id = "error-table",
                            style = {"border-collapse": "collapse",
                                     "border": "1px solid black",
                                     "width":"90%",
                                     "margin": "auto"}
                             )
                  ],
        id = "error-table-div",
        style={"margin-top":"2%",
               "margin-bottom":"2%",
               "margin-right":"5%",
               "margin-left":"5%",
        }
        )
    return r


app.layout = html.Div(
    [
    dcc.Interval(
            id='interval-component',
            interval=display_interval*1000, # in milliseconds
            n_intervals=0
        ),
    dcc.Interval( # for slave num info change
            id='interval-component1',
            interval=display_interval*1000, # in milliseconds
            n_intervals=0
        ),
     create_img_div(),
     html.Hr(), # line
     create_operation_div(),
     html.H3("结果展示", style={"text-align": "center"}),
     html.Hr(),
     create_graph_flys(),
     create_graph_total_tasks(),
     create_graph_tps(),
     create_graph_average_response(),
     create_graph_fail(),
     create_task_pie(),
     create_slave_pie(),
     create_task_bar(),
     create_slave_bar(),
     create_error_info_table()
     ]
    )

@app.callback(Output("interval-component", "interval"), 
              inputs=[Input("start-button", "n_clicks"),
                      Input("readyslavenum-value", "children")],
              state =[State("start-button", "disabled"),
                      State("slavenum-value", "children")]
              )
def update_interval(n1, ready_slave_num, start_disabled, slave_num):

    if APP_STATUS == "INIT" or (APP_STATUS == "STOP" and int(ready_slave_num)==int(slave_num)):
        return 36000*1000
    else:
        return display_interval*1000


@app.callback(Output("stop-button", "disabled"), 
              inputs=[Input("start-button", "n_clicks"),
                      Input("stop-button", "n_clicks"),
                      ],
              state =[State("start-button", "disabled"),
                      State("stop-button", "disabled"),
                      State("flynum-input-box", "value"),
                      State("hatchrate-input-box", "value")])
def update_stop_button(n1, n2, start_disabled, stop_disabled, flynum, hatchrate):
    global APP_STATUS
    global SD
        
    # click start button
    if isinstance(n1, int) and (not start_disabled):
        APP_STATUS = "START"
        
        SD.reset()
        try:
            SD.client_count = int(flynum)
        except:
            pass
        try:
            SD.hatch_rate = float(hatchrate)
        except:
            pass
        logger.info("client count is %s, hatch rate is %s" % ((SD.client_count, SD.hatch_rate)))
        fly_master.greenlet.spawn(fly_master.distribute_work)
        
        return False
    
    # click stop button
    elif isinstance(n2, int) and (not stop_disabled):
        APP_STATUS = "STOP"

        fly_master.greenlet.spawn(fly_master.stop_task)
        return True
    else:
        
        if APP_STATUS == "START":
            return False
        else:
            return True
    
@app.callback(Output("start-button", "disabled"), 
              inputs=[Input("start-button", "n_clicks"),
                      Input("stop-button", "n_clicks")],
              state =[State("start-button", "disabled"),
                      State("stop-button", "disabled")]
              )
def update_start_button(n1, n2, start_disabled, stop_disabled):
    # click start
    if isinstance(n1, int) and (not start_disabled):
        return True
    
    #click stop
    elif isinstance(n2, int) and (not stop_disabled):
        return False
    else:
        if APP_STATUS == "START":
            return True
        else:
            return False
        

@app.callback(Output("fly-num-graph", "figure"),
    inputs = [Input("interval-component", "n_intervals")]
    )
def update_fly_num_graph(n):
    if APP_STATUS == "INIT":
        return go.Figure()
    
    # 
    SGD = ShareGraphData()
    figure=go.Figure(
        data=[go.Scatter(x=SGD.time_index_list, y=SGD.fly_num_list, name="虚拟用户")],
        layout=dict(title = '虚拟用户数',
                    xaxis = dict(title = '时间'),
                    yaxis = dict(title = '个数'),
                    )
        )
    return figure


@app.callback(Output("task-num-graph", "figure"),
    inputs = [Input("interval-component", "n_intervals")]
    )
def update_total_tasks_graph(n):
    if APP_STATUS == "INIT":
        return go.Figure()
    
    SGD = ShareGraphData()
    figure=go.Figure(
        data=[go.Scatter(x=SGD.time_index_list, y=SGD.task_num_list, name="总任务数")],
        layout=dict(title = '总任务执行数',
                    xaxis = dict(title = '时间'),
                    yaxis = dict(title = '个数'),
                    )
        )
    return figure

@app.callback(Output("tps-graph", "figure"),
    inputs = [Input("interval-component", "n_intervals")]
    )
def update_tps_graph(n):
    if APP_STATUS == "INIT":
        return go.Figure()
    
    SGD = ShareGraphData()
    figure=go.Figure(
        data=[go.Scatter(x=SGD.time_index_list, y=SGD.tps_list, name="每秒任务数")],
        layout=dict(title = '每秒任务数',
                    xaxis = dict(title = '时间'),
                    yaxis = dict(title = '个数'),
                    )
        )
    return figure

@app.callback(Output("average-response-graph", "figure"),
    inputs = [Input("interval-component", "n_intervals")]
    )
def update_average_response_graph(n):
    if APP_STATUS == "INIT":
        return go.Figure()
    
    SGD = ShareGraphData()
    if not SGD.response_stream_dict:
        return go.Figure()

    data = []
    
    for i, j in SGD.response_stream_dict.items():
        y_data = j
        data.append(go.Scatter(x=SGD.time_index_list, y=y_data, name=i)) 
        
    figure=go.Figure(
        data=data,
        layout=dict(title = '每%s秒平均响应时间' % display_interval,
                    xaxis = dict(title = "测试时间"),
                    yaxis = dict(title = '响应时间(s)'),
                    )
        )
    return figure


@app.callback(Output("fail-graph", "figure"),
    inputs = [Input("interval-component", "n_intervals")]
    )
def update_fail_graph(n):
    if APP_STATUS == "INIT":
        return go.Figure()
    
    SGD = ShareGraphData()
    
    if not SGD.fail_stream_dict:
        return go.Figure()
    
    data = []
    
    for i, j in SGD.fail_stream_dict.items():
        y_data = j
        data.append(go.Scatter(x=SGD.time_index_list, y=y_data, name=i)) 
        
    figure=go.Figure(
        data=data,
        layout=dict(title = '每%s秒失败任务数' % display_interval,
                    xaxis = dict(title = "测试时间"),
                    yaxis = dict(title = '个数'),
                    )
        )
    return figure

@app.callback(Output("task-pie", "figure"),
    inputs = [Input("interval-component", "n_intervals")]
    )
def update_task_pie(n):
    if APP_STATUS == "INIT":
        return go.Figure()
    
    data = []
    labels = []
    values = []
    for i, j in SD.task_node.request_num_dict.items():
        labels.append(i)
        values.append(j)  
    data.append(go.Pie(labels=labels, values=values, domain= {"x": [0, .48]}, name= "总任务数", 
                       hoverinfo = "label+percent+name",hole=.4, text="ALL", textposition= "inside",
                       textinfo='value+percent'))
    
    labels = []
    values = []
    for i, j in SD.task_node.fail_dict.items():
        labels.append(i)
        values.append(j)
    data.append(go.Pie(labels=labels, values=values, domain= {"x": [.52, 1]}, name= "失败数", 
                       hoverinfo = "label+percent+name",hole=.4, text="FAIL", textposition= "inside",
                       textinfo='value+percent'))
    
    figure=go.Figure(
        data=data,
        layout={
                "title": "各任务执行总数和错误数",
                "annotations": [
                    {
                        "font": {
                            "size": 20
                        },
                        "showarrow": False,
                        "text": "ALL",
                        "x": 0.22,
                        "y": 0.5
                    },
                    {
                        "font": {
                            "size": 20
                        },
                        "showarrow": False,
                        "text": "FAIL",
                        "x": 0.78,
                        "y": 0.5
                    }
                ]
            }
        )
    return figure
    
@app.callback(Output("slave-pie", "figure"),
    inputs = [Input("interval-component", "n_intervals")]
    )
def update_slave_pie(n):
    if APP_STATUS == "INIT":
        return go.Figure()
    
    data = []
    labels = []
    values = []
    for i, j in SD.slave_node.request_num_dict.items():
        labels.append(i)
        values.append(j)  
    data.append(go.Pie(labels=labels, values=values, domain= {"x": [0, .48]}, name= "总任务数", 
                       hoverinfo = "label+percent+name",hole=.4, text="ALL", textposition= "inside",
                       textinfo='value+percent'))
    
    labels = []
    values = []
    for i, j in SD.slave_node.fail_dict.items():
        labels.append(i)
        values.append(j)
    data.append(go.Pie(labels=labels, values=values, domain= {"x": [.52, 1]}, name= "失败数", 
                       hoverinfo = "label+percent+name",hole=.4, text="FAIL", textposition= "inside",
                       textinfo='value+percent'))
    
    figure=go.Figure(
        data=data,
        layout={
                "title": "各slave任务总数和错误数",
                "annotations": [
                    {
                        "font": {
                            "size": 20
                        },
                        "showarrow": False,
                        "text": "ALL",
                        "x": 0.22,
                        "y": 0.5
                    },
                    {
                        "font": {
                            "size": 20
                        },
                        "showarrow": False,
                        "text": "FAIL",
                        "x": 0.78,
                        "y": 0.5
                    }
                ]
            }
        )
    return figure

@app.callback(Output("task-bar", "figure"),
    inputs = [Input("interval-component", "n_intervals")]
    )
def update_task_bar(n):
    if APP_STATUS == "INIT":
        return go.Figure()
    
    data = []
    
    x=[]
    y=[]
    for i, j in SD.task_node.max_response_time_dict.items():
        x.append(i)
        y.append(j)
        
    data.append(go.Bar(x=x, y=y, name="MAX", text=y, textposition = 'auto'))
    
    x=[]
    y=[]
    for i, j in SD.task_node.min_response_time_dict.items():
        x.append(i)
        y.append(j)
        
    data.append(go.Bar(x=x, y=y, name="MIN", text=y, textposition = 'auto'))
    
    figure=go.Figure(
        data = data,
        layout = go.Layout(
                barmode = 'group',
                title = "各任务最大最小响应时间(s)"
                )
    

        )
    
    return figure
    
@app.callback(Output("slave-bar", "figure"),
    inputs = [Input("interval-component", "n_intervals")]
    )
def update_slave_bar(n):
    if APP_STATUS == "INIT":
        return go.Figure()
    
    data = []
    
    x=[]
    y=[]
    for i, j in SD.slave_node.max_response_time_dict.items():
        x.append(i)
        y.append(j)
        
    data.append(go.Bar(x=x, y=y, name="MAX", text=y, textposition = 'auto'))
    
    x=[]
    y=[]
    for i, j in SD.slave_node.min_response_time_dict.items():
        x.append(i)
        y.append(j)
        
    data.append(go.Bar(x=x, y=y, name="MIN", text=y, textposition = 'auto'))
    
    figure=go.Figure(
        data = data,
        layout = go.Layout(
                barmode = 'group',
                title = "各slave最大最小响应时间(s)"
                )
        )
    
    return figure

@app.callback(Output("error-table", "children"),
    inputs = [Input("interval-component", "n_intervals")]
    )
def update_error_info_table(n):
    if APP_STATUS == "INIT":
        return 
    tb_body=[]
    
    for i, j in SD.error_node.items():
        tb_body.append(html.Tr([html.Td(k, style={"border": "1px solid black"}) for k in (i,j)]))
    
    r = [html.Tr([html.Th(col, style={"border": "1px solid black", 
                                      "background-color":"green"}) for col in ["Error Name", "Number"]])] + tb_body
    
    return r

@app.callback(Output("slavenum-value", "children"),
    inputs = [Input("interval-component1", "n_intervals")]
    )
def update_slavenum_value(n):
    return str(SD.slave_num)

@app.callback(Output("readyslavenum-value", "children"),
    inputs = [Input("interval-component1", "n_intervals")]
    )
def update_readyslavenum_value(n):
    return str(SD.ready_slave)



    
class WebApp(object):
    '''
    class of webapp init arguments is :
    host(str): ip of the web app default is "127.0.0.1".
    webport(int): the port for webserver default is 8050
    zmqport(int): the port for zmq transform default is 5555
    
    '''
    
    def __init__(self, host="127.0.0.1", webport=8050, zmqport=5555, debug=False):
        self.host = host
        self.webport = webport
        self.zmqport = zmqport
        self.debug = debug
        global fly_master
        fly_master = FlyMaster(server_ip=host, server_port=zmqport)
        self.greenlet = fly_master.greenlet
        
        if not debug:
            werkzeug_log = logging.getLogger("werkzeug")
            werkzeug_log.setLevel(logging.ERROR)
    
    def run(self):
        self.greenlet.spawn(fly_master.handle_message)
        self.greenlet.spawn(app.run_server, host=self.host, port=self.webport, debug=self.debug)
        self.greenlet.join()
        

if __name__ == "__main__":
    # logger.setLevel(logging.ERROR)
    x = WebApp()
    x.run(debug=False)
