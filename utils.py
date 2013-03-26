# -*- encoding=utf-8

'''
File: utils.py
Author: Hunag Ronghua <huangronghua@ndoo.net>
Date: 2013-01-10 00:54
Description: 辅助工具集
'''
import re
import os
import sh
from scrapy import log
from scrapy.utils.misc import md5sum
import apkcrawl.settings

class ApkDumpFailError(Exception):
    """ 
    apk文件解析错误
    """
    pass

class ApkFileParser(object):
    """
    ApkFileParser apk文件解析器
    软件数据入库前 apk文件信息获取
    """

    def __init__(self):
        self.aapt = sh.Command( apkcrawl.settings.AAPT_CMD )
        super(ApkFileParser, self).__init__()

    ##
    # @brief 
    #
    # @param str fname
    #
    # @return dict
    def parse(self, fname):
        """
        解析fname文件路径所指apk,获取文件信息
        返回数据结构:
        {
            "file_name"    :  "8845970f239f7fbd1c2c6f81861e92a81a43b32e.apk", 
            "file_md5"     :  "3bb744c851097281aa64180a8c9a1c3b", 
            "file_size"    :  946163, 
            "pkg_name"     :  'com.book_iuqwer', 
            "version_cdoe" :  1, 
            "version_name" :  '1.0'
        }
        若找不到文件，将抛出OSError找不到文件或目录
        若找解析apk信息错误，即apk文件不完整，将抛出ApkDumpFailError
        """
        info = self.fileparse( fname )
        info.update(self.apkparse( fname ))
        return info
    
    def apkparse(self, fname):
        """
        解析、获取apk信息
        返回数据结构:
        {
            "pkg_name"     :  'com.book_iuqwer', 
            "version_cdoe" :  1, 
            "version_name" :  '1.0'
        }
        若找不到文件，将抛出OSError找不到文件或目录
        若找解析apk信息错误，即apk文件不完整，将抛出ApkDumpFailError
        """
        info = {}
        try:
            result = str(sh.head(self.aapt("dump" , "badging" , fname ), n=1))
            pattern = re.compile(r"package: name='(.+)' versionCode='(\d*)' versionName='(.*)'")
            mth                  = re.match( pattern , result )
            info['pkg_name']     = mth.group(1)
            try:
                info['version_code'] = int(mth.group(2))
            except Exception, e:
                info['version_code'] = 0
            info['version_name'] = mth.group(3)
            return info
        except sh.ErrorReturnCode, e:
            raise ApkDumpFailError(e.message)

    def fileparse(self, fname ):
        """ fileparse
        获取文件信息
        返回数据结构:
        {
            "file_name"    :  "8845970f239f7fbd1c2c6f81861e92a81a43b32e.apk", 
            "file_md5"     :  "3bb744c851097281aa64180a8c9a1c3b", 
            "file_size"    :  946163, 
            "file_path"    :  '/tmp', 
        }
        """
        info = {}
        info['file_path'] = os.path.dirname(fname)
        info['file_name'] = os.path.basename(fname)
        info['file_size'] = os.path.getsize(fname)
        with open(fname,'r') as fh:
            info['file_md5'] = md5sum(fh)

        return info

def search_keys( fpath ):
    """
     @brief 生成器，搜索软件关键字

     @param str fpath 关键字列表

     @return unicode
    """
    import fileinput
    for l in fileinput.input( fpath):
        yield unicode(l.rstrip("\n") , 'utf-8')

def proxy_lists( fpath ):
    """
      @brief 获取并格式化代理列表
     
      @param str fpath
     
      @return list<( protocal , url)>
    """
    fd = open( fpath,'r')
    data = fd.readlines()
    fd.close()
    rtns = []
    for item in data:
        arr      = item.split(',')
        protocal = arr[1].lower().rstrip("\n")
        rtns.append(  ( protocal , '%s://%s' % ( protocal,arr[0]) , ) )
    return rtns

def random_proxy( proxies ):
    """
     @brief 从代理列表随机获取一个代理
    
     @param list<( protocal , url)> proxies
    
     @return str 代理url
    """
    import random
    length = len(proxies)
    index  = random.randint(0, length -1)
    return proxies[index]

class Null(object):
    """The Null Object Pattern for do Nothing"""
    def __new__(cls, *args, **kwargs):
        if '_inst' not in vars(cls):
            cls._inst = type.__new__(cls, *args, **kwargs )
        return cls._inst
    def __init__(self): pass
    def __class(self, *args, **kwargs): return self
    def __repr__(self): return "Null()"
    def __nonzero__(self): return False
    def __getattr__(self, name ): return self
    def __setattr__(self, name , value): return self
    def __delattr__(self, name): return self

class SeqNull(Null):
    """SeqNull do Nothing"""
    def __len__(self): return 0
    def __iter__(self): return iter( () )
    def __getiterm__(self, i ): return self
    def __setiterm__(self, i , v ) :return self
