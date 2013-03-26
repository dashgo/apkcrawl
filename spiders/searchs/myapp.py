# -*- encoding=utf-8
'''
File: myapp.py
Author: Hunag Ronghua <huangronghua@ndoo.net>
Date: 2012-12-20 18:22
Description: android.myapp.com apk资源地址抓取spider
'''
import urllib
import urlparse
import json

from scrapy.selector          import HtmlXPathSelector
from scrapy.http              import Request
from apkcrawl.items           import ApkcrawlItem
from apkcrawl.spiders.searchs import ApkbaseSpider
from apkcrawl.settings        import ITER_SEARCH_MAX , ITER_VERSION_MAX

class MyappSpider(ApkbaseSpider):
    name             = 'myapp'
    start_urls       = []
    DOMAIN           = 'android.myapp.com'
    HOME_PAGE        = ''
    #DOWN_URL
    SEARCH_URL       = ''
    DETAIL_URL       = ''

    def _pre_init(self):
        self.HOME_PAGE = 'http://' + self.DOMAIN
        self.allowed_domains = [ self.DOMAIN ]
        #self.DOWN_URL   = self.HOME_PAGE + '/android/down.jsp?appid=%s&pkgid=%s'
        self.DETAIL_URL = self.HOME_PAGE + '/android/appdetail.jsp?appid=%s&pkgid=%s'
        self.SEARCH_URL = self.HOME_PAGE + '/android/qrysearchrslt_web?actiondetail=2&softname=%s'
        super(MyappSpider, self)._pre_init()

    def parse(self, response):
        """ implementate crawl logic """
        res = json.loads(response.body)
        if int(res.get('result', 1)) != 0: yield []
        cnt = 0
        for app in res.get('info', {}).get('value', []):
            cnt+=1
            if cnt > self.ITER_SEARCH_MAX: break
            else: cnt+=1
            entry_url = self.DETAIL_URL % ( app.get('appid') , app.get('pkgid', -1))
            yield Request( url=entry_url, callback=self.parse_entry ,
                        meta={"Referer" : response.url },
                        headers={"Referer":response.url})

    def parse_entry(self, response):
        """ crawl entry detail page, include follow version list url """
        hxs = HtmlXPathSelector(response)
        # crawl entry detail page and mark is_entry=True
        e = self.crawl_version( response )
        e['is_entry'] = True
        yield e
        # iterate version detail page less than ITER_VERSION_LIMIT, not include entry detail page
        cnt = 0
        for v in hxs.select("//ul[@class='mod-app-item']/li/p[@class='app-name']/a/@href").extract():
            detail_url = urlparse.urljoin( response.url , v )
            detail_url = self.refactor_app_url( detail_url )

            if cnt > self.ITER_VERSION_MAX: break
            else: cnt+=1
            yield Request( url=detail_url , callback=self.crawl_version, 
                        meta={"Referer":response.url},
                        headers={"Referer":response.url} )

    def crawl_version(self, response ):
        """ crawl version detail page"""
        hxs            = HtmlXPathSelector(response)
        l              = ApkcrawlItem()
        l['site']      = self.DOMAIN
        l['is_entry']  = False
        l['entry_url'] = response.url
        l['referer_url'] = response.meta['Referer']
        dw_url = hxs.select("//div[@class='installbtn']/a[@class='downtopc']/@href").extract().pop()
        if dw_url:
            l['download_url'] = urlparse.urljoin( response.url , dw_url )
            l['download_url'] = self.refactor_app_url( l['download_url'] )
        return l

    def refactor_app_url(self, url ):
        """ clear other query parameter, keep appid and pkgid """
        up = urlparse.urlparse( url )
        qs = urlparse.parse_qs(up.query)
        nqs = [('appid', qs.get('appid')) , ('pkgid',qs.get('pkgid',-1))]
        up = list(up)
        up[4] = urllib.urlencode(nqs,doseq=True)
        return urlparse.urlunparse(tuple(up))
