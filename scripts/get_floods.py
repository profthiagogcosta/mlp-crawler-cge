import os
from datetime import datetime

from src.logger import Logger
from src.scrapping.crawler_floods_factory import CrawlerFloodsFactory

# --------------------------
# -----DESC: Logger-----
logger = Logger().get_logger()
# --------------------------


def execute_crawler():
    scrapping_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    # -----OBTENCAO DO RANGE DE DATAS-----
    data_inf = os.environ.get('DATA_INFERIOR', '')
    data_sup = os.environ.get('DATA_SUPERIOR', '')

    logger.info('-' * 50)
    logger.info(f'data_inf: {data_inf}')
    logger.info(f'data_sup: {data_sup}')
    logger.info('-' * 50)
    # ------------------------------

    # -----Crawler Flooding-----
    crawler_factory = CrawlerFloodsFactory()

    floods_crawler = crawler_factory.createCrawler()

    floods_crawler.executar(
        data_inf=data_inf,
        data_sup=data_sup,
        scrapping_date=scrapping_date,
        api_code=os.environ.get('API_CODE', ''),
        scrapping_level=os.environ.get('SCRAPPING_LEVEL', 'bronze'),
    )
    # ------------------------------


def main():
    # ------------------------------
    # DESC: Execute the crawler
    execute_crawler()
    # ------------------------------


if __name__ == '__main__':
    main()
