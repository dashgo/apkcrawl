# -*- encoding=utf-8
'''
File: anzhi.py
Author: Hunag Ronghua <huangronghua@ndoo.net>
Date: 2012-12-19 14:15
Description: www.anzhi.com apk资源地址抓取spider
'''
import urllib
import urlparse
import re
from scrapy.selector          import HtmlXPathSelector
from apkcrawl.items           import ApkcrawlItem
from apkcrawl.spiders.searchs import ApkbaseSpider
from apkcrawl.settings        import ITER_SEARCH_MAX , ITER_VERSION_MAX


class AnzhiSpider(ApkbaseSpider):
    name               = 'anzhi'
    start_urls         = []
    DOMAIN             = 'www.anzhi.com'
    HOME_PAGE          = ''
    SEARCH_URL         = ''

    def _pre_init(self):
        self.allowed_domains  = [ self.DOMAIN ]
        self.HOME_PAGE        = 'http://' + self.DOMAIN
        self.SEARCH_URL       = self.HOME_PAGE + '/search.php?keyword=%s'
        super(AnzhiSpider,self)._pre_init()

    def parse(self, response):
        hxs        = HtmlXPathSelector(response)
        entry_urls = hxs.select("//div[contains(@class,'app_list')]//li/div[@class='app_icon']/a/@href").extract()
        items      = []
        cnt        = 0
        for url in entry_urls:
            if cnt > self.ITER_SEARCH_MAX: break
            else: cnt+=1
            i              = ApkcrawlItem()
            i['is_entry']  = True
            i['entry_url'] = urlparse.urljoin( response.url , url )
            i['referer_url'] = response.url
            i['site'] = self.DOMAIN
            try:
                _id = re.search('soft_(\d+)\.html', url ).group(1)
                i['download_url'] = urlparse.urljoin( response.url , '/dl_app.php?s=' + _id )
            except Exception, e:
                i['download_url'] = ''

            yield i
            #items.append(i)
        #return items

