import datetime

from src.scrapping.utils import get_preprocessed_date, get_scrapping_date
from src.templates.dataclass import RawFlood


def test_raw_flood(raw_flood_data):
    raw_flood = RawFlood(**raw_flood_data)

    assert raw_flood.day == '28/10/2019'
    assert raw_flood.status == 'transitavel'
    assert raw_flood.periodo == 'DE 04:05 A 10:08'
    assert raw_flood.endereco == 'R. MIGUEL YUNES'
    assert raw_flood.sentido == 'SENTIDO: INTERLAGOS/MARGINAL'
    assert raw_flood.referencia == 'AV INTERLAGOS'


def test_scrapping_date():
    day = datetime.datetime(2024, 12, 21)

    assert '21/12/2024' == get_preprocessed_date(day=day)


def test_get_scrapping_date():
    today = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    result = get_scrapping_date()

    assert result == today
