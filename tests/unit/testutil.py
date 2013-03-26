# -*- encoding=utf-8
'''
File: testutil.py
Author: Hunag Ronghua <huangronghua@ndoo.net>
Date: 2013-01-08 16:48
Description: 辅助工具测试
'''
import sys
import os
from apkcrawl.tests import get_projectpath

cur_file = os.path.realpath(__file__)
cur_dir = os.path.dirname(os.path.dirname(cur_file))
#crawl_path = os.path.dirname(os.path.dirname( cur_dir ))
#sys.path.append( crawl_path )
import unittest2 as unittest
from apkcrawl import settings
from apkcrawl.utils import random_proxy , proxy_lists

from apkcrawl.utils import ApkFileParser, ApkDumpFailError

projectpath = get_projectpath()
class TestSetting(unittest.TestCase): # pargma: no cover
    """ 项目配置测试 TestSettingBuild"""

    settings = settings

    def test_proxy_lists(self):
        """test_proxy_lists 测试代理列表"""
        proxies = proxy_lists( settings.PROXY_LIST_FILE )
        self.assertTrue( len(proxies) != 0)
        #print( random_proxy( proxies ) )

class TestApkParse(unittest.TestCase):
    """ TestApkParse 测试解析apk包信息"""

    def setUp(self):
        self.parser = ApkFileParser()

    def test_parseinfo(self):
        """test_parseinfo 正常解析apk文件信息"""
        fp = os.path.join( cur_dir , "tmp" , "8845970f239f7fbd1c2c6f81861e92a81a43b32e.apk" )
        info = self.parser.parse( fp )
        self.assertIn("pkg_name",info)
        self.assertIsInstance(info.get("pkg_name"), str)
        self.assertIn("version_code",info)
        self.assertIsInstance(info.get("version_code"), int)
        self.assertIn("version_name",info)
        self.assertIsInstance(info.get("version_name"), str)
        self.assertIn("file_size",info)
        self.assertIsInstance(info.get("file_size"), int)
        self.assertIn("file_md5" ,info)
        self.assertIsInstance(info.get("file_md5"), str)
        self.assertEquals(len(info.get("file_md5")), 32)
        self.assertIn("file_name",info)
        self.assertIsInstance(info.get("file_name"), str)

    def test_parseerror(self):
        """test_parseerror 找不到文件、解析包错误测试"""
        import time
        fp = os.path.join( projectpath, "tests/tmp" , str(time.time())+".apk" )
        # no such file or directory
        self.assertRaises(OSError, self.parser.parse , fp ) 

        # apk dump failed error
        fp = os.path.join( projectpath, "tests/tmp" ,"fbaafb5dbf0aa3f6d0ebb40709a52cd8a5104241.apk.bk" )
        self.assertRaises( ApkDumpFailError , self.parser.parse , fp )

if __name__ == '__main__':
    unittest.main()
