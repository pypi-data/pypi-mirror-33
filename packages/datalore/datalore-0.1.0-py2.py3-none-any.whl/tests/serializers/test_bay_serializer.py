import json

from datalore.serializers import bay_serializer as srs
from datalore.domain.bay import Bay


def test_serialize_domain_bay():
    room = Bay('f853578c-fc0f-4e65-81b8-566c5dffa35a',
                     size=200,
                     price=10,
                     longitude='-0.09998975',
                     latitude='51.75436293')

    expected_json = """
{
"code": "f853578c-fc0f-4e65-81b8-566c5dffa35a",
"size": 200,
"price": 10,
"longitude": -0.09998975,
"latitude": 51.75436293
}
"""

    assert json.loads(json.dumps(room, cls=srs.BayEncoder)) \
        == json.loads(expected_json)
