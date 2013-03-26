# -*- encoding=utf-8
import sys
from os.path import dirname , realpath
project_dir = dirname(dirname(realpath(__file__)))
sys.path.append( project_dir )

def get_crawler(settings_dict=None):
    """Return an unconfigured Crawler object. If settings_dict is given, it
    will be used as the settings present in the settings module of the
    CrawlerSettings.
    """
    from scrapy.crawler import Crawler
    from scrapy.settings import CrawlerSettings

    class SettingsModuleMock(object):
        pass
    settings_module = SettingsModuleMock()
    if settings_dict:
        for k, v in settings_dict.items():
            setattr(settings_module, k, v)
    settings = CrawlerSettings(settings_module)
    return Crawler(settings)

def get_projectpath():
    return project_dir

def get_pythonpath():
    """Return a PYTHONPATH suitable to use in processes so that they find this
    installation of Scrapy"""
    sep = ';' if sys.platform == 'win32' else ':'
    scrapy_path = __import__('scrapy').__path__[0]
    return os.path.dirname(scrapy_path) + sep + os.environ.get('PYTHONPATH', '')
