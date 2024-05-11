from bson import ObjectId

class VlanAdminModel:
    def __init__(self, ip_admin: str, vlan: str, id_nodo: ObjectId):
        self.ip_admin = ip_admin
        self.vlan = vlan
        self.id_nodo = id_nodo

    def to_document(self):
        return {
            "ip_admin": self.ip_admin,
            "vlan": self.vlan,
            "id_nodo": self.id_nodo
        }