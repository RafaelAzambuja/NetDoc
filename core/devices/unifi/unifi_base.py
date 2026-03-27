from ..base_device import BaseHost
from ...discovery.discovery_snmp import SNMPMgmt
from ...pollers.snmp_poller import SNMPPoller
# They used the same vendor oid...............

class SNMPPoller_Unifi(SNMPPoller):

    def baseInfo_get_sys_mac(self):
        unifi_mac_oid = ".1.3.6.1.4.1.41112.1.6.2.1.1.4.1"

        try:
            raw = self.snmp_obj.snmpget(unifi_mac_oid)[0]
            mac = self._normalize_snmp_string(raw).replace(" ", ":")
            return mac if mac else None
        except Exception:
            return None

class UnifiBase(BaseHost):

    host_category = "Access Point"
    vendor = "Unifi"
    model = "Unifi ap"

    def __init__(self, ip, ssh=None, snmp=None):
        super().__init__(ip, ssh, snmp)

        if snmp:
            self.poller_snmp = SNMPPoller_Unifi(snmp)

