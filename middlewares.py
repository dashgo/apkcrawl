# -*- encoding=utf-8
import random
from apkcrawl import settings
from apkcrawl.utils import proxy_lists , random_proxy

proxies = proxy_lists( settings.PROXY_LIST_FILE )
 
class ProxyMiddleware(object):

    def process_request(self, request, spider):
        request.meta['proxy'] = random_proxy( proxies )[1]

class EmptyProxyMiddleware(object):

    def process_request(self, request, spider):
        pass
