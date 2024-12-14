import pandas as pd
from pymongo import MongoClient

from src.logger import Logger
from src.templates.singleton import Singleton

# --------------------------
# -------DESC: Logger-------
logger = Logger().get_logger()
# --------------------------


class StorageData(Singleton):
    def connection(self, host: str, port: str, user: str, password: str) -> MongoClient:
        try:
            client = MongoClient(f'mongodb://{user}:{password}@{host}:{port}/')

            logger.info('-' * 50)
            logger.info('Connection Successful!')
            logger.info('-' * 50)
            return client
        except Exception as e:
            logger.info('-' * 50)
            logger.info('Connection Error!')
            logger.info('-' * 50)
            raise e

    def insert_all_floods(
        self, client: MongoClient, df: pd.DataFrame, scrapping_level: str = 'bronze'
    ) -> None:
        try:
            floods_db = client['floods_db']
            floods_collection = floods_db['floods_collection_' + scrapping_level]

            list_df = df.to_dict('records')

            floods_collection.insert_many(list_df)

            logger.info('-' * 50)
            logger.info('Insertion Successful!')
            logger.info('-' * 50)

            print('Insertion Successful!')

        except Exception as e:
            print('Insertion Error!')
            raise e
