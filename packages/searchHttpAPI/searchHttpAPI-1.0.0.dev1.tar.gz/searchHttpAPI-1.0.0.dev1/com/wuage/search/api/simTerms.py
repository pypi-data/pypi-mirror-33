#-*- coding: utf-8 -*-
# ------ wuage.com testing team ---------
# __author__ : jianxing.wei@wuage.com
import requests
import json
import os
class SuggestTerms():
    # 搜索用关键词
    kws = []
    def __init__(self, fileName):
        # 读取搜索关键词
        for line in open(fileName, 'r' , encoding='utf-8').readlines():
            # print(line)
            self.kws.append(line.strip())

    @property
    def get_allkws(self):
        return self.kws

    def getSuggestionTerms(self , kw):
        url = "https://s.wuage.com/suggest/getSimilarWordByKeyword?callback=whk&keyword="+ kw +"&size=30&type=1"
        testurl = "http://172.17.4.22:8241/suggest/getSimilarWordByKeyword?callback=whk&keyword=" + kw + "&size=30&type=1"
        items=list()
        resp=requests.get(url=url)
        content=resp.content.decode('utf-8')
        jsonstr=content[4:-2]

        # print(jsonstr)
        obj=json.loads(jsonstr)
        # print(type(obj))
        for info in obj:
            items.append(info['key'])
        print(items)
        return kw , items



if __name__ == "__main__":
    suggest=SuggestTerms("/Users/wuage/PycharmProjects/searchHttpAPI/com/wuage/search/api/kws.txt")
    suggest.getSuggestionTerms(kw="不锈钢")



