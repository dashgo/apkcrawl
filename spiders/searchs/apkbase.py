# -*- encoding=utf-8
'''
File: apkbase.py
Author: Hunag Ronghua <huangronghua@ndoo.net>
Date: 2012-12-20 23:45
Description: 搜索抓取apk资源地址基类
'''
import urllib
import urlparse
from scrapy            import log
from scrapy.selector   import HtmlXPathSelector
from scrapy.http       import Request
from scrapy.spider     import BaseSpider
from apkcrawl.items    import ApkcrawlItem
from apkcrawl.settings import SEARCH_KEYWORDS_FILE, ITER_SEARCH_MAX , ITER_VERSION_MAX
from apkcrawl.utils    import search_keys

SEARCH_KEYWORDS = search_keys( SEARCH_KEYWORDS_FILE )

class ApkbaseSpider(BaseSpider):
    """ 爬取apk数据spider基类 """

    allowed_domains  = []

    start_urls       = []

    ##
    # @name 爬虫自定义参数
    # @{ 
    name             = 'apkbase'
    DOMAIN           = 'apkbase.com'
    HOME_PAGE        = ''
    SEARCH_URL       = ''
    ITER_SEARCH_MAX  = ITER_SEARCH_MAX
    ITER_VERSION_MAX = ITER_VERSION_MAX

    ##
    # @brief 搜索页解析软件入口地址的xpath
    XPATH_SEARCH_RECORD_URL= ''
    ##
    # @brief 详情页解析软件其他版本入口地址的xpath
    XPATH_DETAIL_VERSION_URL= ''
    ##  @} 

    ##
    # @brief 
    #
    # @param *a
    # @params **kw
    # |--@param str|unicode keyword 若制定则以搜索一个关键字形式爬取信息
    #
    # @return void
    def __init__(self, *a, **kw):
        """ 
            若未设定keyword则以关键字列表 settings/keywords.csv组织搜索地址爬取软件信息
        """
        self._pre_init()
        w = kw.get('keyword')
        if w is not None:
            w= w if isinstance( w , unicode) else w.decode('utf-8')
            self.start_urls = self.keywords2urls( [ w ] ) 

        super(ApkbaseSpider,self).__init__(*a, **kw)

    ##
    # @brief 初始化前的挂钩点
    # @override 
    #
    # @return 
    def _pre_init(self):
        """
            初始化前的挂钩点
            使用关键字拼接搜索地址
        """
        self.start_urls            = self.keywords2urls( SEARCH_KEYWORDS )

    ##
    # @brief scrapy的spider，根据开始爬虫url封装请求体
    #
    # @param unicode url
    #
    # @return scrapy.http.Request
    def make_requests_from_url(self, url):
        """ 重写scrapy spider的 start_urls 请求创建,添加入口点的Referer,高度伪造请求行为 """
        req = super(ApkbaseSpider,self).make_requests_from_url(url)
        req.headers.setlist('Referer',self.HOME_PAGE)
        return req

    ##
    # @brief spider的爬虫后的响应入口 
    #
    # @param scrapy.http.Response response
    #
    # @return scrapy.http.Request
    def parse(self, response):
        """ 
            解析搜索结果列表
            获取ITER_SEARCH_MAX个软件结果，进入下一轮详细页面的爬虫
        """
        hxs = HtmlXPathSelector(response)
        cnt = 0
        for href in hxs.select( self.XPATH_SEARCH_RECORD_URL).extract():
            cnt+=1
            if cnt > self.ITER_SEARCH_MAX: break
            else: cnt+=1
            yield Request( url=href, callback=self.parse_entry, 
                    meta={"Referer":response.url},
                    headers={"Referer":response.url})

    ##
    # @brief 爬取软件详情页面，跟踪各个版本的入口地址
    #
    # @param response
    #
    # @return scrapy.item.Item
    def parse_entry(self, response):
        """ crawl entry detail page, include follow version list url 
            爬取软件详情页面，获取各版本入口地址
        """
        hxs = HtmlXPathSelector(response)

        # crawl entry detail page and mark is_entry=True
        e = self.crawl_version( response )
        e['is_entry'] = True
        #e['referer_url'] = response.meta['Referer']
        yield e
        # iterate version detail page less than ITER_VERSION_LIMIT, not include entry detail page
        cnt = 0
        for v in hxs.select( self.XPATH_DETAIL_VERSION_URL).extract():
            if cnt > self.ITER_VERSION_MAX: break
            else: cnt+=1
            yield Request( url=v , callback=self.crawl_version , 
                    meta={"Referer": e['entry_url']}, 
                    headers={'Referer':e['entry_url']} )

    ##
    # @brief 具体软件版本信息解析的方法
    # @overwride
    #
    # @param response
    #
    # @return  ApkcrawlItem
    def crawl_version(self, response ):
        """ crawl version detail page"""
        pass

    def keywords2urls(self, keywords ):
        """ 关键字转换拼接搜索地址
        change keyword to search url """
        for kw in keywords:
            yield self.SEARCH_URL % urllib.quote(kw.encode("utf-8"))
