def getNodos(documents):
    nodos = []
    for nodo in documents:
        nodos.append((nodo.get('_id'), nodo.get('nickname')))
    return nodos

def getInfoVendor(documents):
    vendors = list()
    for vendor in documents:
        vendors.append([vendor.get('_id'), vendor.get('model')])
    return vendors

def cleanIP(vlan_admin, loopback_admin):
    diccionario = {item['hostname']: item for item in vlan_admin}
    for item in loopback_admin:
        if item['hostname'] in diccionario:
            if item['ip_admin'].startswith('100.127'):
                diccionario[item['hostname']] = item
        else:
            diccionario[item['hostname']] = item
    lista_final = list(diccionario.values())
    return lista_final
