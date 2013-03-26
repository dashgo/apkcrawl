# -*- encoding=utf-8
from apkcrawl.settings.common import *
from os.path import join

######## aapt command
AAPT_CMD="/Users/newuser/Downloads/android-sdk/platform-tools/aapt"
ARIA2C_CMD = '/opt/local/bin/aria2c'

PROXY_LIST_PATH = join( SETTING_DIR , "proxy.csv" )
SEARCH_KEYWORDS_FILE = join( SETTING_DIR , "test_keywords.csv" )

DOWNLOAD_DELAY = 0 

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

DOWNLOAD_TMP_DIR='/Users/newuser/PycharmProjects/apkcrawl/apkcrawl/tests/tmp'
DOWNLOAD_SERVER_URI='http://localhost:6800/rpc'

HTTPCACHE_ENABLED=True
HTTPCACHE_EXPIRATION_SECS=0
HTTPCACHE_IGNORE_HTTP_CODES=[504]

# apk资源归档文件绝对路径
APK_RESOURCE_ABS_DIR = '/Users/newuser/PycharmProjects/apkcrawl/apkcrawl/tests/backup'
# apk资源归档文件相对路径
APK_RESOURCE_REL_DIR = 'apkcrawl'

######## MySQLdb
DB_HOST    = '127.0.0.1'
DB_NAME    = 'market_crawl'
DB_USER    = 'root'
DB_PASSWD  = '12345'
DB_CHARSET = 'utf8'
