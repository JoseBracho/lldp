import os
import subprocess
import platform
import ipaddress
import bson
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from bson import ObjectId
from dotenv import load_dotenv
from db.MongoDB import MongoDBManager
from models.Device import DeviceModel
from helpers.getdata import getNodos, getInfoVendor
from snmp import SNMP
import time

load_dotenv()

class Devices:

    def __init__(self) -> None:
        self.manager =  MongoDBManager('LLDP')
        self.timeout = 1
        self.max_workers = 255


    def ping_host(self, ip: str) -> bool:
        if platform.system().lower() == 'windows':
            command = ['ping', '-n', '1', '-w', str(self.timeout * 1000), ip]
        else:
            command = ['ping', '-c', '1', '-W', str(self.timeout), ip]
        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=self.timeout + 2
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False
        except Exception as e:
            return False

    def ipMonitoring(self, documents, field):
        active_ips = []
        no_active_ips = []
        for document in documents:
            segments = document.get(field)
            network = ipaddress.ip_network(segments, strict=False)
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                ips = [str(ip) for ip in network.hosts()]
                results = executor.map(self.ping_host, ips)
                for ip, is_active in zip(ips, results):
                    if is_active:
                        active_ips.append(ip)
                    else:
                        no_active_ips.append(ip)
        return [active_ips,no_active_ips]
    
    def getSnmpQuery(self, args):
        ip, community, nodos, info = args

        try:
            snmp = SNMP(ip, community)
            nameDevice = snmp.getNameValue()
            infovendor = snmp.getVendor()
            if len(nameDevice) > 0 and len(infovendor) > 0:
                nickname = nameDevice.split('-')[1] 
                vendor = [vendor for vendor in info if vendor[1] in infovendor] 
                if vendor:  
                    for nodo in nodos:
                        if nickname in nodo:
                            model = DeviceModel(ip, ObjectId(nodo[0]), nameDevice, ObjectId(vendor[0][0]))
                            device_dict = model.to_document()
                            device_dict['last_seen'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            device_dict['status'] = 'active'
                            return device_dict
        except Exception as e:
            print(f"Error en SNMP para IP {ip}: {e}")
        return None

    def getDeviceInfo(self, active_ips, DeviceModel, nodos, info):
        devices = []
        tasks = []
        for ip in active_ips:
            community = ''
            if int(ip.split('.')[-1]) > 29 and int(ip.split('.')[-1]) < 40:
                community = os.getenv('COMMUNITY_SNMP_OLT')
            else:
                community = os.getenv('COMMUNITY_SNMP')
            tasks.append((ip, community, nodos, info))
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_ip = {executor.submit(self.getSnmpQuery, task): task[0] for task in tasks}
            for future in as_completed(future_to_ip):
                ip = future_to_ip[future]
                try:
                    result = future.result(timeout=10)
                    if result:
                        devices.append(result)
                except Exception as e:
                    print(f"Error procesando IP {ip}: {e}")
        return devices
    
    def mark_offline_devices(self, current_ips):
        all_devices = self.manager.find_documents('devices', {'status': 'active'})
        for device in all_devices:
            device_ip = device.get('ip_admin')
            if device_ip in current_ips:
                print(device_ip)
                self.manager.update_document(
                    'devices',
                    {'_id': device['_id']},
                    {
                        'status': 'offline',
                        'last_seen': device.get('last_seen'),
                        'offline_since': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                )
    def mark_online_devices(self, current_ips):
        all_devices = self.manager.find_documents('devices', {'status': 'offline'})
        for device in all_devices:
            device_ip = device.get('ip_admin')
            if device_ip in current_ips:
                self.manager.update_document(
                    'devices',
                    {'_id': device['_id']},
                    {
                        'status': 'active',
                        'last_seen': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                )

    def cleanup_old_offline_devices(self, days=1):
        threshold_date = datetime.now() - timedelta(days=days)
        offline_devices = self.manager.find_documents(
            'devices',
            {'status': 'offline'}
        )
        deleted_count = 0
        for device in offline_devices:
            offline_since = device.get('offline_since')
            if not offline_since:
                continue
            if isinstance(offline_since, str):
                try:
                    offline_since = datetime.fromisoformat(offline_since.replace('Z', '+00:00'))
                except ValueError:
                    continue
            elif isinstance(offline_since, bson.ObjectId):
                offline_since = offline_since.generation_time

            if offline_since < threshold_date:
                try:
                    result = self.manager.delete_document('devices', {'_id': device['_id']})
                    if result:
                        deleted_count += 1
                    else:
                        print(f"Error al eliminar dispositivo {device['_id']}")
                except Exception as e:
                    print(f"Excepción al eliminar dispositivo {device['_id']}: {e}")
    
    def searchDevice(self):
        nodos = self.manager.find_documents('nodos')
        infoDevice = self.manager.find_documents('infodevices')
        vlanAdmin = self.manager.find_documents('vlanAdmins')
        loopback = self.manager.find_documents('loopbacks')
        nodos = getNodos(nodos)
        infoVendor = getInfoVendor(infoDevice)
        result_vlan = self.ipMonitoring(vlanAdmin, 'ip_admin')
        result_loopback = self.ipMonitoring(loopback, 'ip_loopback')
        vlan_admin = self.getDeviceInfo(result_vlan[0], DeviceModel, nodos, infoVendor)
        loopback_admin = self.getDeviceInfo(result_loopback[0], DeviceModel, nodos, infoVendor)
        self.mark_offline_devices(result_vlan[1])
        self.mark_offline_devices(result_loopback[1])
        self.mark_online_devices(result_loopback[0])
        self.mark_online_devices(result_vlan[0])
        self.cleanup_old_offline_devices()
        clean_ip = [loopback_admin,vlan_admin]
        for i in clean_ip:
            for devices in i:
                existing_document  = self.manager.find_documents_one('devices', {'ip_admin': devices.get('ip_admin')})
                if not existing_document:
                    self.manager.insert_document('devices', devices)

            
if __name__ == '__main__':
    while True:
        try:
            inicio = time.time()
            Devices().searchDevice()
            fin = time.time()
            # print(f"Duración del escaneo: {(fin - inicio)/60} minutos")
        except Exception as e:
            print(e)