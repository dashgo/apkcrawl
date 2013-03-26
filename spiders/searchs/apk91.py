# -*- encoding=utf-8
'''
File: apk91.py
Author: Hunag Ronghua <huangronghua@ndoo.net>
Date: 2012-12-19 18:15
Description: apk.91.com apk资源地址抓取处理
'''
import urllib
import urlparse
from scrapy                   import log
from scrapy.selector          import HtmlXPathSelector
from scrapy.http              import Request
from apkcrawl.items           import ApkcrawlItem
from apkcrawl.settings        import ITER_SEARCH_MAX , ITER_VERSION_MAX
from apkcrawl.spiders.searchs import ApkbaseSpider
from apkcrawl.utils           import search_keys
from scrapy.exceptions        import DropItem

class Apk91Spider(ApkbaseSpider):
    name = 'apk91'
    start_urls       = []
    DOMAIN           = 'apk.91.com'

    def _pre_init(self):
        self.HOME_PAGE                = 'http://' + self.DOMAIN
        self.allowed_domains          = [ self.DOMAIN, 'd.91.com', 'dl.91rb.com']
        self.SEARCH_URL               = self.HOME_PAGE + '/soft/Android/search/1_5_0_0_%s'
        #self.XPATH_SEARCH_RECORD_URL  = "//div[contains(@class,'soft_list_con')]//h5/a/@href"
        self.XPATH_SEARCH_RECORD_URL  = "//div[@class='soft_conc']//h5/a/@href"
        self.XPATH_DETAIL_VERSION_URL = "//div[@id='HistoryFloat']//ul/li/a/@href"
        super(Apk91Spider,self)._pre_init()

    def crawl_version(self, response ):
        """ crawl version detail page"""

        hxs = HtmlXPathSelector(response)
        l = ApkcrawlItem()
        l['site']      = self.DOMAIN
        l['is_entry']  = False
        l['entry_url'] = response.url
        l['referer_url'] = response.meta['Referer']

        # clear query parameter `m` and rebuild download url by entry(referer) page url
        # 搜索页面可能返回无效404的软件详情地址,对其忽略处理
        # 如：http://apk.91.com/Soft/Android/alonetheme.html
        try:
            dw_xpath = "//div[@class='soft_detail_btn']/a[@class='link1']/@href"
            path        = hxs.select( dw_xpath ).extract()[0]
        except Exception, e:
            raise DropItem("Invalid Page")

        up          = urlparse.urlparse(path)
        qs          = urlparse.parse_qs(up.query)
        qs.pop('m')
        up          = list(up)
        cur_up      = urlparse.urlparse(response.url)
        up[0], up[1], up[4] = cur_up.scheme, cur_up.netloc, urllib.urlencode(qs, doseq=True)
        l['download_url'] = urlparse.urlunparse( tuple( up ) )
        return l
