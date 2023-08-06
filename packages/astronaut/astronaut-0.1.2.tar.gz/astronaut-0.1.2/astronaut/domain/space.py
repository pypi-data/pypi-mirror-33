from astronaut.shared.domain_model import DomainModel


class Space(object):

    def __init__(self, code, size, price, latitude, longitude):
        self.code = code
        self.size = size
        self.price = price
        self.latitude = float(latitude)
        self.longitude = float(longitude)

    @classmethod
    def from_dict(cls, adict):
        room = Space(
            code=adict['code'],
            size=adict['size'],
            price=adict['price'],
            latitude=adict['latitude'],
            longitude=adict['longitude'],
        )

        return room


DomainModel.register(Space)
