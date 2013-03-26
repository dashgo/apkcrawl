# -*- encoding=utf-8
from apkcrawl.settings.common import *
from os.path import join

######## aapt command
AAPT_CMD="/usr/bin/aapt"

PROXY_LIST_FILE      = join( SETTING_DIR , "proxy.csv" )
SEARCH_KEYWORDS_FILE = join( SETTING_DIR , "keywords.csv" )
HTTPCACHE_EXPIRATION_SECS=0

######## MySQLdb
DB_HOST    = '172.16.1.25'
DB_NAME    = 'market_crawl'
DB_USER    = 'root'
DB_PASSWD  = '506506'
DB_CHARSET = 'utf8'

DOWNLOAD_DELAY = 0 
DOWNLOADER_MIDDLEWARES = {
    ##'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 110,
    ##'apkcrawl.middlewares.ProxyMiddleware': 100,
    'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware':130
    }
ITEM_PIPELINES = [
     # 文件下载流程, 下载队列处理
     'apkcrawl.pipelines.SigninPipeline'          , # 签入下载队列
     'apkcrawl.pipelines.LocalDownloadPipeline'   , # 本地下载至临时路径
     'apkcrawl.pipelines.FileParsePipeline'       , # 文件基本信息解析
     'apkcrawl.pipelines.SignoutPipeline'         , # 签出下载队列，登记下载队列状态

    # apk抓取数据入库处理
     'apkcrawl.pipelines.RecoverResourcePipeline' , # 取出下载队列的基本数据
     'apkcrawl.pipelines.ApkParsePipeline'        , # apk文件信息解析
     'apkcrawl.pipelines.ApkPutStoragePipeline'   , # 将apk下载信息导入抓取软件表信息
     'apkcrawl.pipelines.ApkFileArchivePipeline'  , # apk文件转移至项目目录，更新入库状态和下载队列状态
]

DOWNLOAD_TMP_DIR = os.path.join( os.path.dirname(os.path.dirname(os.path.abspath(__file__)) ) ,
                                        'tests/tmp' )

# apk资源归档文件绝对路径
APK_RESOURCE_ABS_DIR = os.path.join( os.path.dirname(os.path.dirname(os.path.abspath(__file__)) ) ,
                                        'tests/tmp/apkcrawl' )
# apk资源归档文件相对路径
APK_RESOURCE_REL_DIR = 'apkcrawl'
