# -*- encoding=utf-8
'''
File: hiapk.py
Author: Hunag Ronghua <huangronghua@ndoo.net>
Date: 2012-12-18 15:14
Description: apk.hiapk.com apk资源地址抓取spider
'''
import urlparse
from scrapy.selector   import HtmlXPathSelector
from scrapy.http       import Request
from apkcrawl.items    import ApkcrawlItem
from apkcrawl.spiders.searchs  import ApkbaseSpider
from apkcrawl.settings import ITER_SEARCH_MAX , ITER_VERSION_MAX

class HiapkSpider(ApkbaseSpider):
    name             = 'hiapk'
    start_urls       = []
    DOMAIN           = 'apk.hiapk.com'

    def _pre_init(self):
        self.allowed_domains = [ self.DOMAIN ]
        self.HOME_PAGE = 'http://' + self.DOMAIN
        self.SEARCH_URL = self.HOME_PAGE + '/search?keyword=%s&type=0'
        self.XPATH_SEARCH_RECORD_URL  = "//div[@id='Soft_SearchList']//span[contains(@class,'list_title')]/a/@href"
        self.XPATH_DETAIL_VERSION_URL = "//div[@id='otherSoftBox']//a[@class='aimg']/@href"
        super(HiapkSpider, self)._pre_init()

    def crawl_version(self, response ):
        hxs           = HtmlXPathSelector(response)
        l             = ApkcrawlItem()
        url           = response.url
        pr            = urlparse.urlparse(response.url)
        l['site']     = self.DOMAIN
        l['is_entry'] = False
        l['referer_url'] = response.meta['Referer']
        if pr.query.__len__():
            _pr    = list(pr)
            _pr[4] = ''
            url    = urlparse.urlunparse(tuple(_pr))
        l['entry_url'] = url
        l['download_url'] = hxs.select("//div[@class='inner_right200 d_r_t35']//div[contains(@class,'btnmarg')]/a/@href").extract().pop()
        return l

    def keywords2urls(self, keywords ):
        """ change keyword to search url """
        urls = []
        for kw in keywords:
            yield self.SEARCH_URL % kw.__repr__().lstrip("u").strip("'").upper().replace("\\U","%u")
