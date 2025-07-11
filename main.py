from flask import Flask, request, g
import requests
import yaml
import threading
import queue
import time
from datetime import datetime
import json
import requests
from flask import Flask, request, g
import yaml
from typing import Tuple
from src.run import run_passive_reply,run_event_detector,run_proactive_message,run_schedule_initialization,schedule_generator,user_ids
import os
from src.settings import API_KEY, BASE_URL

os.environ["OPENAI_API_BASE"] = BASE_URL
os.environ["OPENAI_API_KEY"] = API_KEY
app = Flask(__name__)

last_check=None
last_length=None
user_states = {}

#这是一个获得请求并生成回复的函数方法。
#第二个参数 methods 是一个选项，它指定了这个路由可以响应哪些类型的 HTTP 请求方法
@app.route('/', methods=["POST"]) 
def post_data():
    # send passive reply
    # global last_length,last_check,messages

    #从 HTTP 请求中获取 JSON 格式的数据，并将其存储在一个字典变量中
    #request.get_json() 是 Flask 的一个方法，它尝试解析请求体中的 JSON 数据，并将其转换为 Python 的字典（dict）或列表（list）
    raw_package: dict = request.get_json()
    #如果raw_package里面有message_type这个键值，就进行以下的一些信息存储
    if 'message_type' in raw_package:
        message_type = raw_package['message_type']
        #访问 raw_package 字典中 sender 键对应的值（这本身也是一个字典），然后进一步访问这个内部字典的 user_id 键
        user_id = raw_package['sender']['user_id']
        message = raw_package['message']
        #将这行信息加到对应user_id字典的"messages"键值下。
        user_states[user_id]["messages"].append({"role": "user", "content": message})
        print(f"user_id is {user_id}, messages are"+str(message))
        #进行回应对话生成
        response = run_passive_reply(user_id, message)
        #添加助手对话
        user_states[user_id]["messages"].append({"role": "assistant", "content":response})
        #输出的是特定用户的所有对话消息的总数，包括用户发送的消息和助手回复的消息。
        # 这可以帮助你了解到目前为止，该用户与助手之间进行了多少轮对话。
        print(f"messages length is {len(user_states[user_id]['messages'])}")

        # last_check is the user latest reply timing, last_length means the whole length in a round of conversation. 
        user_states[user_id]["last_check"]=time.time()
        user_states[user_id]["last_length"]=len(user_states[user_id]["messages"])
        print(f"{user_id}'s last length is "+str(user_states[user_id]["last_length"]))
    return 'ok'
#     user_states = {
#     "user1": {
#         "last_check": 1633036800,
#         "last_length": 0,
#         "messages": [             # 消息列表更新
#             {"role": "user", "content": "你好，你是谁？"},
#             {"role": "assistant", "content": "你好，我是你的助手。"},
#             {"role": "user", "content": "你能做什么？"}  # 新增的消息
#         ]
#     },
#     "user2": {
#         "last_check": 1633037000,
#         "last_length": 0,
#         "messages": [
#             {"role": "user", "content": "今天天气如何？"},
#             {"role": "assistant", "content": "今天晴天，气温23度。"}
#         ]
#     }
# }

#判断是否进行event detect，如果进行了就清空短期记忆
def event_detect():
    for user_id in user_ids:
        # judge whether single round of conversation end and prevent repeated detect.
        if time.time() - user_states[user_id]["last_check"] >= 60 and len(user_states[user_id]["messages"]) == user_states[user_id]["last_length"] and len(user_states[user_id]["messages"]) != 0:
            print(f"begin event detecting for {user_id}...")
            print(f"dialogue content in {user_id} is:{user_states[user_id]['messages']}")
            run_event_detector(user_id,user_states[user_id]["messages"])
            #经历了event detector之后，message清零
            user_states[user_id]["messages"]=[]
    #十秒钟检查一次
    threading.Timer(10, event_detect).start()

#从 YAML 配置文件中提取服务器的主机名（host）和端口号（port）
#host：这是从配置文件中提取的服务器的主机名，通常是服务器的域名或IP地址。
#port：这是从配置文件中提取的服务器的端口号，是一个整数，表示服务器监听的端口。
def get_host_port() -> Tuple[str, int]:
    with open('./config.yml', 'r', encoding='utf-8') as f:
        obj = yaml.load(f.read(), Loader = yaml.FullLoader)
    url = obj['servers'][0]['http']['post'][0]['url']
    host, port = url.replace('http://', '').split(':')
    return str(host), int(port)

#从reflection获取回顾之后，在每天23:59时生成每日计划
thread1 = threading.Thread(target=run_schedule_initialization)
#主动发送消息
thread2 = threading.Thread(target=run_proactive_message)

thread3 = threading.Thread(target=event_detect)

@app.route('/unity_chat', methods=["POST"])
def unity_post_data():
    raw_package: dict = request.get_json()
    
    user_id = raw_package.get("user_id", "unity_user")
    message = raw_package.get("message", "")

    # 如果这个用户还没有初始化
    if user_id not in user_states:
        user_states[user_id] = {
            "last_check": time.time(),
            "last_length": 0,
            "messages": []
        }

    # 加入用户消息
    user_states[user_id]["messages"].append({"role": "user", "content": message})
    print(f"[Unity] user_id: {user_id}, message: {message}")
    
    # 调用 ComPeer 的主回复逻辑
    response = run_passive_reply(user_id, message)

    # 记录助手回复
    user_states[user_id]["messages"].append({"role": "assistant", "content": response})
    user_states[user_id]["last_check"] = time.time()
    user_states[user_id]["last_length"] = len(user_states[user_id]["messages"])

    return {"reply": response}

if __name__ == '__main__':
    #字典initial reflection和user states的初始化：
    print(f'Begin to generate the schedule of.')
    initial_reflection = {}
    for user_id in user_ids:
        user_states[user_id] = {"last_check": time.time(), "last_length": None, "messages": []}
        initial_reflection[user_id]="用户尚未提供反思信息，请默认安排基础生活作息"
    #schedule_generator.initialize_schedule(initial_reflection)
    # first initialize schedule
    # schedule_generator.initialize_schedule(initial_reflection)
    print(f"user_ids is...{user_ids}")
    print("finish init!")
    print("[Init] 今日 schedule 初始化完成！")
    #提供 WSGI 服务器：gevent.pywsgi 提供了一个 WSGI 服务器，可以让你的 Flask、Django 或其他 WSGI 兼容的应用运行在 gevent 的异步框架上
    from gevent import pywsgi
    thread1.start()
    thread2.start()
    thread3.start()
    # host, port = get_host_port()
    # server = pywsgi.WSGIServer(
    #     listener=(host, port),
    #     application=app,
    #     log=None
    # )
    server = pywsgi.WSGIServer(
    listener=("0.0.0.0", 9000),  # 或你希望的端口
    application=app,
    log=None
)
    server.serve_forever()