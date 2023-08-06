import itchat
from itchat.content import *
import json
import time
from .components import AI
from .components import weather

list_friends = []
switch_AI = True

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
    global switch_AI
    #通过文件助手控制是否开启AI自动回复
    if msg['ToUserName'] == 'filehelper':
        if msg['Text'] == 'start':
            switch_AI = True
            itchat.send('AI started', toUserName='filehelper')
        if msg['Text'] == 'stop':
            switch_AI = False
            itchat.send('AI stoped', toUserName='filehelper')
        return
    #备注为AI的用户自动使用AI回复
    if msg['User']['RemarkName'] == 'AI' and switch_AI==True:
        return AI.get_msg(msg['Text'])

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
#群发问候
def batch_message():
    global list_friends
    '''
    读取好友地址，调用接口定时发送天气预报
    
    for friend in list_friends:
        if friend['RemarkName'] == '张平' or friend['NickName']=='张平':
            result = weather._now('北京')
            itchat.send('@msg@'+result[1],friend.UserName)
            print(friend['City'])
    '''

def run():
    global list_friends
    itchat.auto_login(hotReload=True)
    list_friends = itchat.get_friends(update=True)
    batch_message()

    #with open('friends.json','w',encoding='utf-8') as f:
    #    f.write(json.dumps(list_friends,ensure_ascii=False))
    #print(len(result))
    itchat.run()
    