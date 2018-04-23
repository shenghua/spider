#!/usr/bin/python
# coding:utf-8

import time
import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver  
from prettytable import PrettyTable    
import os
import sqlite3
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

class KouBei():
    def __init__(self):
        self.session=requests.session()
        self.headers = {
            'Host': 'fuwu.koubei.com',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive'}
        self.session.get('http://fuwu.koubei.com',headers=self.headers)
        # cookieJar = {'JSESSIONID':'044AA59ED1CC0018389BEB990A721584', 'rtk':'NtIxKehSxBJ1uyLk9tCZuLbTsuAvcYpEllImlgq6EtpCGzcD01A}
        # resp = self.session.request("GET", 'http://fuwu.koubei.com/commodity/v2/merchandise/search.json?pageSize=20&categoryId=102495&labelId=&needCharge=&pageNum=1&_input_charset=utf-8',headers=self.headers,cookies=cookieJar)
        # print('resp:'+resp.text)
        self.count=0

    def work(self):
        self.get_urls('http://fuwu.koubei.com',0)
        # self.get_url_dynamic('http://fuwu.koubei.com/commodity/v2/merchandise/search.json')

    def get_urls(self,url,types):
        dbs=['koubei1.db']
        db=dbs[types]
        if os.path.isfile(db):
            conn = sqlite3.connect(db)
            cursor=conn.cursor()
        else:
            conn=sqlite3.connect(db)
            cursor=conn.cursor()
            cursor.execute("create table commodity(commodity_id varchar(40) primary key, app_name varchar(30), app_company varchar(30), app_comment_number varchar(10), app_cost varchar(20))")
        
        commodities=self.get_url(url)
        print(commodities)
        for commodity in commodities:
            try:
                cursor.execute("insert into commodity(commodity_id, app_name, app_company, app_comment_number, app_cost) values (?, ?, ?, ?, ?)",(commodity['commodity_id'], commodity['app_name'], commodity['app_company'], commodity['app_comment_number'], commodity['app_cost']))
            except:
                continue
        cursor.close()
        conn.commit()
        conn.close()
        print(db+'    OK')

    def get_url_dynamic(self,url):
        data ={'categoryId':'',  
               'channelCode':'KOUBEI',  
               'firstOrderByField':'Rating',  
               'pageNum':1, 
               'pageSize':5000,  
               'secondOrderByField':'MerchantSalesCount',
               'statusList':'',
               'sort':'-',
               'supportTest':'false'
              }  
        school_datas  = requests.get(url,data = data)
        print(school_datas.text)

    def get_url(self,url):
        num=0
        commodities=[]

        browser = webdriver.Chrome()
        browser.get(url)
        # print(BeautifulSoup(browser.page_source))

        time.sleep(2)
        # try:
        #     html=self.session.get(url).text
        # except:
        #     print('geturl except')
        #     return commodities
        try:
            items=BeautifulSoup(browser.page_source).find('div',attrs={'class':'detail-content-right-content'}).find_all('div',attrs={'class':'new-item'})
        except:
            print('find item except')
            return commodities

        i=0
        for item in items:
            i+=1
            print(i)
            href=item.find('a').get('href')
            hreflen=len(href)
            start=href.find('=',0,hreflen)+1
            commodity_id=href[start:hreflen]
            app_name=item.find('div',attrs={'class':'app-name'}).get_text()
            app_company=item.find('div',attrs={'class':'app-company'}).get_text()
            app_comment_number=item.find('span',attrs={'class':'app-commentNum'}).get_text()
            app_cost=item.find('div',attrs={'class':'app-cost'}).get_text()
            commodity={'commodity_id':commodity_id, 'app_name':app_name, 'app_company':app_company, 'app_comment_number':app_comment_number, 'app_cost':app_cost}
            commodities.append(commodity)

        return commodities

    def run(self):
        for i in range(9):
            self.get_text(i)

    def get_text(self,num):
        dbs=['juqing_urls.db','donghua_urls.db','fanzui_urls.db','jingsong_urls.db','xuanyi_urls.db','cult_urls.db']
        conn = sqlite3.connect(dbs[num])
        cursor = conn.execute("SELECT url from urls")
        file_text=open(dbs[num].replace('_urls.db','.txt'),'w',encoding='utf-8')
        for row in cursor:
            time.sleep(2)
            try:
                text=self.spider(row[0])
            except:
                continue
            file_text.write(text+'\n\n')
            print(self.count)
            self.count+=1
        cursor.close()
        conn.commit()
        conn.close()
        file_text.close()

    def spider(self, url):
        html = requests.get(url, headers=self.headers).text
        soup = BeautifulSoup(html)
        name=soup.find('span',attrs={'property':'v:itemreviewed'}).get_text()
        picture=soup.find('img',attrs={'rel':'v:image'}).get('src')
        picture='[img]'+picture+'[/img]'
        text=name+'\n'
        text+=picture+'\n'
        info=soup.find('div',attrs={'class':'indent clearfix'}).find('div',attrs={'id':'info'}).get_text()
        text+=info
        intro=soup.find('div',attrs={'class':'related-info'}).get_text()
        text+=intro
        return text

def test():
    work = KouBei()
    #work.get_url('http://www.douban.com/tag/%E7%8A%AF%E7%BD%AA/movie')
    print(work.spider('http://fuwu.koubei.com'))

if __name__ == '__main__':
    work = KouBei()
    work.work()
    #work.run()
