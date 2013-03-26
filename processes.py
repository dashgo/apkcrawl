# -*- encoding=utf-8
from apkcrawl.pipelines import *
import threading, time, datetime
from scrapy.exceptions import DropItem
import Queue

NULL = None
AfterSigninDownloadStorePipelines = [
        RecoverResourcePipeline() , 
        LocalDownloadPipeline()   , 
        FileParsePipeline()       , 
        SignoutPipeline()         , 
        ApkParsePipeline()        , 
        ApkPutStoragePipeline()   , 
        ApkFileArchivePipeline()  , 
    ]

Counter = 0
ApkdwQueue = Queue.Queue()
class AfterSigninDownloadStoreTask(threading.Thread):
    """AfterSigninDownloadStoreTask"""

    _queue = None

    _count = None

    def __init__(self, queue):
        super(AfterSigninDownloadStoreTask, self).__init__()
        global counter
        counter = Counter + 1
        self._count = counter
        self._queue = queue

    def run(self):
        """run"""
        global AfterSigninDownloadStorePipelines
        while True:
            item = self._queue.get()
            try:
                for p in AfterSigninDownloadStorePipelines :
                    item = p.process_item( item , spider=NULL ) 
                print item
            except DropItem, e:
                pass
            finally:
                self._queue.task_done()

def RunAfterSigninDownloadStoreProcess( items, thread_count=2 ):
    """RunAfterSigninDownloadStoreProcess 多线程运行签入后的下载、入库流程"""

    for item in items:
        ApkdwQueue.put(item)

    for i in xrange(thread_count):
        t = AfterSigninDownloadStoreTask( ApkdwQueue )
        t.setDaemon(True)
        t.start()

    ApkdwQueue.join()
