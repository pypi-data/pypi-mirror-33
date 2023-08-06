import uuid
from astronaut.domain.space import Space


def test_space_model_init():
    code = uuid.uuid4()
    space = Space(code, size=200, price=10,
                          longitude='-0.09998975',
                          latitude='51.75436293')
    assert space.code == code
    assert space.size == 200
    assert space.price == 10
    assert space.longitude == -0.09998975
    assert space.latitude == 51.75436293


def test_space_model_from_dict():
    code = uuid.uuid4()
    space = Space.from_dict(
        {
            'code': code,
            'size': 200,
            'price': 10,
            'longitude': '-0.09998975',
            'latitude': '51.75436293'
        }
    )
    assert space.code == code
    assert space.size == 200
    assert space.price == 10
    assert space.longitude == -0.09998975
    assert space.latitude == 51.75436293
