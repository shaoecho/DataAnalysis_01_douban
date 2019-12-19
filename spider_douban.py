#!/usr/bin/env python
# coding=utf-8
'''
用的request+ xpath来爬取豆瓣点评短评
数据储存为csv
用fake_useragent库中的UserAgent来伪造UserAgent.
用阿布云的收费的http代理
'''

import time
import re
import random
import requests
from lxml import etree
import pandas as pd
from fake_useragent import UserAgent
import json

username_list, score_list, date_list, like_list, content_list = [], [], [], [], []
ua = UserAgent()

# 此处的requests.Session对象只是一个用于保存Cookie的对象,和session不同,session是保存在服务端的.
s = requests.Session()  #用于生成Session对象，用于保存Cookie

# 模拟登录.
# 方法是需要在后台获取登录的 URL并填写请求体参数，然后 POST 请求登录
def login_douban():
    # 登录URL
    login_url = 'https://accounts.douban.com/j/mobile/login/basic'
    # 请求头
    ua = UserAgent()   #用fake_useragent库中的UserAgent来伪造UserAgent.
    headers = {'user-agent': ua.random}
    # 传递用户名和密码
    data = {'User-agent': ua.random,
            'Connection ':'keep-alive',
            'Content-Encoding': 'br',
            'Keep-Alive': 'timeout=30',
            'name': '15191811233',
            'password': '123456',
            'remember': 'false'}
    try:
        r = s.post(login_url, headers=headers, data=data)
        r.raise_for_status()
    except:
        print('登录请求失败')
        return 0
    # 打印请求结果
    print("(模拟登录函数)====r.text: ",r.text)
    return 1   #是因为想用后面用if login_douban():来判断是否登录,#此处返回1,为真.

# 代理ip,
def get_proxies():
    # 代理服务器(购买的阿布云)
    proxyHost = "http-pro.abuyun.com"
    proxyPort = "9010"

    # 代理隧道验证信息
    proxyUser = "H477376K5G8P470P"     # 替换为你自己买的
    proxyPass = "0F146FC04BF2DA42"     # 替换为你自己买的

    proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
        "host": proxyHost,
        "port": proxyPort,
        "user": proxyUser,
        "pass": proxyPass,
    }

    proxies = {
        #"http": proxyMeta,
        "https": proxyMeta,   #要爬取类型是https的urls,只需要类型是https的代理
    }

    print("(阿布云代理IP)====proxies: ", proxies)
    return proxies

#  将url,headers,proxies传入requests.get(),获取当页的respone.
def get_resp(movieId, currentPage):
    # 1) 拼接url
    c = ('https://movie.douban.com/subject/',str(movieId), '/comments?start=' , str(20*(currentPage-1)) , '&limit=20&sort=new_score&status=P')
    url = ''.join(c)    #'表示直接拼接,如果是'-'.join(c)则表示c的字符串之间用-相连接.
    print('(get_resp函数)====想要爬取的此页的url:',url)

    # 2) 用fake_useragent库中的UserAgent来伪造UserAgent.
    # cookie会过期, 每次都要重新添加.
    cookies = {
        'bid': 'WeP59nZJJjE; douban-fav-remind=1',
        'ap_v': '0,6.0',
        '_pk_ses.100001.4cf6': '*',
        '__utma': '223695111.1698435046.1569404628.1572852419.1572861816.21',
        '__utmb': '30149280.0.10.1572861816',
        '__utmc': '223695111',
        '__utmz': '223695111.1572184730.15.4.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/passport/login',
        'dbcl2': '197175079:7OsRZk4vqh8',
        'ck': 'WaD5',
        '_pk_id.100001.4cf6': '6ac57c41d6b5ec28.1569404628.22.1572862133.1572853829.',
        'push_doumail_num': '0',
        'push_noty_num': '0',
    }
    headers = { 'Connection':'keep-alive',
                'Content-Encoding': 'br',
                'Keep-Alive': 'timeout=30',
                'User-agent': ua.random
                }
    print('(get_resp函数)====User-agent:',ua.random)

    # 3) 将url,header,proxies传入requests.get()函数中,向网页发起请求,拿到response.
    while True:
        try:
            proxies = get_proxies()   #得到参数
            resp = requests.get(url, headers=headers, proxies= proxies,cookies=cookies )
            print("(get_resp函数)====resp.status_code:", resp.status_code)
            return resp
            break
        except requests.ConnectionError as e:
            print("(get_resp函数)====OOPS!! Connection Error. Make sure you are connected to Internet. Technical Details given below.")
            print(str(e))
            proxies = get_proxies()
            continue
        except requests.Timeout as e:
            print("(get_resp函数)====OOPS!! Timeout Error")
            print(str(e))
            proxies = get_proxies()
            continue
        except requests.RequestException as e:
            print("(get_resp函数)====OOPS!! General Error")
            print(str(e))
            proxies = get_proxies()
            continue
        except KeyboardInterrupt:
            print("(get_resp函数)====Someone closed the program")
    print("====================================================================================")

# 爬取某个歌曲(movieId)某一页(currentPage)的内容
def get_content(movieId, currentPage):  #此函数爬取某一页的20个短评

    # 运行get_resp()函数, 得到respone.
    resp = get_resp(movieId, currentPage)

    # 对拿到的resp进行解析,提取想要的数据,并存入5个列表中 username_list,  score_list,  content_list, date_list, like_list
    if (resp.status_code == 200):
        print('\n第{}页的数据爬取成功'.format(currentPage))
    else:
        print('\n o(╯□╰)o第{}页的数据爬取失败'.format(currentPage))
        print("状态码:",resp.status_code)

    resp.encoding = "utf-8"  # 对res进行编码才能看的懂
    #print("5.1)====res", resp.text)
    x = etree.HTML(resp.text)
    print("5.2)====x: ",x)

    # 电影名称只需要取一次就行了
    global MovieName
    if currentPage == 1:
        MovieName = x.xpath('//*[@id="content"]/h1/text()')

    for j in range(1, 21):  # 豆瓣一页只有20条评论

        try:
            print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            print('*******开始爬取本页的第{}条评论'.format(j))

            # 用户名
            # 下面的user_name返回的是一个列表,包含本页20个user_name, format(j)的作用有点类似于表达这个列表的索引.
            user_name = x.xpath('//div[@class="comment-item"]/div/a/@title'.format(j))
            #print('==========user_name:',user_name)
            username_list.append(str(user_name[j-1]).strip())   # strip()用于移除字符串头尾的空格
            #print('====username_list:',username_list)

            # 有多少个人点赞
            # 若没有人点赞的时候,有对应节点,数据值为0 ,一页能抓取20个点赞数据,不需要特殊处理
            like = x.xpath('//span[@class="comment-vote"]/span/text()'.format(j))  #.format(j)此处的作用是通过j进行循环
            like_list.append(str(like[j-1]))
            #print('====like_list:',like_list)

            # 评论内容
            # 当有文字评论内容时，<span class="short">真好听啊</span>
            # 当没有文字评论内容时，存在子节点，但内容为空。用ext()[.!= ""]表示不为空
            #  此处用了li[{}]..format(j),那么得到的就不是包含整页数据的列表,而是20个li块中的某一个进行提取,得到的是一个只包含一个值的列表, 所以此处用content(0)而不是content[j - 1])
            a = x.xpath('//div[@class="comment-item"][{}]/div[2]/p/span/text()[.!= ""]'.format(j))
            c = len(a)  #a要么是空列表,要么是只有一个值的列表. c=0时,表示无评论.c=1时,表示有评论.
            #print('==========a:', a)
            #print('==========c:', c)
            if c:
                content = x.xpath('//div[@class="comment-item"][{}]/div[2]/p/span/text()'.format(j))
                content_list.append(str(content[0]).strip())
                #print('========本条评论为:', a)
            else:
                content_list.append('无')     #当没有评论时,用代替.
                #print('========本条无评论:', a)
            #print('====content_list:', content_list)

            # 评分
            # 和没有文字评论还不一样，当没有打星时，连节点也没有。并且有没有评分，时间xpath路径是不一样的
            # 判断//span[@class="comment-info"][{}]下有几个span标签,b=3表示有打星, b=2表示没有打星.
            b = len(x.xpath('//div[@class="comment-item"][{}]/div[2]/h3/span[@class="comment-info"]/span'.format(j)))
            #print('========b:',b)
            if b == 3:  # 有打星
                date = x.xpath('//div[@class="comment-item"][{}]/div[2]/h3/span[@class="comment-info"]/span[3]/text()'.format(j))
                date_list.append(str(date[0]).strip())

                score = x.xpath('//div[@class="comment-item"][{}]/div[2]/h3/span[@class="comment-info"]/span[2]/@title'.format(j))

                # 把中文转化成评分来显示
                if score[0] == '力荐':
                    score = '5'               #表示5颗星的评价
                elif score[0] == '推荐':
                    score = '4'
                elif score[0] == '还行':
                    score = '3'
                elif score[0] == '较差':
                    score = '2'
                else:
                    score = '1'
                score_list.append(score)
                #print('========本条有打星')
            else:
                date = x.xpath('//div[@class="comment-item"][{}]/div[2]/h3/span[@class="comment-info"]/span[2]/text()'.format(j))
                print('date:',date)
                date_list.append(str(date[0]).strip().strip('/n'))
                score_list.append('0')
                #print('========本条没有打星')

            #print('====date_list:', date_list)
            #print('====score_list:', score_list)

        except IndexError:
            print('error here')
            pass

#主框架
def main(movieId, scrapyPage):
    global MovieName
    # 第二步: 依次爬取1到scrapyPage页的数据
    for i in range(1, scrapyPage + 1):

        # 第一步: 爬取某一页的数据,并存入5个列表中 username_list,  score_list,  content_list, date_list, like_list
        get_content(movieId, i)
        time.sleep(round(random.uniform(1, 5), 2))   # 随机等待时间，免得被封ip
        # random.uniform(1, 2)表示生成1到2之间的随机浮点数, round(x, num)表示对浮点数x的第n位小数进行四舍五入值。

    # 第三步: 将5个list中scrapyPage页的所有数据保存进DataFrame.
    infos = {'username': username_list, 'score': score_list,
             'content': content_list, 'date': date_list, 'like': like_list}

    data = pd.DataFrame({k:pd.Series(v[:20*scrapyPage]) for k,v in infos.items()},
                        columns=['username', 'score', 'content', 'date', 'like'])

    # 注意 20*爬取的页数表示不考虑缺数据的情况下爬取的数据列表的行数.!


    # 获取电影名称, 并设置为全球变量
    movieName = ''.join(MovieName)
    data.to_csv(movieName + ".csv")   # 存储名为  歌曲名.csv
    print('done!')

#初始程序
if __name__ == '__main__':
    # 登录成功才爬取
    if login_douban():        #登录成功时,会返回1
        main(30166972, 25)     # 评论电影的ID号+要爬取的评论页面数, 豆瓣登录情况下,最多只能登录25页.

