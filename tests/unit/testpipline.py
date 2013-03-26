# -*- encoding=utf-8
import os
import unittest2 as unittest
from apkcrawl.pipelines import SigninPipeline, \
                               LocalDownloadPipeline,\
                               FileParsePipeline,\
                               SignoutPipeline,\
                               RecoverResourcePipeline,\
                               ApkParsePipeline, ApkPutStoragePipeline,\
                               ApkFileArchivePipeline
from apkcrawl.items import ApkcrawlItem, ApkQueueItem
from scrapy.exceptions import DropItem
from apkcrawl.utils import ApkDumpFailError
from apkcrawl.tests import get_projectpath
from apkcrawl import settings
import copy 
import math

class ApkQueueMock(object):
    """ApkQueueMockFactory"""

    @classmethod
    def fixtures(cls , rd , t=ApkcrawlItem ):
        """fixtures"""
        from apkcrawl.tests.fixtures.items import apkcrawlitems
        item = None
        if type(rd) is int:
            item = ApkcrawlItem( **apkcrawlitems[rd] )
        else:
            item = ApkcrawlItem( **rd )
        return item

    @classmethod
    def delmock(cls, item):
        pass


class SigninPipelineTest(unittest.TestCase):
    """ signin 下载队列签入测试 """

    name = 'signin'

    test_type = 'unit'

    fixture_idx = 0

    def setUp(self):
        self._item = ApkQueueMock.fixtures( self.fixture_idx, ApkcrawlItem  )
        self._pipcls = SigninPipeline

    def tearDown(self):
        if hasattr(self,'_rm_signinitem'):
            self.remove_signinitem( self._rm_signinitem )

    def remove_signinitem(self, item):
        """ 删除下载队列数据 """
        pipeline = self._pipcls()
        cur = pipeline.con.cursor()
        sql = """ DELETE FROM crawl_resource_queue
                  WHERE rqid=%s"""
        cur.execute( sql , ( item['rqid'], ) )
        pipeline.con.commit()

    def test_normal_signin(self):
        """ test_normal_sigin 测试正常签入下载队列 """
        pipeline = self._pipcls()
        item = self._item 

        item = pipeline.process_item( item )
        self._rm_signinitem = item

        # check sha1 length 
        self.assertEquals( 40 , len(item['identifier'] ) )
        if item['is_entry']:
            self.assertEquals( "" , item['parent_identifier'])
        else:
            self.assertEquals( 40 , len(item['parent_identifier']))
        self.assertIsNotNone( item['rqid'] )
        return item

    def test_exception_signin_duplicate(self):
        """ test_exception_signin 异常签入，重复相同的下载队列资源，抛出异常并中断处理"""
        self._item = ApkQueueMock.fixtures( 1, ApkcrawlItem  )
        item = self._item

        pipeline = self._pipcls()
        item = pipeline.process_item( item )
        self._rm_signinitem = item
        self.assertRaises( DropItem , pipeline.process_item , item=item )

class LocalDownloadPipelineTest(SigninPipelineTest):
    """ 本地下载测试 """

    name = 'localdown'

    fixture_idx = 2

    def setUp(self):
        super(LocalDownloadPipelineTest , self).setUp()
        self._downloadpipcls = LocalDownloadPipeline

    def tearDown(self):
        if hasattr(self,'_rm_downloaditem'):
            self.rmitem( self._rm_downloaditem)
        super(LocalDownloadPipelineTest , self).tearDown()
        pass

    def rmitem(self , item ):
        fp = os.path.join( settings.DOWNLOAD_TMP_DIR,  
                            item['identifier'] + ".apk" )
        try:
            os.remove( fp )
        except Exception, e:
            pass

    def test_normal_download(self):
        """ test_normal_download 测试正常的本地下载功能 """
        pipeline = self._downloadpipcls()
        qitem = self.test_normal_signin()
        item = pipeline.process_item( qitem )

        fp = os.path.join( settings.DOWNLOAD_TMP_DIR,  
                            item['identifier'] + ".apk" )
        self.assertTrue( os.path.isfile(fp) )
        self._rm_downloaditem= item
        return item

    def test_exception_download(self):
        """ test_exception_download 异常下载，抛出错误并中断，更新下载队列状态"""
        pipeline = self._downloadpipcls()
        item = self.test_normal_signin()
        item['download_url'] = 'http://apk.hiapk.com/404';
        self.assertRaises( DropItem , pipeline.process_item , item )
        fp = os.path.join( settings.DOWNLOAD_TMP_DIR,  
                            item['identifier'] + ".apk" )
        self.assertFalse( os.path.isfile(fp) )
        self._rm_downloaditem = item

        rrp = RecoverResourcePipeline()
        chitem = rrp.process_item( item )
        self.assertEquals( 2001 , chitem['res_state'] )

        return item

class FileParsePipelineTest(LocalDownloadPipelineTest):
    """ 文件解析测试"""

    name = 'fileparse'

    fixture_idx = 3

    def setUp(self):
        super(FileParsePipelineTest, self).setUp()
        self._fileparsepipcls = FileParsePipeline

    def tearDown(self):
        super(FileParsePipelineTest, self).tearDown()

    def test_normal_fileparse(self):
        """ test_normal_fileparse 正常解析文件数据 """
        item = self.test_normal_download()
        pipeline = self._fileparsepipcls()
        item = pipeline.process_item( item )
        self.assertEquals( item['fileinfo']['file_name'] , 
                                item['identifier'] + ".apk")
        self.assertEquals( 32 , len(item['fileinfo']['file_md5']))
        self.assertGreater( item['fileinfo']['file_size'] , 10 )

        return item

    def test_exception_fileparse(self):
        """ test_exception_fileparse 解析文件数据错误-文件不存在，抛出异常中断操作 """
        self.fixture_idx = 4
        item = self.test_normal_download()

        src = os.path.join( settings.DOWNLOAD_TMP_DIR , item['identifier'] + ".apk" )
        dst = os.path.join( settings.DOWNLOAD_TMP_DIR , item['identifier'] + ".apk.bk")
        os.rename( src , dst )
        pipeline = self._fileparsepipcls()
        self.assertRaises( DropItem , pipeline.process_item , item )
        os.rename( dst, src )

        rrp = RecoverResourcePipeline()
        chitem = rrp.process_item( item )
        self.assertEquals( 3001 , chitem['res_state'] )

class SignoutPipelineTest(FileParsePipelineTest):
    """ 下载队列签出测试 """

    name = 'signout'

    fixture_idx = 5

    def setUp(self):
        super( SignoutPipelineTest , self).setUp()
        self._signoutpipcls = SignoutPipeline

    def tearDown(self):
        super( SignoutPipelineTest , self).tearDown()

    def test_normal_signout(self):
        """ test_normal_signout 下载队列正常签出 """
        pipeline = self._signoutpipcls()
        item = self.test_normal_fileparse()

        item = pipeline.process_item( item )

        rrp    = RecoverResourcePipeline()
        chitem = rrp.process_item( item )
        self.assertEquals( 1001 , chitem['res_state'] )
        self.assertEquals( settings.DOWNLOAD_TMP_DIR , chitem['fileinfo']['file_path'] )

        self.assertEquals( chitem['fileinfo']['file_name'] , 
                                    chitem['identifier'] + ".apk")
        self.assertEquals( 32 , len(chitem['fileinfo']['file_md5']))
        self.assertGreater( item['fileinfo']['file_size'] , 10 )

        return item

class  RecoverResourcePipelineTest( SignoutPipelineTest ):
    """ 获取下载队列记录信息测试 """

    name = 'recres'

    def setUp(self):
        self._recrespipcls = RecoverResourcePipeline
        super(RecoverResourcePipelineTest , self).setUp()

    def tearDown(self):
        super(RecoverResourcePipelineTest, self).tearDown()

    def test_normal_recover(self):
        """ test_normal_recover 正常获取已下载完成的资源信息"""
        item = self.test_normal_signout()
        pipeline = self._recrespipcls()
        qitem = pipeline.process_item( item=item )

        self.assertIsNotNone( qitem['rqid'] )
        self.assertIsNotNone( qitem['parent_rqid'] )
        self.assertIsNotNone( qitem['is_entry'] )
        self.assertIsNotNone( qitem['fileinfo'] )
        self.assertIsNotNone( qitem['csid'] )
        self.assertIsNotNone( qitem['site'] )
        self.assertIsNotNone( qitem['fileinfo']['file_md5'] )
        self.assertIsNotNone( qitem['fileinfo']['file_size'] )
        self.assertIsNotNone( qitem['fileinfo']['file_name'] )
        self.assertEquals( str(qitem['fileinfo']['file_name']).split('.')[-1:][0] , 'apk' )
        self.assertIsNotNone( qitem['fileinfo']['file_path'] )
        self.assertIsNotNone( qitem['res_state'])
        #self.assertEquals( qitem['res_state'] , 1001 )
        return qitem

    def test_exception_not_exists(self):
        """ test_exception_not_exists 下载队列数据记录不存在, 抛出异常中断处理 """
        item = self.test_normal_signout()
        item['identifier'] = '123123'

        pipeline = self._recrespipcls()
        self.assertRaises( DropItem , pipeline.process_item, item=item )

class ApkParsePipelineTest( RecoverResourcePipelineTest ):
    """ApkParsePipelineTest 测试解析apk包信息"""

    name = 'apkparse'

    fixture_idx = 6

    def setUp(self):
        super(ApkParsePipelineTest, self).setUp()
        self._apkparsepipecls = ApkParsePipeline

    def tearDown(self):
        super(ApkParsePipelineTest, self).tearDown()

    def test_normal_apkparse(self):
        """ test_normal_parse 测试正常解析apk"""
        item = self.test_normal_recover()
        pipeline = self._apkparsepipecls()

        qitem = pipeline.process_item( item )

        self.assertIsNotNone( qitem['apkinfo'] )
        self.assertIsNotNone( qitem['apkinfo']['pkg_name'] )
        self.assertIsNotNone( qitem['apkinfo']['version_name'] )
        self.assertIsNotNone( qitem['apkinfo']['version_code'] )
        self.assertIsInstance(qitem['apkinfo']['version_code'], int )

        return qitem

    def test_exception_apkparse(self):
        """ test_exception_parse 测试找不到文件、解析包错误，抛出异常中断"""

        qitem = self.test_normal_recover()
        # 暂存状态，后面恢复数据
        fname,fpath = qitem['fileinfo']['file_name'] , qitem['fileinfo']['file_path']
        state = qitem['res_state']

        pipeline = self._apkparsepipecls()

        recrespipeline = self._recrespipcls()

        # 以不存在的文件做测试
        qitem['fileinfo']['file_name'] = 'dropitem_test.apk'
        try:
            pipeline.process_item( qitem )
        except  DropItem, e:
            _qitem = recrespipeline.process_item( qitem )
            self.assertEquals( 3001, _qitem['res_state'] ) 
        else:
            self.assertTrue(False , "解析不存在的文件包下载资源队列后状态更新失败，目标状态为3001")
        
        # 以错误格式的包做解析测试
        qitem['fileinfo']['file_path'] = os.path.join( get_projectpath(), "tests/tmp")
        qitem['fileinfo']['file_name'] = "fbaafb5dbf0aa3f6d0ebb40709a52cd8a5104241.apk.bk"
        try:
            pipeline.process_item( qitem )
        except DropItem, e:
            _qitem = recrespipeline.process_item( qitem )
            self.assertEquals( 3001, _qitem['res_state'] ) 
        else:
            self.assertTrue(False , "解析格式错误的包后下载资源队列状态更新失败，目标状态为3001")


        qitem['res_state'] = state
        qitem['fileinfo']['file_name'] , qitem['fileinfo']['file_path'] = fname,fpath
        # 恢复初始状态
        cur = pipeline.con.cursor()
        pipeline._update_state( qitem , state )
        pipeline.con.commit()
        cur.close()

class ApkPutStoragePipelineTest(ApkParsePipelineTest):
    """ ApkPutStoragePipeline 入库操作单元测试"""

    name = 'storage'

    fixture_idx = 7

    def setUp(self):
        super(ApkPutStoragePipelineTest, self).setUp()
        self._apkputstoragepipcls =  ApkPutStoragePipeline

    def tearDown(self):
        if hasattr(self,'_rm_pkgversion'):
            self.remove_pkgversion( self._rm_pkgversion )
        super(ApkPutStoragePipelineTest , self).tearDown()

    def test_normal_storage(self):
        __test__ = False
        """ test_normal_storage 正常入库操作，未转移资源文件 """
        item = self.test_normal_apkparse()

        # 3. 入库处理
        apsp = self._apkputstoragepipcls()
        qitem = apsp.process_item( item=item )

        # 4. 校验入库数据的正确性
        rd = self.recover_pkgversion( qitem )
        self.assertEquals( 0 , rd['crawl_state'] )
        self.assertEquals( qitem['fileinfo']['file_name'] , rd['file_name'] )
        self.assertEquals( qitem['fileinfo']['file_size'] , rd['file_size'] )
        self.assertEquals( qitem['fileinfo']['file_md5']  , rd['file_md5'] )
        self.assertEquals( qitem['apkinfo']['pkg_name']  , rd['pkg_name'] )
        self.assertEquals( qitem['apkinfo']['version_code']  , rd['version_code'] )
        self.assertEquals( qitem['apkinfo']['version_name']  , rd['version_name'] )
        self.assertEquals( qitem['rqid']     , rd['rqid'] )
        self.assertEquals( qitem['is_entry'] , rd['is_entry'] )
        self.assertEquals( qitem['csid']     , rd['csid'] )
        self.assertEquals( qitem['cpid'] ,  rd['cpid'] )
        self.assertEquals( qitem['res_id'] ,  rd['res_id'] ) 
        self._rm_pkgversion = rd
        return qitem

    def test_duplicate_storage_version(self):
        """ test_duplicate_storage_version 测试重复添加相同的软件版本(文件MD5唯一键冲突),抛出异常中断 """
        qitem = self.test_normal_storage()
        apsp= self._apkputstoragepipcls()
        self.assertRaises( DropItem , apsp.process_item , item=qitem )

    def test_duplicatefilemd5_diff_resourcequeue(self):
        """ test_duplicatefilemd5_diff_resourcequeue 
            测试入库相同filemd5软件版本(crawl_package_version)
            但下载队列记录(crawl_resource_queue)不同的软件版本(文件MD5唯一键冲突),
            抛出异常中断,更新下载队列记录为相同文件md5
        """
        qitem = self.test_normal_storage()
        apsp= self._apkputstoragepipcls()
        try:
            apsp.process_item( item=qitem )
        except DropItem, e:
            rrp = RecoverResourcePipeline()
            _item = rrp.process_item( item=qitem )
            self.assertEquals( 5001 , _item['res_state'] )
        else:
            self.assertTrue( False , "重复文件md5,未正常中断入库操作" )

    def recover_pkgversion(self, item):
        pipeline = self._apkputstoragepipcls()
        cur = pipeline.con.cursor()
        sql = """ SELECT     cp.cpid  , cp.csid          , cp.pkg_id        , cp.pkg_name , 
                    cpv.res_id      , cpv.version_code , cpv.version_name , 
                    cpv.crawl_state , cpv.file_name    , cpv.apk_md5      , 
                    cpv.file_size   , cpv.rqid         , cpv.is_entry
                FROM crawl_package_version AS cpv 
                INNER JOIN crawl_package AS cp ON ( cp.cpid=cpv.cpid )
                WHERE cpv.res_id=%s
                LIMIT 1 """
        rd = None
        if cur.execute( sql , ( item['res_id'], ) ):
            r  = cur.fetchone()
            rd = {
                    'cpid'         : r[0 ] , 
                    'csid'         : r[1 ] , 
                    'pkg_id'       : r[2 ] , 
                    'pkg_name'     : r[3 ] , 
                    'res_id'       : r[4 ] , 
                    'version_code' : r[5 ] , 
                    'version_name' : r[6 ] , 
                    'crawl_state'  : r[7 ] , 
                    'file_name'    : r[8 ] , 
                    'file_md5'     : r[9 ] , 
                    'file_size'    : r[10] , 
                    'rqid'         : r[11] , 
                    'is_entry'     : r[12] , 
                }

        cur.close()
        return rd

    def remove_pkgversion(self, rd):
        pipeline = self._apkputstoragepipcls()
        cur = pipeline.con.cursor()
        sql1 = """ DELETE FROM crawl_package_version WHERE crawl_package_version.cpid=%s LIMIT 100;"""
        sql2 = """ DELETE FROM crawl_package WHERE crawl_package.cpid=%s LIMIT 1; """
        cur.execute( sql1 , ( rd['cpid'],) )
        cur.execute( sql2 , ( rd['cpid'],) )
        pipeline.con.commit()
        cur.close()

class ApkFileArchivePipelineTest(ApkPutStoragePipelineTest):
    """ apk文件归档测试 """

    name = 'archive'

    fixture_idx = 8

    def setUp(self):
        super(ApkFileArchivePipelineTest , self).setUp()
        self._apkfilearchpipcls= ApkFileArchivePipeline

    def tearDown(self):
        if hasattr(self,'_rollback_resitem' ):
            self.rollback_resitem( self._rollback_resitem[0] ,
                                    self._rollback_resitem[1] )
        super(ApkFileArchivePipelineTest, self).tearDown()

    def test_normal_archive(self):
        """ test_normal_archive 正常移动文件"""
        qitem = self.test_normal_storage()
        org_item = copy.deepcopy(qitem)
        pipeline = self._apkfilearchpipcls()
        qitem = pipeline.process_item( item=qitem )
        self._rollback_resitem = ( org_item , qitem )

        cpv = self.recover_pkgversion( qitem )
        self.assertEquals( cpv['crawl_state'] , 1 )
        rrp = RecoverResourcePipeline()
        _item = rrp.process_item( item=qitem )

        self.assertEquals( _item['res_state'] , 1)
        self.assertEquals( cpv['file_name'] , _item['fileinfo']['file_name'] )
        self.assertEquals( _item['fileinfo']['file_path'] , 
                           os.path.join( settings.APK_RESOURCE_REL_DIR , 
                                          str(int(math.floor(cpv['res_id']/ pipeline.partition_limit))) ) 
                        )

    def test_exception_apkfilearching(self):
        """ test_exception_apkfilearching 转移文件时异常中断测试 """
        self.fixture_idx = 9
        qitem = self.test_normal_storage()
        org_item = copy.deepcopy(qitem)
        pipeline = self._apkfilearchpipcls()

        qitem['fileinfo']['file_name'] = 'file_not_exists.apk';
        self.assertRaises( DropItem , pipeline.process_item , item=qitem )
        self._rollback_resitem = ( org_item , qitem )

    def rollback_resitem(self, org, nitem ):
        """rollback_resitem 回滚资源状态，以及恢复apk文件至临时文件"""
        pipeline = self._apkfilearchpipcls()
        cur=pipeline.con.cursor()
        sql = """UPDATE crawl_resource_queue 
                SET res_state=%s,
                file_name=%s,
                file_path=%s
                WHERE rqid=%s
                LIMIT 1"""
        cur.execute( sql , ( org['res_state'],
                             org['fileinfo']['file_name'],
                             org['fileinfo']['file_path'],
                             org['rqid'] ) )
        src = os.path.join( pipeline._gen_apkres_abs_path(nitem) , 
                            nitem['fileinfo']['file_name'] )
        #dst = os.path.join( org['fileinfo']['file_path'] ,
                            #org['fileinfo']['file_name'] )
        try:
            os.remove(src)
            #os.rename( src , dst )
        except Exception, e:
            pass
        pipeline.con.commit()
        cur.close()

if __name__ == '__main__':
    unittest.main()
