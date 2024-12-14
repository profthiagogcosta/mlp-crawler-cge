import datetime
from typing import List

import bs4
import pandas as pd
import requests
from requests import get as get_requests

from src.logger import Logger

# --------------------------
# -----DESC: Logger-----
logger = Logger().get_logger()
# --------------------------


def get_all_days(*, data_inf: str, data_sup: str) -> List[str]:
    try:
        start_date = pd.to_datetime(data_inf, format='%d/%m/%Y')
        end_date = pd.to_datetime(data_sup, format='%d/%m/%Y')

        # Use pandas date_range to generate all days between start_date and end_date
        all_days = pd.date_range(start=start_date, end=end_date, freq='D')

        return all_days

    except Exception as e:
        logger.info('-' * 50)
        logger.info(f'Error: {e}')
        logger.info('-' * 50)


def get_preprocessed_date(*, day):
    return day.strftime('%d/%m/%Y')


def get_scrapping_date() -> str:
    return datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')


def get_flood_list(*, day: str):
    url_base = (
        'https://www.cgesp.org/v3/alagamentos.jsp?dataBusca='
        + day
        + '+&enviaBusca=Buscar'
    )

    logger.info('-' * 50)
    logger.info(f'{url_base}')
    logger.info('-' * 50)

    response = get_requests(url_base)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')

    floods_list = soup.find_all(class_='tb-pontos-de-alagamentos')

    return floods_list


def get_status_flood_point(*, flood_point: bs4.element.Tag):
    if (flood_point.find(class_='ativo-transitavel')) or (
        flood_point.find(class_='inativo-transitavel')
    ):
        status = 'transitavel'
    elif (flood_point.find(class_='ativo-intransitavel')) or (
        flood_point.find(class_='inativo-intransitavel')
    ):
        status = 'intransitavel'
    else:
        status = None

    return status


def get_flood_points(*, flood_ocurrence: bs4.element.Tag):
    return flood_ocurrence.find_all(class_='ponto-de-alagamento')


def get_flood_descs(*, flood_point: bs4.element.Tag):
    return flood_point.find_all(class_='arial-descr-alag')


def get_desc_flood_point(*, desc_references: bs4.element.ResultSet):
    flood_descs = [
        desc_reference.find_all(text=True) for desc_reference in desc_references
    ]

    return {
        'periodo': flood_descs[0][0].upper(),
        'endereco': flood_descs[0][1].upper(),
        'sentido': flood_descs[1][0].upper(),
        'referencia': flood_descs[1][1].upper(),
    }


def get_df_from_model_list(*, models: List):
    return pd.DataFrame([model.model_dump() for model in models])


def get_google_results(*, address, api_key=None):
    # Set up your Geocoding url
    geocode_url = 'https://maps.googleapis.com/maps/api/geocode/json?address={}'.format(
        address
    )

    if api_key:
        geocode_url = geocode_url + '&key={}'.format(api_key)

    # Ping google for the reuslts:
    results = requests.get(geocode_url)

    if results.status_code != 200:
        raise ValueError('Error in API response')

    results = results.json()

    result_vector = []

    if len(results['results']) == 0:
        result_vector.extend([0] * 8)
    else:
        answer = results['results'][0]

        result_vector.extend(
            [
                answer.get('formatted_address'),
                answer.get('geometry', {}).get('location', {}).get('lat'),
                answer.get('geometry', {}).get('location', {}).get('lng'),
                answer.get('geometry', {}).get('location_type'),
                answer.get('types'),
                address,
                len(results['results']),
                results.get('status'),
            ]
        )

    return result_vector


def tem_numeros(string):
    return any(char.isdigit() for char in string)


def replace_address_terms(address, replace_dict):
    for old, new in replace_dict.items():
        address = address.replace(old, new)
    return address


def clean_referencia(referencia, replace_dict, aux_num_pattern):
    # Perform the replace operations for 'referencia' field
    for old, new in replace_dict.items():
        referencia = referencia.replace(old, new)

    # Apply the auxiliary number pattern
    referencia = pd.Series(referencia).replace(aux_num_pattern, '', regex=True).iloc[0]

    # Clean the final parts of the string after the dash and colon
    referencia = referencia.split('-')[0].split(':')[0]

    return referencia
