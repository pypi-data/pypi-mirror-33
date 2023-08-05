# -*- coding: utf-8 -*-
"""
similarity_calculate 主要完成了：
1.加载word2vec模型
2.WMD计算短语相似度
3.相似度-->模板匹配度
"""
__title__ = 'QGDT-cpu'
__author__ = 'Ex_treme'
__license__ = 'MIT'
__copyright__ = 'Copyright 2018, Ex_treme'

import re

from gensim.models import Word2Vec
from jieba import cut

from QGDT.templates_x import templates_x1, templates_x2, templates_x3
from QGDT.tools import get_current_path, chinese, log


# 匹配模板
def templates(x1='', x2='', x3=''):
    """接受得到的搜索词，匹配相应搜索词个数的模板

    Keyword arguments:
    x1                  -- x1，搜索词1
    x2                  -- x2，搜索词2
    x3                  -- x3,搜索词3
    Return:
        (搜索序列，模板号)
    """
    if x1 and x2 and x3:
        s1 = x1 + ' ' + x2 + ' ' + x3
        return s1, 3
    elif x1 and x2:
        s1 = x1 + ' ' + x2
        return s1, 2
    elif x1:
        s1 = x1
        return s1, 1
    else:
        raise Exception('未正确输入查询词')


class Search2Similar(object):
    """搜索词-->生成相似度"""

    def __init__(self, search_list, w2v_path):
        """
        Keyword arguments:
        w2v                 -- 词嵌入，word2vec
        templates           -- 搜索序列和模板号
        """
        self.x1, self.x2, self.x3 = '', '', ''
        self.w2v = Word2Vec.load(get_current_path(w2v_path))
        for index, i in enumerate(search_list):
            if index == 0:
                self.x1 = i
            elif index == 1:
                self.x2 = i
            elif index == 2:
                self.x3 = i
        self.templates = templates(x1=self.x1, x2=self.x2, x3=self.x3)

    def search2keywords(self, s):
        """ 查询词转换成关键词

        Return:
        k      --关键词序列，list格式
        """

        k = []
        for i in cut(s):
            if i.__len__() >= 2 and re.search(chinese, i):
                k.append(i)
        return k

    def wmd(self, s1, s2):
        """ 计算两个搜索词之间的WMD距离
        注意：当词嵌入中不存在计算词时，返回'inf',意为距离无穷大。
        Return:
        wmd      --wmd距离（wmd越小，表示搜索词越相似），float格式
        """
        try:
            if s1.__len__() >= 1 and s2.__len__() >= 1:
                return self.w2v.wmdistance(self.search2keywords(s1), self.search2keywords(s2))
            else:
                return float('inf')
        except:
            return float('inf')

    def mul_wmd(self, s1, s2):
        """ 计算多个查询词的平均WMD距离

        Return:
        avg_wmd      --平均wmd距离（wmd越小，表示搜索词越相似），float格式
        """
        if s1.split().__len__() is not s2.split().__len__():
            raise Exception('输入的查询词个数不一致，无法计算WMD。')
        else:
            s1 = s1.split()
            s2 = s2.split()
            count = len(s1 or s2)

        mul_wmd = []
        for i in range(count):
            mul_wmd.append(self.wmd(s1[i], s2[i]))
        return sum(mul_wmd) / mul_wmd.__len__()

    def similarity_calculate(self):
        """ 搜索序列与模板之间的相似度计算

        Return:
        templates_id        --对应搜索词个数的模板，int格式
        min_wmd             --最小wmd距离（wmd越小，表示搜索词越相似），float格式
        template_id         --最后使用模板id，int格式
        """
        wmd_list = []
        avg_wmd_list = []
        s1 = self.templates[0]
        templates_id = self.templates[1]
        if templates_id == 1:
            for s2 in templates_x1.x1_1:
                wmd_list.append(self.wmd(s1, s2))
            avg_wmd_list.append(sum(wmd_list) / wmd_list.__len__())
            wmd_list = []
            for s2 in templates_x1.x1_2:
                wmd_list.append(self.wmd(s1, s2))
            avg_wmd_list.append(sum(wmd_list) / wmd_list.__len__())
            wmd_list = []
            for s2 in templates_x1.x1_3:
                wmd_list.append(self.wmd(s1, s2))
            avg_wmd_list.append(sum(wmd_list) / wmd_list.__len__())
            wmd_list = []
            for s2 in templates_x1.x1_4:
                wmd_list.append(self.wmd(s1, s2))
            avg_wmd_list.append(sum(wmd_list) / wmd_list.__len__())
        elif templates_id == 2:
            for s2 in templates_x2.x1_x2_1:
                wmd_list.append(self.wmd(s1, s2))
            avg_wmd_list.append(sum(wmd_list) / wmd_list.__len__())
            wmd_list = []
            for s2 in templates_x2.x1_x2_2:
                wmd_list.append(self.wmd(s1, s2))
            avg_wmd_list.append(sum(wmd_list) / wmd_list.__len__())
            wmd_list = []
            for s2 in templates_x2.x1_x2_3:
                wmd_list.append(self.wmd(s1, s2))
            avg_wmd_list.append(sum(wmd_list) / wmd_list.__len__())
            wmd_list = []
            for s2 in templates_x2.x1_x2_4:
                wmd_list.append(self.wmd(s1, s2))
            avg_wmd_list.append(sum(wmd_list) / wmd_list.__len__())
        elif templates_id == 3:
            for s2 in templates_x3.x1_x2_x3_1:
                wmd_list.append(self.wmd(s1, s2))
            avg_wmd_list.append(sum(wmd_list) / wmd_list.__len__())
            wmd_list = []
            for s2 in templates_x3.x1_x2_x3_2:
                wmd_list.append(self.wmd(s1, s2))
            avg_wmd_list.append(sum(wmd_list) / wmd_list.__len__())
            wmd_list = []
            for s2 in templates_x3.x1_x2_x3_3:
                wmd_list.append(self.wmd(s1, s2))
            avg_wmd_list.append(sum(wmd_list) / wmd_list.__len__())
            wmd_list = []
            for s2 in templates_x3.x1_x2_x3_4:
                wmd_list.append(self.wmd(s1, s2))
            avg_wmd_list.append(sum(wmd_list) / wmd_list.__len__())

        log('warning', '相似度计算：{}-->{}'.format(s1, avg_wmd_list))

        return avg_wmd_list


if __name__ == "__main__":
    pass
