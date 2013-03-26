# -*- encoding=utf-8
# Scrapy settings for apkcrawl project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'apkcrawl'

SPIDER_MODULES = ['apkcrawl.spiders']
NEWSPIDER_MODULE = 'apkcrawl.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'

DOWNLOAD_DELAY = 2 
DOWNLOAD_TIMEOUT = 1800

ITEM_PIPELINES = [ ]

######## LOG ######## 
#LOG_ENABLED  = True
#LOG_ENCODING = 'utf-8'
#LOG_FILE     = '/tmp/apkcrawl.log'
#LOG_LEVEL    = 'DEBUG'
#LOG_STDOUT   = Falsko

import os
SETTING_DIR = os.path.dirname(os.path.realpath(__file__)) 

CONCURRENT_REQUESTS = 50
CONCURRENT_REQUESTS_PER_DOMAIN = 20
DOWNLOADER_MIDDLEWARES = {
    #'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 110,
    #'apkcrawl.middlewares.ProxyMiddleware': 100,
    #'scrapy.contrib.downloadermiddleware.httpcompression.HttpCompressionMiddleware': 120,
    'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware':130
    }

HTTPCACHE_ENABLED=True
HTTPCACHE_EXPIRATION_SECS=84600
HTTPCACHE_IGNORE_HTTP_CODES=[504]

RETRY_ENABLED=True
RETRY_TIMES=3

######## apkcrawl env 项目基本环境设置

ITER_SEARCH_MAX      = 3
ITER_VERSION_MAX     = 5
SEARCH_KEYWORDS_FILE = SETTING_DIR + "/keywords.csv"
PROXY_LIST_FILE      = SETTING_DIR + "/proxy.csv"
AAPT_CMD             = "/usr/bin/aapt"
ARIA2C_CMD           = '/usr/local/bin/aria2c'
# apk资源归档文件绝对路径
APK_RESOURCE_ABS_DIR = '/Users/killuavx/Documents/Dev/apkcrawl_res'
# apk资源归档文件相对路径
APK_RESOURCE_REL_DIR = 'apkcrawl'

########## aria2c download config
DOWNLOAD_SERVER_URI                = 'http://localhost:6800/rpc'
DOWNLOAD_TMP_DIR                   = '/tmp'
DOWNLOAD_SPLIT                     = 10
DOWNLOAD_MIN_SPLIT_SIZE            = "1M"
DOWNLOAD_CONTINUE                  = True
DOWNLOAD_MAX_CONNECTION_PER_SERVER = 10
DOWNLOAD_CONCURRENT_DOWNLOADS      = 12
DOWNLOAD_LOG_FILE                  = '/tmp/arica2.log'


########## Database config
DB_HOST    = '172.16.1.92'
DB_NAME    = 'market'
DB_USER    = 'root'
DB_PASSWD  = '506506'
DB_CHARSET = 'utf8'
