import os
import subprocess
from bson import ObjectId
from dotenv import load_dotenv
from db.MongoDB import MongoDBManager
from models.Device import DeviceModel
from helpers.getdata import getNodos, getInfoVendor
from snmp import SNMP

load_dotenv()

class Devices:

    def __init__(self) -> None:
        self.manager =  MongoDBManager('LLDP')

    def getIpactive(self, documents, field, DeviceModel, nodos, info):
        devices = []
        for document in documents:
            segments = document.get(field).split('0/')[0]
            ips = [segments + str(i) for i in range(1, 115)]
            active_ips = [ip for ip in ips if subprocess.call(["ping", "-c", "2", ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0]
            for ip in active_ips:
                community = ''
                if int(ip.split('.')[-1]) > 29:
                    community = os.getenv('COMMUNITY_SNMP_OLT')
                else:
                    community = os.getenv('COMMUNITY_SNMP')
                try:
                    snmp = SNMP(ip, community)
                    nameDevice = snmp.getNameValue()
                    infovendor = snmp.getVendor()
                    if len(nameDevice) > 0 and len(infovendor) > 0:
                        nickname = nameDevice.split('-')[1]
                        vendor = [vendor for vendor in info if vendor[1] in infovendor]
                        if len(vendor) > 0:
                            vendor = vendor[0]
                            for nodo in nodos:
                                if nickname in nodo:
                                    model = DeviceModel(ip, ObjectId(nodo[0]), nameDevice,  ObjectId(vendor[0]))
                                    devices.append(model.to_document())
                        else:
                            for nodo in nodos:
                                if nickname in nodo:
                                    model = DeviceModel(ip, ObjectId(nodo[0]), nameDevice)
                                    devices.append(model.to_document())                  
                    else:
                        for nodo in nodos:
                                if nickname in nodo:
                                    model = DeviceModel(ip, ObjectId(nodo[0]))
                                    devices.append(model.to_document())          
                except Exception as e:
                    print(e)
        return devices
    
    def searchDevice(self):
        nodos = self.manager.find_documents('nodos')
        infoDevice = self.manager.find_documents('infodevices')
        vlanAdmin = self.manager.find_documents('vlanAdmins')
        loopback = self.manager.find_documents('loopbacks')
        nodos = getNodos(nodos)
        infoVendor = getInfoVendor(infoDevice)
        vlan_admin = self.getIpactive(vlanAdmin, 'ip_admin', DeviceModel, nodos, infoVendor)
        loopback_admin = self.getIpactive(loopback, 'ip_loopback', DeviceModel, nodos, infoVendor)
        clean_ip = [vlan_admin, loopback_admin]
        for i in clean_ip:
            for devices in i:
                existing_document  = self.manager.find_documents_one('devices', {'ip_admin': devices.get('ip_admin')})
                if not existing_document:
                    self.manager.insert_document('devices', devices)

            
if __name__ == '__main__':
    while True:
        try:
            Devices().searchDevice()
        except Exception as e:
            print(e)