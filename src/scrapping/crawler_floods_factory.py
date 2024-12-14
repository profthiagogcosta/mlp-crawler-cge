from src.scrapping.crawler_floods import CrawlerFloods
from src.templates.crawler_base import CrawlerBase
from src.templates.crawler_factory import CrawlerFactory


# ConcreteCreator
# DESC: É importante retornar o CrawlerBase, pois
# o construtor deve ser generalista...
class CrawlerFloodsFactory(CrawlerFactory):
    def createCrawler(self) -> CrawlerBase:
        return CrawlerFloods()
