from ..base_device import BaseHost
from ...pollers.snmp_poller import SNMPPoller

class SNMPPoller_Cisco(SNMPPoller):

    def vlan_get_static_list(self) -> dict:
        
        # Don't know how to fix the vlan 1 issue with cisco, so just add manually and pray

        vlan_list = [{"VID": '1', "Name": "VLAN0001"}]
        vlan_list.extend(super().vlan_get_static_list())
        return vlan_list

    def vlan_get_untagged(self, vid) -> list:
        '''
        
        '''
        
        if str(vid) == '1':
            return []
        
        return super().vlan_get_untagged(vid)
    
class CiscoBase(BaseHost):
    vendor = "Cisco"

    def __init__(self, ip, ssh=None, snmp=None):
        super().__init__(ip, ssh, snmp)

        if snmp:
            self.poller_snmp = SNMPPoller_Cisco(snmp)

class Cisco_SF300_24(CiscoBase):
    host_category = "Switch"
    model = "SF300-24"

class Cisco_SF300_48(CiscoBase):
    host_category = "Switch"
    model = "SF300-48"

class Cisco_SG300_28PP(CiscoBase):
    host_category = "Switch"
    model = "SG300-28PP"