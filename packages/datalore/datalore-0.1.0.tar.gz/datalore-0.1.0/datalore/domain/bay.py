from datalore.shared.domain_model import DomainModel


class Bay(object):

    def __init__(self, code, size, price, latitude, longitude):
        self.code = code
        self.size = size
        self.price = price
        self.latitude = float(latitude)
        self.longitude = float(longitude)

    @classmethod
    def from_dict(cls, adict):
        room = Bay(
            code=adict['code'],
            size=adict['size'],
            price=adict['price'],
            latitude=adict['latitude'],
            longitude=adict['longitude'],
        )

        return room


DomainModel.register(Bay)
