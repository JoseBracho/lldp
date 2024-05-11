class InfoDeviceModel:
    def __init__(self, make: str, model: str, type: str):
        self.make = make
        self.model = model
        self.type = type

    def to_document(self):
        return {
            "name": self.make,
            "model": self.model,
            "type": self.type
        }