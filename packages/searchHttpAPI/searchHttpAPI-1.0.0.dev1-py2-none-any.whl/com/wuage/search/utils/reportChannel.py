#-*- coding: utf-8 -*-
# ------ wuage.com testing team ---------
# __author__ : jianxing.wei@wuage.com

import requests

"""
    todo
    消息推送接口，读取运行报告根据条件推送消息到指定的IM group
"""
class DingIM():
    WEBHOOK_TOKEN = "https://oapi.dingtalk.com/robot/send?access_token=488041f9be3af5962af3370b10dbb1328ca06c35d53c2560788e33ceb5346842"
    # msgTemplate='{"msgtype":"text","text":{"content":"{content}"},"at":{"atMobiles":[{mbs}],"isAtAll":false}}'
    query= {}
    def __init__(self , msg="" , level=0 , names=""):
        self.level=level
        self.names=names
        self.msg='{"msgtype":"text","text":{"content":"'+msg+('"},"at":{"atMobiles":[')+names+'],"isAtAll":false}}'
    def pushMsg(self):
        print("trans msg is : "+self.msg)
        headers = {"Content-Type": "application/json" ,"charset":"utf-8"}
        resp=requests.post(url=self.WEBHOOK_TOKEN , data=self.msg.encode('utf-8') , headers=headers).content
        print(resp)
    # def pushMsg(self , msg , msgfrom ):
    #     print("trans msg is : " + msg)
    #     if self.query[msgfrom] is not None:
    #         self.query[msgfrom]
    #     else:
    #         self.query[msg]=1
    #     headers = {"Content-Type": "application/json", "charset": "utf-8"}
    #     resp = requests.post(url=self.WEBHOOK_TOKEN, data=msg.encode('utf-8'), headers=headers).content
    #     print(resp)

if __name__ == "__main__":

    msg="搜索关键词推荐接口包含无推荐"
    names='"13520309744","魏建星"'
    ding=DingIM(msg,'1',names)
    ding.pushMsg()