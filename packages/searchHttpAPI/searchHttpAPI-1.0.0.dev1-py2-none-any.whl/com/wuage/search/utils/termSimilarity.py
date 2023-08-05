#-*- coding: utf-8 -*-
# ------ wuage.com testing team ---------
# __author__ : jianxing.wei@wuage.com
"""
    相似度badcases：
        1：搜索词长度大于推荐词 如用户搜索300不锈钢圆棒 推荐terms 可能会包含304不锈钢圆棒
        2：搜索词为不绣钢 推荐词应该考虑包含 不锈钢
        3：搜索词为螺纹钢 推荐词应该包含类似 热轧类钢筋 xxx螺纹钢 ...
        4：xxx价格，如螺纹钢价格
        5：
"""

from difflib import SequenceMatcher
import jellyfish
class SimilarityTools():
    def buildinSimScore(self,src , target):
        sm= SequenceMatcher(None, src, target)
        return sm.ratio()
    #如果两个字符串长度相等 计算levenshtein_distance 如果>0
    def jellyfishSimScore(self,src, target):
        # jellyfish.hamming_distance()
        score=0
        if(len(src) == len(target)):
            # print("caculate jaro winkler score.")

            # score= jellyfish.levenshtein_distance(src, target )
            # jellyfish.
            # todo
            score= jellyfish.jaro_winkler(src, target)

        return score


    def wuageSimScore(self,src , target):
        score1 = self.buildinSimScore(src, target)
        return round(score1 , 2)
        # score2 = jellyfishSimScore(src, target )
        # return round((score1 + score2)/2 ,2)


if __name__ == '__main__':
    # badcases
    src = u'不锈钢'
    target='不锈钢3e8'
    target2='3e8不锈钢'
    s = SimilarityTools()

    score = s.jellyfishSimScore(target , target2)
    print("jellyfish score=>{0}".format(score))

    # score=buildinSimScore(src , target2)
    # print("difflib score=>{0}".format(score))
    # score=jellyfishSimScore(src, target2)
    # print("jellyfish score=>{0}".format(score))

    score = s.wuageSimScore(target, target2)
    print("wuage score=>{0}".format(score))
