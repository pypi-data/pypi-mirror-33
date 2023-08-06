import json


class BayEncoder(json.JSONEncoder):

    def default(self, o):
        try:
            to_serialize = {
                'code': o.code,
                'size': o.size,
                'price': o.price,
                "latitude": o.latitude,
                "longitude": o.longitude,
            }
            return to_serialize
        except AttributeError:
            return super().default(o)
