# -*- encoding=utf-8
'''
File: testcrawlapk.py
Author: Hunag Ronghua <huangronghua@ndoo.net>
Date: 2013-01-10 10:05
Description: apk爬虫 spiders测试
'''
import re
import urllib
import urllib2
import unittest2 as unittest
import apkcrawl.settings
from apkcrawl.spiders.searchs import *
from apkcrawl.tests import get_crawler, get_projectpath , get_crawler
import __future__ 
from scrapy.core.downloader.handlers.http import HttpDownloadHandler
from scrapy.http import Request
from scrapy.http.response.text import TextResponse as Response
from scrapy.settings import Settings
from apkcrawl.items    import ApkcrawlItem

#from apkcrawl.spiders.searchs.apk91 import Apk91Spider
#from apkcrawl.spiders.searchs.hiapk import HiapkSpider
#from apkcrawl.spiders.searchs.myapp import MyappSpider
#from apkcrawl.spiders.searchs.anzhi import AnzhiSpider

# 将搜索关键字生成器转换为列表，以满足可重置列表，重置测试上下文环境
from apkcrawl.spiders.searchs import apkbase
apkbase.SEARCH_KEYWORDS = list(apkbase.SEARCH_KEYWORDS)

def it_is_empty( it ):
    for _ in it:
        return False
    return True
from nose.plugins.skip import SkipTest

class SpiderTest(unittest.TestCase):

    __test__ = False

    test_type='feature'

    spider_class = Apk91Spider

    site             = ''
    entry_pattern    = ''
    search_pattern   = ''
    download_pattern = ''

    keyword = u'语音搜索';

    ##
    # @brief 模拟crawler、downloader 和 spidermanager的爬虫处理，返回response结果
    #
    # @param request
    # @param spider
    #
    # @return scrapy.http.Response
    def download_request(self , request, spider=None):
        headers = dict(request.headers.items())
        req = urllib2.Request( request.url,headers = headers )

        opener = urllib2.build_opener()
        res = urllib2.urlopen( req)
        headers = { k:v for k,v in res.headers.items() }

        response = Response( request.url , request=request ,
                status=res.code , headers=headers, body=res.read() )
        return response

    def spider_crawl_package(self , spider , request ):
        """spider_crawl_package 爬取本次请求的软件-包括版本数据"""
        response = self.download_request( request, 0)
        items = []
        pcnt = 0
        vcnt = 0
        for preq in spider.parse( response ):

            if isinstance( preq , ApkcrawlItem ):
                items.append( preq )
                continue

            pres = self.download_request( preq , 1)
            for vreq in spider.parse_entry( pres ):
                if isinstance( vreq , ApkcrawlItem ):
                    items.append(vreq)
                else:
                    vres = self.download_request( vreq , 2 )
                    item = spider.crawl_version( vres )
                    items.append( item )
        return items

    def assert_searchurl(self, pattern_str , url , keyword ):
        """assert_searchurl 搜索url断言，圈出关键字比对spider是否正确生成搜索url"""
        self.assertRegexpMatches( url , pattern_str )
        mth = re.match(  pattern_str , url )
        self.assertEquals(mth.group(1) , urllib.quote( keyword.encode('utf-8')) )

    def assert_parseItem(self, item ):
        """ 断言item数据结构"""
        referer_pattern = self.entry_pattern
        if item.get('is_entry'):
            referer_pattern = self.search_pattern

        self.assertRegexpMatches( item.get('referer_url'), referer_pattern )
        self.assertRegexpMatches( item.get('entry_url'), self.entry_pattern )

        self.assertRegexpMatches( item.get('download_url'), self.download_pattern )
        self.assertEquals( item.get('site') , self.site)

    def test_crawl_searchapk(self):
        __doc__ = self.cn + """test_crawl_searchapk 基本爬取功能检查，爬取站点是否正确，包括生成搜索url列表， """
        spider = self.spider_class( self.spider_class.DOMAIN )
        self.assertEqual(spider.name, self.site )
        empty = True
        for _ in spider.start_urls:
            empty = False
            break
        self.assertFalse( empty )
        return spider

    def test_userkeyword_search(self):
        __doc__ = self.cn + """.test_userkeyword_search 用户输入关键字搜索爬取操作"""

        keyword = self.keyword
        spider = self.spider_class( self.spider_class.DOMAIN , keyword= keyword )
        self.cur_spider = spider
        start_requests = spider.start_requests()

        requests = []
        pattern_str = self.search_pattern
        for _ in start_requests:
            self.assert_searchurl( pattern_str , _.url , keyword )
            requests.append( _ )

        self.assertEquals( 1 , len(requests), '搜索关键字请求地址只会产生一个地址')
        items = self.spider_crawl_package( spider , requests[0] )
        for i in items:
            self.assert_parseItem( i )

        return ( spider , items )

    cn = __module__ + '.' + __name__

class Apk91CrawlSpiderTest(SpiderTest):
    """Apk91CrawlSpiderTest 测试apk爬虫处理"""
    spider_class = Apk91Spider

    __test__ = True

    site = 'apk.91.com'
    entry_pattern    = 'http:\/\/apk\.91\.com\/Soft/Android/([a-zA-Z0-1_\.]+)-(.+)\.html'
    search_pattern   = 'http:\/\/apk\.91\.com\/soft\/Android\/search/1_5_0_0_(.+)'
    download_pattern = 'http:\/\/apk\.91\.com\/soft\/Controller.ashx\?Action=Download&id=(\d+)'

    #def test_userkeyword_search(self):
        #"""Apk91CrawlSpiderTest.test_userkeyword_search 用户输入关键字搜索爬取操作"""

        #spider , items = super( Apk91CrawlSpiderTest , self).test_userkeyword_search()
        ## 向上遍历5个版本，另最新版本共6个
        #self.assertLessEqual( len(items) , 6 )

class AnzhiCrawlSpiderTest(SpiderTest):
    """AnzhiCrawlSpiderTest 测试 安智网 apk爬虫"""
    spider_class = AnzhiSpider

    __test__ = True

    site = 'www.anzhi.com'
    entry_pattern    = 'http:\/\/www\.anzhi\.com\/soft_(\d+)\.html'
    search_pattern   = "http:\/\/www\.anzhi\.com\/search\.php\?keyword=([%0-9A-X]+)"
    download_pattern = 'http:\/\/www\.anzhi\.com\/dl_app.php\?s=(\d+)'

class MyappCrawlSpiderTest(SpiderTest):
    """MyappCrawlSpiderTest 测试 应用汇 apk爬虫"""
    spider_class = MyappSpider

    __except__ = True

    __test__ = True

    site = 'android.myapp.com'
    entry_pattern    = 'http:\/\/android\.myapp\.com\/android/appdetail.jsp\?appid=(\d+)&pkgid=(\d+)'
    search_pattern   = 'http:\/\/android\.myapp\.com\/android\/qrysearchrslt_web\?actiondetail=\d+&softname=([%0-9A-X]+)'
    download_pattern = 'http:\/\/android\.myapp\.com\/android\/down.jsp\?appid=(\d+)&pkgid=()'


class HiapkCrawlSpiderTest(SpiderTest):
    """HiapkCrawlSpiderTest 测试 安卓 apk爬虫"""
    spider_class = HiapkSpider

    __except__ = True

    __test__ = True

    site = 'apk.hiapk.com'
    entry_pattern    = 'http:\/\/apk\.hiapk\.com\/html/[\d/]+\.html'
    search_pattern   = 'http:\/\/apk\.hiapk\.com\/search\?keyword=([%u0-9A-X]+)&type=0'
    download_pattern = 'http:\/\/apk\.hiapk\.com\/Download.aspx\?aid=(\d+)&em=14'

    def assert_searchurl(self, pattern_str , url , keyword ):
        """assert_searchurl 搜索url断言，圈出关键字比对spider是否正确生成搜索url"""
        self.assertRegexpMatches( url , pattern_str )
        mth = re.match(  pattern_str , url )
        self.assertEquals(mth.group(1) ,repr(keyword)
                                            .lstrip("u").strip("'")
                                            .upper().replace("\\U", "%u") )

def get_settings( settings ):
    """ 获取apkcrawl配置信息 """
    return { k:getattr(settings,k) for k in settings.__dict__ 
                if k[:2] != '__' and type(getattr(settings,k)) in [ list , dict , tuple , long , int, float , str] }

if __name__ == '__main__':
    unittest.main()

