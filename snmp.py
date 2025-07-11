from pysnmp.entity.rfc3413.oneliner import cmdgen

class SNMP:
    
    def __init__(self, host, community) -> None:
        self._host = host
        self._SYSNAME = '1.3.6.1.2.1.1.5.0'
        self._VENDOR = '1.3.6.1.2.1.1.1.0'
        self._COMMUNITY = community
        
    def getNameValue(self,):
        response = ''
        oid = self._SYSNAME
        auth = cmdgen.CommunityData(self._COMMUNITY)
        cmdGen = cmdgen.CommandGenerator()
        errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
            auth,
            cmdgen.UdpTransportTarget((self._host, 161)),
            cmdgen.MibVariable(oid),
            lookupMib=False,
        )
        for oid, val in varBinds:
            response = val.prettyPrint()
        return response
    
    def getVendor(self,):
        response = ''
        oid = self._VENDOR
        auth = cmdgen.CommunityData(self._COMMUNITY)
        cmdGen = cmdgen.CommandGenerator()
        errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
            auth,
            cmdgen.UdpTransportTarget((self._host, 161)),
            cmdgen.MibVariable(oid),
            lookupMib=False,
        )
        for oid, val in varBinds:
            response = val.prettyPrint()
        return response

if __name__ == '__main__':
    ...