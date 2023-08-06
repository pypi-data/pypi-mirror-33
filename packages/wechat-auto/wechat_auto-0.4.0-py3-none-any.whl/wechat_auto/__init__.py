import itchat
from itchat.content import *
import json
import time
import threading
import os
import re
import random
from .components import ai
from .components import weather

'''
全局变量
'''
LIST_FRIENDS = [] #好友列表
SWITCH_AI = False #是否开启AI自动回复
SWITCH_GREET = False #是否开启定时问候
ALLCOMMAND = "开启(关闭)AI回复\n开启(关闭)定时消息[,小时][,分钟]\n状态\n"
HOUR='8' #定时消息时针
MIN='0' #定时消息分针
GREETING=('Hi[愉快]','在一切开始之前，能不能请你关注一下我参与创作的公众号“北城故事会”[可怜]\n在我的朋友圈就能找到\n当然决定权在你啦,手动感谢O(∩_∩)O哈哈~','顺便一提，如果发现了哪篇是我写的文章，说不准有小惊喜哦[偷笑]')#加好友后的打招呼信息
MAX_COUNT = 100 #问候用户每天最大数量


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
        return ai.get_msg(msg['Text'],msg['User']['PYQuanPin'])





#系统消息
#删除好友用户记录到本地文档，定期清理好友
@itchat.msg_register(NOTE)
def msg_system(msg):
    #如果拉黑或者删除，则读取昵称写入文件
    if re.match(r'^.*开启了朋友验证，你还不是他（她）朋友.*$',msg['Text'])!=None or re.match(r'^消息已发出，但被对方拒收了.*$',msg['Text'])!=None:
        nickname=msg['User']['NickName']
        with open("deleted_friend",'a+',encoding='utf8') as deleted_friend:
            deleted_friend.write(nickname+'\n')

#新好友请求
@itchat.msg_register(FRIENDS)
def add_friend(msg):
    print(msg)
    #延时接受好友请求
    #time.sleep(10)
    itchat.add_friend(**msg['Text'])# 该操作将自动将好友的消息录入，不需要重载通讯录
    #新好友的打招呼信息,延迟后发送公众号信息
    time.sleep(2)
    itchat.send_msg(GREETING[0],msg['RecommendInfo']['UserName'])
    time.sleep(5)
    itchat.send_msg(GREETING[1],msg['RecommendInfo']['UserName'])
    time.sleep(3)
    itchat.send_msg(GREETING[2],msg['RecommendInfo']['UserName'])


def _command(msg):
    global SWITCH_AI
    global SWITCH_GREET
    global HOUR
    global MIN
    if re.match(r'^help.*$',msg['Text']) != None:
        itchat.send(ALLCOMMAND, toUserName='filehelper')
    if re.match(r'^开启AI回复.*$',msg['Text']) != None:
        SWITCH_AI = True
        itchat.send('已经开启AI回复', toUserName='filehelper')
    if re.match(r'^关闭AI回复.*$',msg['Text']) != None:
        SWITCH_AI = False
        itchat.send('已经关闭AI回复', toUserName='filehelper')
    if re.match(r'^开启定时消息.*$',msg['Text']) != None:
        #如果命令设置了时间，则设置时间
        t_hour = re.search(r'^开启定时消息,*([0-9]*),*([0-9]*).*$',msg['Text'])[1]
        t_min = re.search(r'^开启定时消息,*([0-9]*),*([0-9]*).*$',msg['Text'])[2]
        if t_hour!="":
            HOUR = t_hour
        if t_min!="":
            MIN = t_min
        SWITCH_GREET = True
        itchat.send('已经开启定时消息,时间为'+HOUR+"点"+MIN+"分", toUserName='filehelper')
    if re.match(r'^关闭定时消息.*$',msg['Text']) != None:
        SWITCH_GREET = False
        itchat.send('已经关闭定时消息', toUserName='filehelper')
    if re.match(r'^状态.*$',msg['Text']) != None:
        get_status()
    

#获取当前机器人状态
def get_status():
    result = "当前时间为:"+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
    result += "机器人当前状态：\n"
    if SWITCH_AI:
        result += "AI回复功能: "+ "开启\n"
    else:
        result += "AI回复功能: "+ "关闭\n"
    if SWITCH_GREET:
        result += "定时问候功能: 开启,"+HOUR+"点"+MIN+"分\n"
    else:
        result += "定时问候功能: "+ "关闭\n"
    itchat.send(result, toUserName='filehelper')


#定时问候 子线程
def batch_message(a):
    global SWITCH_GREET
    global LIST_FRIENDS
    friends = LIST_FRIENDS.copy()
    #读取好友地址，调用接口定时发送天气预报
    while True:
        #如果当前是凌晨1点，则重新初始化天气数据
        if time.localtime(time.time())[3]==1 and time.localtime(time.time())[4]==0:
            weather.init()

        if (SWITCH_GREET):
            if time.localtime(time.time())[3]==int(HOUR) and time.localtime(time.time())[4]==int(MIN):
                index = 0
                for friend in LIST_FRIENDS:
                    if index>MAX_COUNT:
                        break
                    weather_brief = _get_location_weather(friend, weather.CITYS_WEATHER)
                    itchat.send('@msg@'+"早上好 "+weather_brief,friend.UserName)
                    index += 1
                    time.sleep(1)
        time.sleep(60)

def _get_location_weather(friend, weathers):
    if friend['City'] in weathers:
        return  '\n'+weathers[friend['City']]
    if friend['Province'] in weathers:
        return  '\n'+weathers[friend['Province']]
    if '北京' in weathers:
        return  '\n'+weathers['北京']
    return ""


def run():
    global LIST_FRIENDS
    itchat.auto_login(hotReload=False)
    #获取天气
    weather.init()
    #获取好友
    LIST_FRIENDS = itchat.get_friends(update=True)
    random.shuffle(LIST_FRIENDS)
    #开启定时问候任务
    timing_greet = threading.Thread(target=batch_message,args=(1,))
    timing_greet.start()
    #with open('friends.json','w',encoding='utf-8') as f:
    #    f.write(json.dumps(list_friends,ensure_ascii=False))
    #print(len(result))
    get_status()
    itchat.run()
    