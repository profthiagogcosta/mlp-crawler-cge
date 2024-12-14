import pytest


@pytest.fixture
def raw_flood_data():
    return {
        'day': '28/10/2019',
        'status': 'transitavel',
        'periodo': 'DE 04:05 A 10:08',
        'endereco': 'R. MIGUEL YUNES',
        'sentido': 'SENTIDO: INTERLAGOS/MARGINAL',
        'referencia': 'AV INTERLAGOS',
    }
