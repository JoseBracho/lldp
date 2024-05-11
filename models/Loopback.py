from bson import ObjectId

class LoopbackModel:
    def __init__(self, id_nodo: ObjectId, ip_loopback: str):
        self.id_nodo = id_nodo
        self.ip_loopback = ip_loopback

    def to_document(self):
        return {
            "id_nodo": self.id_nodo,
            "ip_loopback": self.ip_loopback
        }