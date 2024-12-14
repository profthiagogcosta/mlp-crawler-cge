from src.templates.singleton import Singleton


# WebScrapper
class CrawlerBase(Singleton):
    def _configurar(self):
        raise NotImplementedError

    def _captar(self):
        raise NotImplementedError

    def _preprocessar(self):
        raise NotImplementedError

    def _transformar(self):
        raise NotImplementedError

    def _persistir(self):
        raise NotImplementedError

    def executar(self):
        raise NotImplementedError
