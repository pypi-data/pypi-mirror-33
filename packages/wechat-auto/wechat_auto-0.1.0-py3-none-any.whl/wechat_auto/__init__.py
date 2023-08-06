import itchat
from itchat.content import *
import json
import time
import threading
import os
import re
from .components import AI
from .components import weather

'''
全局变量
'''
LIST_FRIENDS = [] #好友列表
SWITCH_AI = False #是否开启AI自动回复
SWITCH_GREET = False #是否开启定时问候
ALLCOMMAND = "开启(关闭)AI回复\n开启(关闭)定时消息\n状态\n"

'''
#全部消息
@itchat.msg_register(INCOME_MSG)
def text_reply(msg):
    print(msg)
    return 'Hello'
'''

#文本消息
@itchat.msg_register(TEXT)
def msg_system(msg):
    global SWITCH_AI
    #通过文件助手控制各个模块开关
    if msg['ToUserName'] == 'filehelper':
        _command(msg)
        return
    #开启后自动回复
    if SWITCH_AI:
        return AI.get_msg(msg['Text'],msg['User']['PYQuanPin'])

def _command(msg):
    global SWITCH_AI
    global SWITCH_GREET
    if re.match(r'^help.*$',msg['Text']) != None:
        itchat.send(ALLCOMMAND, toUserName='filehelper')
    if re.match(r'^开启AI回复.*$',msg['Text']) != None:
        SWITCH_AI = True
        itchat.send('已经开启AI回复', toUserName='filehelper')
    if re.match(r'^关闭AI回复.*$',msg['Text']) != None:
        SWITCH_AI = False
        itchat.send('已经关闭AI回复', toUserName='filehelper')
    if re.match(r'^开启定时消息.*$',msg['Text']) != None:
        SWITCH_GREET = True
        itchat.send('已经开启定时消息', toUserName='filehelper')
    if re.match(r'^关闭定时消息.*$',msg['Text']) != None:
        SWITCH_GREET = False
        itchat.send('已经关闭定时消息', toUserName='filehelper')
    if re.match(r'^状态.*$',msg['Text']) != None:
        get_status()
    


'''
#系统消息
#UNDO, 删除好友用户记录到本地文档，定期清理好友
@itchat.msg_register(NOTE)
def msg_system(msg):
    print(msg)

#新好友请求
@itchat.msg_register(FRIENDS)
def add_friend(msg):
    print(msg)
    #延时接受好友请求
    #time.sleep(10)
    itchat.add_friend(**msg['Text'])# 该操作将自动将好友的消息录入，不需要重载通讯录
    #UNDO 新好友的打招呼信息,延迟后发送公众号信息
    itchat.send_msg('Nice to meet you!',msg['RecommendInfo']['UserName'])
'''
#获取当前机器人状态
def get_status():
    result = "当前时间为:"+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
    result += "机器人当前状态：\n"
    if SWITCH_AI:
        result += "AI回复功能: "+ "开启\n"
    else:
        result += "AI回复功能: "+ "关闭\n"
    if SWITCH_GREET:
        result += "定时问候功能: "+ "开启\n"
    else:
        result += "定时问候功能: "+ "关闭\n"
    itchat.send(result, toUserName='filehelper')


#定时问候 子线程
def batch_message(a):
    global SWITCH_GREET
    global LIST_FRIENDS
    #读取好友地址，调用接口定时发送天气预报
    while True:
        if (SWITCH_GREET):
            if time.localtime(time.time())[3]==21 and time.localtime(time.time())[4]==39:
                for friend in LIST_FRIENDS:
                    if friend['RemarkName'] == '咖喱' or friend['NickName']=='咖喱':
                        weather_brief = _get_location_weather(friend, weather.CITYS_WEATHER)
                        itchat.send('@msg@'+"早上好 "+weather_brief,friend.UserName)
        time.sleep(60)

def _get_location_weather(friend, weathers):
    if friend['City'] in weathers:
        return  weathers[friend['City']]
    if friend['Province'] in weathers:
        return  weathers[friend['Province']]
    if '北京' in weathers:
        return  weathers['北京']
    return ""


def run():
    global LIST_FRIENDS
    itchat.auto_login(hotReload=True)
    #获取天气
    weather.init()
    #获取好友
    LIST_FRIENDS = itchat.get_friends(update=True)
    #开启定时问候任务
    timing_greet = threading.Thread(target=batch_message,args=(1,))
    timing_greet.start()
    #with open('friends.json','w',encoding='utf-8') as f:
    #    f.write(json.dumps(list_friends,ensure_ascii=False))
    #print(len(result))
    get_status()
    itchat.run()
    