# -*- encoding=utf-8
from apkcrawl.settings.common import *
from os.path import join

DOWNLOAD_DELAY = 5 

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

######## env
SEARCH_KEYWORDS_FILE = join( SETTING_DIR , "keywords.csv" )

######## aapt command
AAPT_CMD="/usr/bin/aapt"
ARIA2C_CMD = '/opt/local/bin/aria2c'

PROXY_LIST_FILE = join( SETTING_DIR , "proxy.csv" )
SEARCH_KEYWORDS_FILE = join( SETTING_DIR , "keywords.csv" )

# apk资源归档文件绝对路径
APK_RESOURCE_ABS_DIR = os.path.join( '/data0/www/nmarket/',
                                        '/apkcrawl' )


######## MySQLdb
DB_HOST    = '172.16.1.92'
DB_NAME    = 'market'
DB_USER    = 'root'
DB_PASSWD  = '506506'
DB_CHARSET = 'utf8'


