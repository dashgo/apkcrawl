# -*- encoding=utf-8
import hashlib
from scrapy import log
import apkcrawl.items
from apkcrawl.items import ApkQueueItem, ApkcrawlItem
from apkcrawl import settings
from scrapy.exceptions import DropItem
from apkcrawl.utils import ApkFileParser, ApkDumpFailError,Null

#import apkcrawl.tools

import hashlib
import math
import time
import xmlrpclib
import sh
import shutil
import MySQLdb as mdb

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

null = None

kmysqlduplicateentry = 1062
con=mdb.connect(
        host    = settings.DB_HOST,
        user    = settings.DB_USER,
        passwd  = settings.DB_PASSWD,
        db      = settings.DB_NAME,
        charset = settings.DB_CHARSET)

class ApkcrawlQuery(object):
    """ 爬虫队列查询"""
    con = con

    STATUS_CODE_RESIGNIN       = -1

    STATUS_CODE_SIGNIN         = 0

    STATUS_CODE_SIGNOUT        = 1001

    STATUS_CODE_ERROR_DOWNLOAD = 2000

    STATUS_CODE_ERROR_PARSE    = 3000

    STATUS_CODE_ERROR_SYSTEM   = 4000

    STATUS_CODE_EXCEPTION_SL   = 5000

    ##
    # @brief 
    # @see getItemsByStatus
    #
    # @param limit
    #
    # @return 
    def getSigninItems(self, limit=False):
        """getSigninItems 获取签入状态的记录"""
        return self.getItemsByStatus( self.STATUS_CODE_SIGNIN, limit=limit )

    ##
    # @brief 获取对应状态的下载队列数据
    #
    # @param int status 状态编号
    # @param bool|int limit 最大查询数量, 默认False，不设限
    #
    # @return <generator ApkcrawlItem>
    def getItemsByStatus(self, status , limit=False ):
        """getItemsByStatus 获取对应状态的下载队列数据 """
        sql = """
            SELECT identifier , rqid 
            FROM crawl_resource_queue 
            WHERE res_state=%s 
            """ 
        params = None
        if limit is not False and limit > 0:
            params = ( status , limit )
            sql = sql + " LIMIT 0 , %s"
        else:
            params = ( status , )

        cur = self.con.cursor()
        cur.execute(sql, params )
        for r in cur.fetchall():
             yield ApkcrawlItem(identifier=r[0] , rqid=r[1]) 

        cur.close()

class Empty(object):
    """docstring for Empty"""

    def process_item(self, item, spider):
        return item

def _update_state(self, item, state ):
    """_update_state 更新下载队列状态
        绑定到对应类里，依赖con数据库连接器
        执行完后，方法外提交commit
    """
    cur=self.con.cursor()
    sql = """ UPDATE crawl_resource_queue
              SET res_state=%s,
              update_dt=NOW()
              WHERE identifier=%s
              LIMIT 1 """
    flag = cur.execute(sql , ( state , item['identifier'] ) )
    cur.close()
    return flag

class SigninPipeline(object):
    """ apk信息签入处理 """
    con=con

    def process_item(self, item, spider=null):
        """
            登记apk初始信息，用于下载跟踪与后期重新下载apk
        """
        try:
            cursor = self.con.cursor()
            item['identifier']        = apkcrawl.items.gen_identifier( item )
            item['parent_identifier'] = apkcrawl.items.gen_parent_identifier( item )
            self.signin( cursor , item )
            cursor.close()
            self.con.commit()
            return item
        except mdb.IntegrityError, e:
            if e[0] == kmysqlduplicateentry :
                raise DropItem("Duplicate entry %s"%(e,))
            else:
                raise DropItem("Database InterityError in %s"%(e,))
        except mdb.Error, e:
            raise DropItem("Database Error in %s"%(e))

    def signin(self, cursor , item ):
        """ signin 资源签入下载队列,状态为0 """
        sql = """ 
                INSERT INTO 
                    crawl_resource_queue (  csid         , 
                                            identifier   , 
                                            referer_url  , 
                                            entry_url    , 
                                            download_url , 
                                            file_name    , 
                                            create_dt    ,
                                            update_dt    ,
                                            parent_rqid
                                            )
                SELECT 
                    ( SELECT csid FROM crawl_site WHERE site_domain=%s LIMIT 1) AS csid,
                    %s         AS identifier ,
                    %s         AS referer_url ,
                    %s         AS entry_url ,
                    %s         AS download_url ,
                    %s         AS file_name ,
                    NOW()      AS create_dt ,
                    NOW()      AS update_dt ,
                    ( SELECT rqid FROM crawl_resource_queue WHERE identifier=%s LIMIT 1) AS parent_rqid
                LIMIT 1
                """
        flag = cursor.execute(sql , (
                                 item['site']                , # for csid
                                 item['identifier']          , #
                                 item['referer_url']         ,
                                 item['entry_url']           ,
                                 item['download_url']        ,
                                 item['identifier'] + ".apk" ,
                                 item['parent_identifier']   , # for parent_rqid
                                 ))
        item['rqid'] = cursor.lastrowid
        return flag

class AsynDownloadPipeline(object):
    """
    ApkAsynDownloadPipeline 调用下载组件，下载apk文件
    """

    def __init__(self):
        """__init__"""
        serv=xmlrpclib.ServerProxy( settings.DOWNLOAD_SERVER_URI )

    def process_item(self, item , spider=null):
        """process_item"""
        try:
            self.dw_item( item )
            return item
        except Exception, e:
            raise DropItem( e[0] ,  settings.DOWNLOAD_SERVER_URI)

    def dw_item(self, item):
        """ 下载文件 """
        self.serv.aria2.addUri([ item['download_url'] ], 
                { 'dir': settings.DOWNLOAD_TMP_DIR, "referer":item['entry_url'], "out": item['identifier'] + ".apk"})

class LocalDownloadPipeline(object):
    """ ApkLocalDownloadPipeline 调用下载组件，下载apk文件
       下载失败，记录队列资源状态2xxx
    """

    con = con

    _update_state = _update_state

    def process_item(self, item , spider=null):
        """process_item"""
        try:
            self.dw_item( item )
            return item
        except Exception, e:
            res_state = 2001 # 下载文件异常中断
            try: 
                self._update_state( item , res_state )
                self.con.commit()
            except Exception, e: pass
            raise DropItem( res_state , e[0] , item )

    def dw_item(self, item):
        """ 下载文件 """
        sh.aria2c = sh.Command(settings.ARIA2C_CMD)
        args = { 'dir'                       : settings.DOWNLOAD_TMP_DIR                   ,
                    "referer"                   : item['entry_url']                           ,
                    "out"                       : item['identifier'] + ".apk"                 ,
                    "user-agent"                : settings.USER_AGENT                         ,
                    "split"                     : settings.DOWNLOAD_SPLIT                     ,
                    "min-split-size"            : settings.DOWNLOAD_MIN_SPLIT_SIZE            ,
                    "continue"                  : settings.DOWNLOAD_CONTINUE                  ,
                    "max-connection-per-server" : settings.DOWNLOAD_MAX_CONNECTION_PER_SERVER ,
                    "max-concurrent-downloads"  : settings.DOWNLOAD_CONCURRENT_DOWNLOADS      ,
                    "log"                       : settings.DOWNLOAD_LOG_FILE ,
                }
        arg1 = item['download_url']
        sh.aria2c( arg1, **args)

import os
apkparser = ApkFileParser()
class FileParsePipeline(object):
    """
    FileParsePipeline 获取文件信息
    获取错误记录 资源队列状态3xxx
    """

    con=con

    _update_state = _update_state

    def process_item(self, item , spider=null):
        apkfile = os.path.join(
                settings.DOWNLOAD_TMP_DIR, item['identifier'] + ".apk")
        try:
            item['fileinfo'] = apkparser.fileparse( apkfile )
            return item
        except OSError, e:
            errno = 1
            res_state = "3{0}".format(str(errno).zfill(3)) 
            self._update_state( item , res_state )
            self.con.commit()
            #try: 
            #except Exception, e: pass
            raise DropItem("file:%s not exists" % apkfile)

class SignoutPipeline(object):
    """Signout 完成下载后台签出(将下载并解析成功的apk文件，同步到ApkSignin阶段录入数据)"""

    con=con

    def process_item(self, item , spider=null):
        log.msg( "ApkSignout item: %s<%s>" %(item['identifier'] ,item['download_url'] ) 
                , level=log.INFO, spider=spider )
        try:
            cur = self.con.cursor()
            self.signout( cur , item )
            self.con.commit()
            cur.close()
            log.msg( "ApkSignout item Finish: %s<%s>" %(item['identifier'] ,item['download_url'] ) 
                    , level=log.INFO, spider=spider )
            return item
        except Exception, e:
            log.msg( "ApkSignout item Drop: %s<%s>" %(item['identifier'] ,item['download_url'] ) 
                    , level=log.WARNING, spider=spider )
            raise DropItem("Database Update Break in %",e )

    def signout(self, cur, item):
        """signout 下载完成，更新状态为签出"""
        sql = """
            UPDATE crawl_resource_queue 
            SET res_state = 1001,
                update_dt = NOW(),
                file_size = %s,
                file_md5  = %s,
                file_name = %s,
                file_path = %s
            WHERE identifier=%s
            LIMIT 1; """
        return cur.execute( sql, ( item['fileinfo']['file_size'] ,
                            item['fileinfo']['file_md5']  ,
                            item['fileinfo']['file_name'] ,
                            settings.DOWNLOAD_TMP_DIR ,
                            item['identifier']
                            ) )

class RecoverResourcePipeline(object):
    """ 获取资源队列内的数据
    """

    con=con

    def process_item(self, item, spider=null):
        try:
            cur= self.con.cursor()
            return self.recover( cur , item )
        except Exception, e:
            raise DropItem( e[1] )
        finally:
            cur.close()

    def recover(self, cur , item ):
        cur.execute(""" SELECT crq.rqid          ,
                               crq.parent_rqid   ,
                               crq.csid          ,
                               cs.site_domain    ,
                               crq.identifier    ,
                               crq.referer_url   ,
                               crq.entry_url     ,
                               crq.download_url  ,
                               crq.create_dt     ,
                               crq.update_dt     ,
                               crq.res_state     ,
                               crq.file_md5      ,
                               crq.file_size     ,
                               crq.file_name     ,
                               crq.file_path
                        FROM crawl_resource_queue AS crq
                        INNER JOIN crawl_site AS cs ON ( cs.csid = crq.csid )
                        WHERE identifier=%s
                        LIMIT 1""" , ( item['identifier'], ))
        rs = cur.fetchone()
        if rs:
            item                 = ApkQueueItem()
            item['rqid']         = rs[0 ]
            item['parent_rqid']  = rs[1 ]
            item['csid']         = rs[2 ]
            item['site']         = rs[3 ]
            item['identifier']   = rs[4 ]
            item['referer_url']  = rs[5 ]
            item['entry_url']    = rs[6 ]
            item['download_url'] = rs[7 ]
            item['create_dt']    = rs[8 ]
            item['update_dt']    = rs[9 ]
            item['res_state']    = rs[10]
            item['fileinfo']     = { "file_md5"  :rs[11 ] ,
                                     "file_size" :rs[12],
                                     "file_name" :rs[13],
                                     "file_path" :rs[14], 
                                   }
            item['is_entry']     = True if item['parent_rqid'] == 0 else False
            return item
        else:
            raise DropItem( """ Not find item in database """ , item )

class ApkParsePipeline(object):
    """
    ApkParsePipeline 解析包文件信息
    解析错误记录 资源队列状态3xxx
    """
    con=con

    _update_state = _update_state

    def process_item(self, item , spider=null):
        apkfile = os.path.join( item['fileinfo']['file_path'] , 
                                item['fileinfo']['file_name'] )
        try:
            item['apkinfo']  = apkparser.apkparse( apkfile )
            return item
        except ApkDumpFailError, e:
            errno = 1
            res_state = "3{0}".format(str(errno).zfill(3)) 
            try:
                self._update_state( item , res_state )
                self.con.commit()
            except Exception, e:pass
            raise DropItem("apk file:%s dump fail" % apkfile)

class ApkPutStoragePipeline(object):
        """ 入库操作
            继ApkParsePipeline之后，将数据入库到crawl_package/package_version内 
        """

        con = con
        ##
        # @brief 
        #
        # @param ApkQueueItem item
        #
        # @return item
        def process_item(self, item, spider=Null ):
            """process_item"""
            return self.putstorage( item )

        def putstorage(self, item ):
            """ putstorage 转移资源数据至crawl_pacage/package_version """
            cur = self.con.cursor()
            try:
                ( flag ,  item ) = self.rd_package( cur, item )
            except mdb.Error, e:
                if e[0] == kmysqlduplicateentry :
                    pass # 业务数据重复，不影响操作
                else:
                    raise DropItem( 4002 , e[1]) # 系统数据库问题中断

            try:
                (flag , item )= self.rd_package_version( cur, item )
                self.con.commit()
            except mdb.Error, e:
                self.con.rollback()
                if e[0] == kmysqlduplicateentry :
                    state = 5001
                    cur   = self.con.cursor()
                    self._update_resource_state( cur , item , state)
                    self.con.commit()
                    raise DropItem( state, e[1]) # 业务数据重复，file_md5冲突中断操作
                else:
                    raise DropItem( 4002 , e[1]) # 系统数据库问题中断
            finally:
                cur.close()

            return item

        def rd_package(self, cur, item ):
            """ crawl_package"""
            sql = """
                INSERT IGNORE INTO
                crawl_package( csid , pkg_id , pkg_name , create_dt , update_dt )
                SELECT
                    ( SELECT csid FROM crawl_site WHERE site_domain=%s LIMIT 1) AS csid ,
                    ( SELECT pkg_id FROM ma_package WHERE pkg_name=%s LIMIT 1)  AS pkg_id,
                    %s AS pkg_name , NOW() AS create_dt , NOW() AS update_dt
                LIMIT 1
                ON DUPLICATE KEY UPDATE update_dt=NOW(), pkg_id=VALUES(pkg_id)
                """
            params = ( item['site'] , item['apkinfo']['pkg_name'],
                                        item['apkinfo']['pkg_name'])
            flag = cur.execute( sql , params )
            item['cpid'] = cur.lastrowid
            return (flag , item )

        def rd_package_version(self, cur, item ):
            """ crawl_package_version"""
            sql = """
                INSERT INTO
                crawl_package_version( cpid        , pkg_id    , version_code , version_name ,
                                       crawl_state , file_name , apk_md5      , file_size    ,
                                       create_dt   , update_dt , rqid         , is_entry      )
                SELECT
                    cp.cpid,
                    ( SELECT pkg_id FROM ma_package WHERE pkg_name=%s LIMIT 1)  AS pkg_id,
                    %s AS version_code , %s AS version_name ,
                    %s AS crawl_state , %s AS file_name , %s AS apk_md5 , %s AS file_size ,
                    NOW() AS create_dt, NOW() AS update_dt, %s AS rqid  , %s AS is_entry
                FROM crawl_package AS cp, crawl_site AS cs
                WHERE cs.site_domain=%s AND cs.csid=cp.csid AND cp.pkg_name=%s
                LIMIT 1
            """
            crawl_state = 0
            is_entry    = 0 if item['parent_rqid'] else 1
            params = ( item['apkinfo']['pkg_name']     , 
                       item['apkinfo']['version_code'] , item['apkinfo']['version_name'] ,
                       crawl_state                     , item['fileinfo']['file_name']   ,
                       item['fileinfo']['file_md5']    , item['fileinfo']['file_size']   ,
                       item['rqid']                    , is_entry                        ,
                       item['site']                    , item['apkinfo']['pkg_name']     ,
                     )
            flag = cur.execute( sql , params  )
            item['res_id'] = cur.lastrowid
            return ( flag , item )

        def _update_resource_state(self , cur , item , state):
            """更新下载队列状态 """
            sql = """ UPDATE crawl_resource_queue
                      SET res_state = %s,
                      update_dt=NOW()
                      WHERE rqid=%s
                      LIMIT 1 """
            return cur.execute(sql , ( state , item['rqid'] ) )

class ApkFileArchivePipeline(object):
    """ApkFileArchivePipeline
       depand on ApkQueueItem
       | <rqid, res_id>
    """

    partition_limit = 1000

    con = con

    def process_item(self, item , spider=Null):
        """process_item"""
        cur = self.con.cursor()
        try:
            self._mv( item )
            self._update_package_version_state_success( cur , item )
            self._update_resource_state_success( cur, item )
            self.con.commit()
            return item
        except Exception, e:
            self.con.rollback()
            _cur         = self.con.cursor()
            err_pv_code  = -1 # 数据转移失败
            err_res_code = 4001 # 系统错误，转移文件失败
            self._update_package_version_state( _cur , item , err_pv_code )
            self._update_resource_state( _cur , item , err_res_code )
            _cur.close()
            self.con.commit()
            raise DropItem( err_res_code , e[0] , item , e)
        finally:
            cur.close()

    def _mv(self, item ):
        """_mv 移动apk文件至最终归档文件夹下，并重命名文件
           更改item['fileinfo']['file_path'] , item['fileinfo']['file_name']至归档后的文件
        """
        dst_d = self._gen_apkres_abs_path( item )
        dst_f = str(item['res_id']) + '.apk' 
        dst   = os.path.join( dst_d , dst_f )

        if os.path.isdir( dst_d ) == False :
            os.mkdir( dst_d , 0777)

        src = os.path.join( item['fileinfo']['file_path'] , item['fileinfo']['file_name'] )

        rel_d = self._gen_apkres_rel_path( item )
        item['fileinfo']['file_path'] = rel_d
        item['fileinfo']['file_name'] = dst_f

        shutil.move( src , dst )

        return item

    def _gen_apkres_rel_path(self, item):
        """_gen_apkres_rel_path 生成文件相对路径目录"""
        return os.path.join( settings.APK_RESOURCE_REL_DIR,
                            str(int(math.floor(item['res_id']/ self.partition_limit ))) )

    def _gen_apkres_abs_path(self, item):
        """_gen_apkres_rel_path 生成文件绝对路径目录"""
        return os.path.join( settings.APK_RESOURCE_ABS_DIR,
                            str(int(math.floor(item['res_id']/ self.partition_limit ))) 
                            )

    def _update_package_version_state_success(self, cur , item):
        """更新入库版本数据状态完成,文件名变更
        """
        sql = """ UPDATE crawl_package_version
                  SET crawl_state = %s,
                  update_dt=NOW(),
                  file_name=%s 
                  WHERE res_id=%s
                  LIMIT 1 """
        crawl_state = 1
        return cur.execute( sql , ( crawl_state , item['fileinfo']['file_name'] , item['res_id'] ) )

    def _update_package_version_state(self, cur , item , crawl_state):
        """更新入库版本数据状态
        """
        sql = """ UPDATE crawl_package_version
                  SET crawl_state = %s,
                  update_dt=NOW()
                  WHERE res_id=%s
                  LIMIT 1 """
        return cur.execute( sql , ( crawl_state , item['res_id'] ) )

    def _update_resource_state_success(self, cur , item ):
        """更新下载队列状态为完成,更新文件名和文件路径
        """
        sql = """ UPDATE crawl_resource_queue
                  SET res_state = %s,
                  update_dt=NOW(),
                  file_name=%s , 
                  file_path=%s 
                  WHERE rqid=%s
                  LIMIT 1 """
        res_state = 1
        return cur.execute(sql , ( res_state , item['fileinfo']['file_name'] , 
                                   item['fileinfo']['file_path'], item['rqid'] ) )

    def _update_resource_state(self , cur , item , state):
        """更新下载队列状态 """
        sql = """ UPDATE crawl_resource_queue
                  SET res_state = %s,
                  update_dt=NOW()
                  WHERE rqid=%s
                  LIMIT 1 """
        return cur.execute(sql , ( state , item['rqid'] ) )

