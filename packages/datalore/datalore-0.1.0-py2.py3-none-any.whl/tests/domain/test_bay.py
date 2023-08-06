import uuid
from datalore.domain.bay import Bay


def test_bay_model_init():
    code = uuid.uuid4()
    bay = Bay(code, size=200, price=10,
                          longitude='-0.09998975',
                          latitude='51.75436293')
    assert bay.code == code
    assert bay.size == 200
    assert bay.price == 10
    assert bay.longitude == -0.09998975
    assert bay.latitude == 51.75436293


def test_bay_model_from_dict():
    code = uuid.uuid4()
    bay = Bay.from_dict(
        {
            'code': code,
            'size': 200,
            'price': 10,
            'longitude': '-0.09998975',
            'latitude': '51.75436293'
        }
    )
    assert bay.code == code
    assert bay.size == 200
    assert bay.price == 10
    assert bay.longitude == -0.09998975
    assert bay.latitude == 51.75436293
