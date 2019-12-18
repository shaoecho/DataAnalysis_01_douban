"""
对爬取的500条短评信息进行分析,用WordCloud和jieba,制作词云并统计词频
"""

import re
from wordcloud import WordCloud
import imageio
import jieba   #中文分词库jieba
import sys
import os
import matplotlib.pyplot as plt
from collections import Counter  # 计数器用于词频统计
import pandas as pd
import pymysql
from sqlalchemy import create_engine    #to_sql目前只支持两类mysql引擎一个是sqlalchemy和sqlliet3
from sqlalchemy.types import NVARCHAR, Float, Integer



#目标01: 根据文本,用WordCloud和jieba制作词云

f = open('少年的你_短评_utf8.csv',encoding='utf-8')   # 从外部.txt文件中读取大段文本，存入变量csv中.
csv_01 = f.read()
word_list = jieba.cut(csv_01,cut_all = False)  # 结巴分词 cut_all=True 设置为精准模式
wl_space_split = " ".join(word_list)   #使用空格连接 进行中文分词
print(wl_space_split)

# 导入imageio库中的imread函数，并用这个函数读取本地图片，作为词云形状图片
mk = imageio.imread("易烊千玺.png")  #报错,所以换了一种图片导入方式  UserWarning: mask image should be unsigned byte between 0 and 255

#构建词云对象w，设置词云图片宽、高、字体、UserWarning: mask image should be unsigned byte between 0 and 255. Got a float array背景颜色等参数

# 不用背景图,构建词云
my_wordcloud_01 = WordCloud(
    width=1000,                   #默认400像素
    height=700,                   #默认200像素
    background_color='black',    #默认背景颜色为黑色
    font_path='msyh.ttc',        #指定字体路径 默认None，对于中文可用font_path='msyh.ttc'
    font_step=1,                  #字号增大的步进间隔 默认1号
    min_font_size=4,              #最小字号 默认4号
    max_font_size=None,           #最大字号 根据高度自动调节
    max_words=200,                 #最大词数 默认200
    stopwords={},                  #不显示的单词 stop_words={"python","java"}
    scale=15,                      #值越大，图像密度越大越清晰
    prefer_horizontal=0.9,         #默认值0.90，浮点数类型。表示在水平如果不合适，就旋转为垂直方向，水平放置的词数占0.9？
    relative_scaling=0.5,          #默认值0.5，浮点型。设定按词频倒序排列，上一个词相对下一位词的大小倍数。有如下取值：“0”表示大小标准只参考频率排名，“1”如果词频是2倍，大小也是2倍
    # mask=mk,                     #不用背景图
    contour_width=1,               #设置轮廓宽度
    contour_color='steelblue'     #设置轮廓颜色
    )

# 自定义背景图,构建词云
my_wordcloud_02 = WordCloud(
    width=1000,                   #默认400像素
    height=700,                   #默认200像素
    background_color='black',    #默认背景颜色为黑色
    font_path='msyh.ttc',        #指定字体路径 默认None，对于中文可用font_path='msyh.ttc'
    font_step=1,                  #字号增大的步进间隔 默认1号
    min_font_size=4,              #最小字号 默认4号
    max_font_size=None,           #最大字号 根据高度自动调节
    max_words=200,                 #最大词数 默认200
    stopwords={},                  #不显示的单词 stop_words={"python","java"}
    scale=15,                      #值越大，图像密度越大越清晰
    prefer_horizontal=0.9,         #默认值0.90，浮点数类型。表示在水平如果不合适，就旋转为垂直方向，水平放置的词数占0.9？
    relative_scaling=0.5,          #默认值0.5，浮点型。设定按词频倒序排列，上一个词相对下一位词的大小倍数。有如下取值：“0”表示大小标准只参考频率排名，“1”如果词频是2倍，大小也是2倍
    mask=mk,                       #指定词云形状图片，默认为矩形
    contour_width=1,               #设置轮廓宽度
    contour_color='steelblue'     #设置轮廓颜色
    )

# 生成图片方法01: 直接生成图片,并保存到文件夹
# 将csv变量传入w的generate()方法，给词云输入文字
my_wordcloud_01.generate(csv_01)
my_wordcloud_02.generate(csv_01)
# 将词云图片导出到当前文件夹
my_wordcloud_01.to_file('词云_少年的你01.png')
my_wordcloud_02.to_file('词云_少年的你02.png')


"""
#生成图片方法02: 用matplotlib生成图片
# 对分词后的文本生成词云
my_wordcloud = WordCloud().generate(wl_space_split)
# 显示词云图
plt.imshow(my_wordcloud)
# 是否显示x轴、y轴下标
plt.axis("off")
plt.show()
"""


""" 目标02: 统计词频"""

#去停用词
def stopwordslist(filepath):
    stopwords = [line.strip() for line in open(filepath, 'r',encoding='utf-8').readlines()]   #strip()方法用于移除字符串头尾指定的字符(默认为空格或换行符
    return stopwords

#分词
def cut_word(datapath):
    with open(datapath, 'r',encoding='utf-8') as fr:
        string=fr.read()
        print("读取的字符串数据类型: ", type(string))

        #删除文件中的非法字符, re.sub(A,B,str1)将字符串str1中的A替换为B.
        data=re.sub(r"[\s+\.\!\/_,$%^*(【】：\]\[\-:;+\"\']+|[+——！，。？、~@#￥%……&*（）]+|[0-9]+","",string)
        word_list= jieba.cut(data)
        print("分词结果__未去停用词: ", word_list)

        stopwords = stopwordslist('stop_words.txt')    # 这里加载停用词的路径
        word_list_cut_stopwords = []
        for word in word_list:
            if word not in stopwords:
                if word != '\t':
                    word_list_cut_stopwords.append(word)
        print("分词结果__已去停用词: ", word_list_cut_stopwords)
        return word_list_cut_stopwords

#词频统计并保存
def statistic_top_word(word_list,top):
    #Counter()统计每个单词出现的次数，再分别将结果转化为键值对（即字典）,即{某分词: 出现的次数}这种形式.
    result= dict(Counter(word_list))
    print(result)
    #sorted(iterable, key=None, reverse=False) 其中iterable表示对可迭代对象,key表示用来进行比较的元素,reverse = True 降序 ， reverse = False 升序（默认）
    #items()方法把字典中每对 key 和 value 组成一个元组，并把这些元组放在列表中返回,result.items()返回[(关键词1,出现次数),(关键词2,出现次数),(关键词3,出现次数),]。
    #lambda表达式lambda item:item[1]的意思则是选取元组中的第二个元素作为比较参数.
    #总结,下句代码会返回一个列表,此列表由(关键词,出现次数)形式的元组组成,并且这些元组会表示根据出现次数进行降序排序.
    sortlist=sorted(result.items(),key=lambda item:item[1],reverse=True)
    resultlist=[]
    for i in range(0,top):  # 取列表sortlist中排名前100的元组, 存入resultlist
        resultlist.append(sortlist[i])
    print("统计词频: ", resultlist)
    return resultlist   #return之后的命令不会再执行

# 保存
def df_save(list):
    result_dict = dict(list)  # 因为list是列表,列表没有items()方法
    data = [(k, v) for k, v in result_dict.items()]  # items()方法可以把result_dic中的元素依次取出来.
    df = pd.DataFrame(data,
                      columns=['分词', '次数']) #此处的列名一定要和mysql中列名一致,否则报错.
    print("df为:", df)

    # 将df中数据保存入csv
    df.to_csv('resultlist.csv')

    # 将df中数据保存入mysql数据库
    engine = create_engine("mysql+pymysql://root:123456@localhost:3306/douban?charset=utf8")
    df.to_sql(name='word_list_cut_stopwords_shaoniandeni',
              con=engine,
              if_exists='append',
              index=False,  # 是否将df的index单独写到一列中
              )


#主函数
def main():
    #设置数据集地址,此处应该是路径(类似 F:\\data\\spam.txt),但我们放在同一个文件夹下,所以直用文件名称.
    datapath='少年的你_短评_utf8.csv'
    #对文本进行分词
    word_list_cut_stopwords=cut_word(datapath)
    #统计文本中的词频
    statistic_result=statistic_top_word(word_list_cut_stopwords,100)
    #输出统计结果
    print("出现频率前100的分词为: ",statistic_result)
    #保存
    df_save(statistic_result)

if __name__ == "__main__":
    main()





