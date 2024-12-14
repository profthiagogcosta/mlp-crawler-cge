import os

import pandas as pd

from src.connections.mongo_db_handler import StorageData
from src.logger import Logger
from src.scrapping.utils import (
    clean_referencia,
    get_all_days,
    get_desc_flood_point,
    get_df_from_model_list,
    get_flood_descs,
    get_flood_list,
    get_flood_points,
    get_google_results,
    get_preprocessed_date,
    get_status_flood_point,
    replace_address_terms,
    tem_numeros,
)
from src.templates.crawler_base import CrawlerBase
from src.templates.dataclass import RawFlood

# --------------------------
# -------DESC: Logger-------
logger = Logger().get_logger()
# --------------------------


# ConcreteProduct
class CrawlerFloods(CrawlerBase):
    def _configurar(
        self,
        *,
        data_inf: str,
        data_sup: str,
        scrapping_date: str,
        api_code: str,
        scrapping_level: str,
    ):
        self.data_inf = data_inf
        self.data_sup = data_sup
        self.scrapping_date = scrapping_date
        self.api_code = api_code
        self.scrapping_level = scrapping_level

    def _captar(self):
        raw_floods = []

        # DESC: Get all days throught some days
        all_days = get_all_days(data_inf=self.data_inf, data_sup=self.data_sup)

        for day in all_days:
            # DESC: Preprocessed date
            preprocessed_date = get_preprocessed_date(day=day)

            # DESC: Get the flood list of the São Paulo city
            flood_list = get_flood_list(day=preprocessed_date)

            for flood_ocurrence in flood_list:
                # DESC: Get the flood point
                flood_points = get_flood_points(flood_ocurrence=flood_ocurrence)

                for flood_point in flood_points:
                    # DESC: Get the status of the flood point
                    status = get_status_flood_point(flood_point=flood_point)

                    # DESC: Get the descriptions of the flood points
                    desc_references = get_flood_descs(flood_point=flood_point)

                    # DESC: Get each description
                    flood_references = get_desc_flood_point(
                        desc_references=desc_references
                    )

                    # DESC: Create a raw flood data
                    raw_flood = RawFlood(
                        day=preprocessed_date,
                        status=status,
                        periodo=flood_references['periodo'],
                        sentido=flood_references['sentido'],
                        endereco=flood_references['endereco'],
                        referencia=flood_references['referencia'],
                    )

                    logger.info('-' * 50)
                    logger.info(f'{raw_flood}')
                    logger.info('-' * 50)

                    # DESC: Append the list of the RawFloods
                    raw_floods.append(raw_flood)

        self.df = get_df_from_model_list(models=raw_floods)

    def _preprocessar(self):
        self.df = self.df.reset_index(drop=True)

        logger.info(f'{self.df}')
        logger.info(f'{self.df.columns}')
        logger.info(f"{self.df['periodo']}")

        # ----------Flood Type----------
        self.df['tipo_alagamento'] = self.df.apply(
            lambda x: 1 if x.status == 'transitavel' else 0, axis=1
        )

        # ----------Período de Alagamento----------
        self.df[['periodo_inicial', 'periodo_final']] = self.df['periodo'].str.split(
            'A', expand=True
        )
        self.df['periodo_inicial'] = self.df['periodo_inicial'].str.replace(
            'DE ', '', regex=False
        )
        self.df['periodo_final'] = self.df['periodo_final'].str.replace(
            ' ', '', regex=False
        )

        # ----------PREPROCESS REFERENCIA----------
        # Create a set of replacements for 'referencia'
        replace_dict = {
            'ALTURA DO NÚMERO': '',
            'ALTURA DO N.': '',
            'ALTURA DO Nº': '',
            'ALTURA DO NUMERO': '',
            'ALTURA DO NUMERO.': '',
            'ALT. Nº': '',
            'ALT Nº': '',
            'ALT. NÚMERO': '',
            'ALT. DO N.': '',
            'ALT. DO Nº': '',
            'ALT. NR': '',
            'ALT. N.': '',
            'ALT N': '',
            'ALT ': '',
            'ALTURA': '',
            'Nº': '',
            'ACESSO': '',
            'TODA EXTENSÃO': '',
            '<': '',
            '1,5KM ANTES': '',
            'SOB': '',
            'PROX.': '',
            'INICIO DO MESMO': '',
            'NO MEMSO': '',
            'NO MESMO': '',
            'MEIO DO MESMO': '',
            'DO No': '',
            'No ': '',
            'ENTRE ': '',
        }

        # Create a regex pattern for auxiliary numbers
        aux_num = list(range(1, 1000))
        aux_num_pattern = '|'.join(
            [
                f'DESEMBOQUE {j} M ANTES|{j}M ANTES DA|{j}M ANTES DO DESEMBOQUE|E {j} M ANTES DA MESMA|{j} METROS ANTES DA|ATÉ {j}M ANTES|ATÉ {j}M APÓS|ATÉ {j}m APÓS|ATÉ {j}m ANTES|{j}M ANTES|{j}M APÓS|{j} M ANTES|{j} M APÓS|{j}m APÓS|{j}m ANTES|{j}. ANTES|{j}. APÓS'
                for j in aux_num
            ]
        )

        # Apply string replacements for 'referencia_modify' efficiently using vectorized operations
        self.df['referencia_modify'] = self.df['referencia'].apply(
            lambda x: clean_referencia(x, replace_dict, aux_num_pattern)
        )

        address_replacements = {
            'AV.': 'AVENIDA',
            'PTE.': 'PONTE',
            'PT.': 'PONTE',
            'R.': 'RUA',
            'PC.': 'PRAÇA',
            'TN.': 'TUNEL',
            'JORN.': 'JORNALISTA',
            'PROF.': 'PROFESSOR',
            'ES.': 'ESTRADA',
            'LG.': 'LARGO',
            'VD.': 'VIADUTO',
            'VELHA FEPASA': 'COMUNIDADE HUNGARA',
        }

        self.df['endereco_modify'] = self.df['endereco'].apply(
            lambda x: replace_address_terms(x, address_replacements)
        )
        self.df['referencia_modify'] = self.df['referencia_modify'].apply(
            lambda x: replace_address_terms(x, address_replacements)
        )

    def _transformar(self):
        data_list = []

        for i in range(len(self.df)):
            try:
                # Collect necessary columns upfront to avoid repeating indexing
                referencia_modify = self.df.loc[i, 'referencia_modify']
                endereco_modify = self.df.loc[i, 'endereco_modify']
                endereco = ''

                # Construct the full address
                if tem_numeros(referencia_modify):
                    endereco = (
                        f'{endereco_modify}, {referencia_modify}, São Paulo, Brasil'
                    )
                else:
                    endereco = (
                        f'{endereco_modify} COM {referencia_modify}, São Paulo, Brasil'
                    )

                # Get Google results
                resultado_vec = get_google_results(
                    address=endereco, api_key=self.api_code
                )

                # Prepare the row as a dictionary
                row = {
                    'data': self.df.loc[i, 'day'],
                    'periodo': self.df.loc[i, 'periodo'],
                    'endereco': self.df.loc[i, 'endereco'],
                    'referencia': self.df.loc[i, 'referencia'],
                    'latitude': resultado_vec[1],
                    'longitude': resultado_vec[2],
                    'tipo_alagamento': self.df.loc[i, 'tipo_alagamento'],
                    'status_alagamento': self.df.loc[i, 'status'],
                    'periodo_inicial': self.df.loc[i, 'periodo_inicial'],
                    'periodo_final': self.df.loc[i, 'periodo_final'],
                    'endereco_CERTO': endereco_modify,
                    'referencia_CERTA': referencia_modify,
                    'endereco_formatado': resultado_vec[0],
                    'acuracia': resultado_vec[3],
                    'google_place_id': resultado_vec[4],
                    'tipo': resultado_vec[5],
                    'numero_resultados': resultado_vec[6],
                    'status_geocoding': resultado_vec[7],
                }

                # Append the row to the data list
                data_list.append(row)

            except ValueError as e:
                print('Erro:', e)

        # Converte a lista para colunas
        colunas = [
            'data',
            'periodo',
            'endereco',
            'referencia',
            'tipo_alagamento',
            'tipo',
            'periodo_inicial',
            'periodo_final',
            'latitude',
            'longitude',
            'referencia_CERTA',
            'endereco_CERTO',
            'endereco_formatado',
            'acuracia',
            'google_place_id',
            'tipo',
            'numero_resultados',
            'status',
        ]

        self.df = pd.DataFrame(data_list, columns=colunas)

    def _persistir(self):
        try:
            storage_data = StorageData()
            client = storage_data.connection('localhost', '27017', 'root', 'password')
            storage_data.insert_all_floods(client, self.df, self.scrapping_level)

        except Exception:
            raise

        return None

    def executar(
        self,
        *,
        data_inf: str,
        data_sup: str,
        scrapping_date: str,
        api_code: str,
        scrapping_level: str,
    ):
        scrapping_level = os.environ.get('SCRAPPING_LEVEL', 'bronze')

        self._configurar(
            data_inf=data_inf,
            data_sup=data_sup,
            scrapping_date=scrapping_date,
            api_code=api_code,
            scrapping_level=scrapping_level,
        )

        self._captar()

        if scrapping_level == 'bronze':
            self._persistir()
        else:
            self._preprocessar()
            self._transformar()
            self._persistir()
