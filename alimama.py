# coding:utf-8
import json
import time

import requests
from selenium import webdriver
from datetime import datetime, timedelta
import json


class Spider(object):
    def __init__(self):
        self.web = webdriver.Chrome()
        self.__username = 'balabala'
        self.__password = 'balabala'
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            #'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36'
            #user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
            'user-agent': 'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
            
        }
        self.req = requests.Session()
        self.cookies = {}
    # 登录

    def login(self):
        self.web.get(
            'https://login.taobao.com/member/login.jhtml?style=mini&newMini2=true&css_style=alimama&from=alimama&redirectURL=http%3A%2F%2Fwww.alimama.com&full_redirect=true&disableQuickLogin=true')
        self.web.find_element_by_class_name('login-switch').click()
        time.sleep(10)
        # self.web.find_element_by_id('TPL_username_1').send_keys(self.__username)
        # self.web.find_element_by_id('TPL_password_1').send_keys(self.__password)
        # time.sleep(2)
        # self.web.find_element_by_id('J_SubmitStatic').click()
        # 等待5秒
        self.web.get('http://pub.alimama.com/myunion.htm')
        cookie = ''
        for elem in self.web.get_cookies():
            cookie += elem["name"] + "=" + elem["value"] + ";"
            if elem["name"] == '_tb_token_':
                self.token = elem["value"]
        self.cookies = cookie
        self.headers['Cookie'] = self.cookies
        # self.web.quit()

        
    def refresh(self, url):
        self.web.get(url)
        time.sleep(5)
        # self.web.find_element_by_id('TPL_username_1').send_keys(self.__username)
        # self.web.find_element_by_id('TPL_password_1').send_keys(self.__password)
        # time.sleep(2)
        # self.web.find_element_by_id('J_SubmitStatic').click()
        # 等待5秒
        cookie = ''
        for elem in self.web.get_cookies():
            cookie += elem["name"] + "=" + elem["value"] + ";"
            if elem["name"] == '_tb_token_':
                self.token = elem["value"]
        self.cookies = cookie
        self.headers['Cookie'] = self.cookies

        content= self.web.page_source
        dir(self.web)
        # self.web.quit()
        return content

    # 获取淘宝客订单列表
    def get_taoke_order_list(self):
        t = int(time.time() * 1000)
        now = datetime.now()
        start_date = (now + timedelta(days=-30)) .strftime("%Y-%m-%d")
        end_date = now.strftime("%Y-%m-%d")

        url = f'http://pub.alimama.com/report/getTbkPaymentDetails.json?startTime={start_date}&endTime={end_date}&payStatus=&queryType=1&toPage=1&perPageSize=50&total=&t={t}&pvid=&_tb_token_={self.token}&_input_charset=utf-8'
        web_data = self.req.get(url, headers=self.headers)

        data = json.loads(web_data.text)
        print(data['data']['paymentList'])

    # 创建推广位
    def add_ad(self):
        name = input()
        res = self.req.post('http://pub.alimama.com/common/adzone/selfAdzoneCreate.json', data={
            'tag': '29',
            'gcid': '8',
            'siteid': 'xxxxxxxx',  # 这里改成导购位ID
            'selectact': 'add',
            'newadzonename': name,
            '_tb_token_': self.token
        }, headers=self.headers)

        print(res.text)

    def get_list_keywords(self, channel, page_size=50):
        t = int(time.time() * 1000)
        url = f'https://pub.alimama.com/items/channel/{channel}.json?channel={channel}&perPageSize={page_size}&shopTag=&t={t}&_tb_token_={self.token}&pvid='
        res = self.req.get(url, headers=self.headers)
        rj = res.json()
        print (rj)
        if len(rj['data']['pageList']) > 0:
            return rj['data']['pageList']
        else:
            return 'no match item'

    # 获取淘宝客链接
    def get_tk_link(self, auctionid):
        t = int(time.time() * 1000)
        pvid = ''
        gcid, siteid, adzoneid = self.__get_tk_link_s1(auctionid, pvid)
        self.__get_tk_link_s2(gcid, siteid, adzoneid, auctionid, pvid)
        res = self.__get_tk_link_s3(auctionid, adzoneid, siteid, pvid)
        return res

    # 第一步，获取推广位相关信息
    def __get_tk_link_s1(self, auctionid, pvid):

        t = int(time.time() * 1000)
        url = f'http://pub.alimama.com/common/adzone/newSelfAdzone2.json?tag=29&itemId={auctionid}&blockId=&t={t}&_tb_token_={self.token}&pvid={pvid}'
        print (self.headers)
        res = self.req.get(url, headers=self.headers)
        # self.logger.debug(res.text)
        if "iframe" in  res.text:
            content = self.refresh(url)
            rj = json.loads(content)
        else:
            rj = res.json()
        gcid = rj['data']['otherList'][0]['gcid']
        siteid = rj['data']['otherList'][0]['siteid']
        adzoneid = rj['data']['otherAdzones'][0]['sub'][0]['id']
        return gcid, siteid, adzoneid

    # post数据
    def __get_tk_link_s2(self, gcid, siteid, adzoneid, auctionid, pvid):
        url = 'http://pub.alimama.com/common/adzone/selfAdzoneCreate.json'
        data = {
            'tag': '29',
            'gcid': gcid,
            'siteid': siteid,
            'selectact': 'sel',
            'adzoneid': adzoneid,
            't': int(time.time() * 1000),
            '_tb_token_': self.token,
            'pvid': pvid,
        }
        headers = self.headers
        headers = headers.update({
            'Content-Length': str(len(json.dumps(data))),
            'Origin': 'http://pub.alimama.com',
            'Referer': 'http://pub.alimama.com/promo/search/index.htm',
        })
        res = self.req.post(url, headers=headers, data=data)
        return res

    # 获取口令
    def __get_tk_link_s3(self, auctionid, adzoneid, siteid, pvid):

        t = int(time.time() * 1000)
        url = f'http://pub.alimama.com/common/code/getAuctionCode.json?auctionid={auctionid}&adzoneid={adzoneid}&siteid={siteid}&scenes=1&t={t}&_tb_token_={self.token}&pvid='
        print(f"__get_tk_link_s3  GET  {url}")
        headers = self.headers
        headers = headers.update({
            'Origin': 'http://pub.alimama.com',
            'Referer': 'http://pub.alimama.com/promo/search/index.htm',
        })
        res = self.req.get(url, headers=headers)
        if "iframe" in  res.text:
            content = self.refresh(url)
            print(content[121:-20])
            rj = json.loads(content[121:-20])
        else:
            rj = res.json()
        return rj['data']

    # 获取推广位列表
    def get_ad_list(self):
        res = self.req.get(
            'http://pub.alimama.com/common/adzone/adzoneManage.json?tab=3&toPage=1&perPageSize=40&gcid=8',
            headers=self.headers)
        print(res.text)


if __name__ == '__main__':
    sp = Spider()
    sp.login()
    product_lists = sp.get_list_keywords('muying', page_size=3)
    print(product_lists)
    for product in product_lists[:5]:
        print(product['auctionId'])
        print(sp.get_tk_link(product['auctionId']))

    # sp.add_ad()
    # sp.get_ad_list()
    # for i in range(1000):
    #     sp.get_taoke_order_list()
    #     time.sleep(30)
