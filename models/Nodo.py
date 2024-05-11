from bson import ObjectId

class NodoModel:
    def __init__(self, name: str, nickname: str, id_state: ObjectId):
        self.id_state = id_state
        self.name = name
        self.nickname = nickname

    def to_document(self):
        return {
            "id_state": self.id_state,
            "name": self.name,
            "nickname": self.nickname
        }