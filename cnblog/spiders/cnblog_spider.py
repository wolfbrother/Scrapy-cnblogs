#!/usr/bin/env python
# -*- coding:utf-8 -*-

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.http import Request, FormRequest
from scrapy import Request


from cnblog.items import cnblogItem

#本爬虫执行方式
# scrapy crawl cnblog -o filename.json


class cnblogSipder(CrawlSpider) :
    name = "cnblog"
    allowed_domains = ["home.cnblogs.com"]
    start_urls = [
        #"http://www.cnblogs.com/"
    ]
    #rules = (
    #	#当前网页中符合allow要求的字段会加到allowed_domains后面组成一个网址，之后将对该网址进行分析
    #    Rule(SgmlLinkExtractor(allow = ('/u/[A-Za-z0-9_]+/$', )), callback = 'parse_page', follow = True),
    #)

    #经验证，在调用Request时如果不加入cookies参数，则不能以已登录用户身份登录页面，也就爬取不到只有已登录用户才能看到的数据
    mycookies = {'__gads':r'ID=5f799eb5ff8a0d1c:T=1426060996:S=ALNI_MY3SIyB9wH3MOArdyDiV2aA15B-5w', '__utma':r'215813774.327332698.1426074473.1426115828.1426219221.2',
'__utmz':r'215813774.1426219221.2.2.utmcsr=cnblogs.com|utmccn=(referral)|utmcmd=referral|utmcct=/', 'lzstat_uv':r'1871254131842491216|2656025',
'_gat':r'1', '.DottextCookie':r'74F22D7360135E7A2E5106E1D9865263D88804329BC310EB4B651B994B30D829B57728798B5C08B764A9F12572BAC4EA8B7AA327E002625185F1253348F3D57CCEA7FDC9CBB85540D110269D1D7F483FDA0572F42392D718704C3DC778189ABF39FFF55556DD4656B0C488F14DC8ABE3B0DDAF267D713E6BDA9E5EB4C1C11F7435E0042260840ADA188B9C71',
'_ga':r'GA1.2.327332698.1426074473',
'SERVERID':r'73ea7682c79ff5c414f1e6047449c5c1|1428238177|1428238176',
'.CNBlogsCookie':r'BD00A1ECB74E3962ED17C2AF34C88D4B13775570C960698381304030A3DC48AE945CF667989B80BEC51DCC085427991DA936ED0B05BD336EB194BE7EA6775F37506E901B7CAFCD19B6D0BC02132774C8F3D22379FF77530648810AE4CEC4882A90C15881F68908222E2579802DFAE43DFEC194A9'
}

    #重写了爬虫类的方法, 实现了自定义请求, 运行成功后会调用callback回调函数
    def start_requests(self):
        yield Request("http://home.cnblogs.com/u/jinliangjiuzhuang/", cookies = self.mycookies,callback=self.parse_home_page)
	
    def parse_home_page(self,response):
        #主页界面示例：http://home.cnblogs.com/u/LeftNotEasy/followees/
        hostname = response.url.split('/')[-2]
        host_followers_page_url = 'http://home.cnblogs.com/u/' + hostname + '/followers/'
        host_followees_page_url = 'http://home.cnblogs.com/u/' + hostname + '/followees/'

        r_host_followers_page_url = Request(host_followers_page_url, cookies = self.mycookies,callback=self.parse_followers_page)
        item = cnblogItem()
        item['url'] = response.url
        item['name'] = hostname
        item['followers'] = []
        r_host_followers_page_url.meta['item'] = item

        r_host_followees_page_url = Request(host_followees_page_url, cookies = self.mycookies,callback=self.parse_followees_page)
        r = [r_host_followers_page_url,r_host_followees_page_url]

        for i in range(2):
            yield r[i] 		

    def parse_followees_page(self,response): #我的关注
        #关注界面示例：http://home.cnblogs.com/u/LeftNotEasy/followees/
        sel = Selector(response)
        find_avatar_list = sel.xpath(u'//div[@id="main"]/div[@class="avatar_list"]/ul/li/div[@class="avatar_name"]/a')
        names = [i.extract().split('/')[2] for i in find_avatar_list]
        home_page_urls = ['http://home.cnblogs.com/u/'+ name +'/' for name in names]

        for url in home_page_urls:
            yield Request(url, cookies = self.mycookies,callback = self.parse_home_page)

        #进入下一页
        next_href_list = sel.xpath(u'//div[@class="pager"]/a').extract()
        href_list = [href for href in next_href_list if href.find('Next &gt')>0]
        if len(href_list) > 0:
            next_href = u'http://home.cnblogs.com' + href_list[0].split('"')[1] #下一页的网址
            print 'The next followees page of the current host: \n     ',next_href
            yield Request(next_href, cookies = self.mycookies,callback = self.parse_followees_page)

    def parse_followers_page(self,response): #我的粉丝
        #粉丝界面网址示例：http://home.cnblogs.com/u/LeftNotEasy/followers/
        sel = Selector(response)
        item = response.meta['item']

        find_avatar_list = sel.xpath(u'//div[@id="main"]/div[@class="avatar_list"]/ul/li/div[@class="avatar_name"]/a')
        names = [i.extract().split('/')[2] for i in find_avatar_list]

        item['followers'].extend(names)



        home_page_urls = ['http://home.cnblogs.com/u/'+ name +'/' for name in names]

        for url in home_page_urls:
            yield Request(url, cookies = self.mycookies,callback = self.parse_home_page)

        next_href_list = sel.xpath(u'//div[@class="pager"]/a').extract()
        href_list = [href for href in next_href_list if href.find('Next &gt')>0]
        if len(href_list) <= 0: #如果粉丝页面读取完毕，则返回item
            yield item

        else:#如果仍有粉丝页面未读，则携带当前item内容进入下一粉丝界面
            next_href = u'http://home.cnblogs.com' + href_list[0].split('"')[1] #下一页的网址
            print 'The next followees page of the current host: \n     ',next_href
            r = Request(next_href, cookies = self.mycookies,callback = self.parse_followers_page)
            r.meta['item'] = item
            yield r
            