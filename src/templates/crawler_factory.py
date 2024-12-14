from src.templates.crawler_base import CrawlerBase
from src.templates.singleton import Singleton


# Creator
class CrawlerFactory(Singleton):
    def createCrawler(self) -> CrawlerBase:
        raise NotImplementedError
