"""
用snownlp进行情感分析
"""
import imageio
import sys
from snownlp import SnowNLP
import codecs
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

# 解决中文乱码问题
#sans-serif就是无衬线字体，是一种通用字体族。
#常见的无衬线字体有 Trebuchet MS, Tahoma, Verdana, Arial, Helvetica, 中文的幼圆、隶书等等。
mpl.rcParams['font.sans-serif']=['SimHei'] #指定默认字体 SimHei为黑体
mpl.rcParams['axes.unicode_minus']=False #用来正常显示负号

source = open("少年的你_comment_utf8 .csv","r",encoding="utf8")
line = source.readlines()
sentimentslist = []
for i in line:
    s = SnowNLP(i)
    print(s.sentiments)
    sentimentslist.append(s.sentiments)

plt.hist(sentimentslist, bins = np.arange(0, 1, 0.01), facecolor = 'g')
plt.xlabel('情感分数')
plt.ylabel('评论数')
plt.title('情感分析--《少年的你》豆瓣短评')
plt.savefig('./情感分数_《少年的你》豆瓣短评.jpg')
plt.show()

