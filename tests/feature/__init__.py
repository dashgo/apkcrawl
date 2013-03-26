# -*- encoding=utf-8
import sys
import os
from twisted.trial import unittest
import scrapy.spider
from scrapy.interfaces import ISpiderManager
from scrapy.spidermanager import SpiderManager
from scrapy.http import Request

import apkcrawl.settings
from apkcrawl.tests import get_projectpath , get_crawler

class SpiderManagerTest(object):

    def setUp(self):
        orig_spiders_dir = os.path.join(get_projectpath() , 'tests', 'feature', 'searchspiders')
        sys.path.append(orig_spiders_dir)
        self.spiderman = SpiderManager(['feature.searchspiders'])

    def tearDown(self):
        del self.spiderman
        sys.path.remove(self.tmpdir)
