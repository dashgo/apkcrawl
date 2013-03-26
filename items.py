# -*- encoding=utf-8
# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field
import hashlib
import time

def gen_identifier( item):
    if item['is_entry'] is True or item['site'] != 'www.anzhi.com':
        s = hashlib.sha1( item['entry_url'] ).hexdigest()
    else:
        s= hashlib.sha1( item['entry_url'] + "&" + str(time.time()) ).hexdigest()
    return s

def gen_parent_identifier( item):
    if item['is_entry'] is True:
        return ""
    return hashlib.sha1( item['referer_url'] ).hexdigest()

class ApkcrawlItem(Item):
    """ ApkcrawlItem 爬取apk数据结构 """
    ##
    # @brief 下载队列的唯一ID crawl_resource_queue.rqid
    rqid         = Field()
    ##
    # @brief crawl_resource_queue.identifier
    identifier   = Field()
    ##
    # @brief for foreign key crawl_resource_queue.csid references crawl_site.csid
    site         = Field()
    ##
    # @brief is_entry
    is_entry     = Field()
    ##
    # @brief 入口地址
    entry_url    = Field()
    ##
    # @brief 下载地址
    download_url = Field()
    ##
    # @brief 入口页面的引用地址
    referer_url  = Field()
    fileinfo     = Field()
    apkinfo      = Field()
    ##
    # @brief 引用地址的identifier, 旨在索引上级引用地址记录，记为crawl_resource_queue.parent_rqid
    parent_identifier   = Field()

class ApkQueueItem(ApkcrawlItem):
    """ ApkQueueItem 资源下载队列的apk数据结构"""
    ##
    # @brief crawl_site.csid
    csid        = Field()
    ##
    # @brief crawl_package_version.cpid
    cpid        = Field()
    ##
    # @brief crawl_package_version.res_id
    res_id      = Field()
    ##
    # @brief crawl_resource_queue.rqid
    rqid        = Field()
    ##
    # @brief crawl_resource_queue.parent_rqid
    parent_rqid = Field()
    ##
    # @brief crawl_resource_queue.res_state
    res_state   = Field()
    ##
    # @brief crawl_resource_queue.create_dt
    create_dt   = Field()
    ##
    # @brief crawl_resource_queue.update_dt
    update_dt   = Field()
