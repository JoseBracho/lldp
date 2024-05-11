from bson import ObjectId

class StateModel:
    def __init__(self, name: str):
        self.name = name

    def to_document(self):
        return {
            "name": self.name
        }