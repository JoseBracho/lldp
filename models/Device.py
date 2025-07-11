from bson import ObjectId

class DeviceModel:
    def __init__(self, ip_admin: str, id_nodo: ObjectId, hostname = '',   id_info_device = ''):
        self.hostname = hostname
        self.ip_admin = ip_admin
        self.id_nodo = id_nodo
        self.id_info_device = id_info_device
        
    def to_document(self):
        return {
            "hostname": self.hostname,
            "ip_admin": self.ip_admin,
            "id_nodo": self.id_nodo,
            "id_info_device": self.id_info_device,
        }