from ..base_device import BaseHost
from ...discovery.discovery_snmp import SNMPMgmt
from ...pollers.snmp_poller import SNMPPoller
# They used the same vendor oid...............

class SNMPPoller_Unifi(SNMPPoller):

    def baseInfo_get_sys_mac(self):
        unifi_mac_oid = ".1.3.6.1.4.1.41112.1.6.2.1.1.4.1"

        try:
            raw = self.snmp_obj.snmpget(unifi_mac_oid)

            match raw[1]:
                case 'STRING':
                    mac = self._normalize_snmp_string(raw[0])
                    mac = ' '.join(f"{ord(c):02x}" for c in mac)
                    return mac.replace(" ", ":")

                case 'Hex-STRING':
                    mac = self._normalize_snmp_string(raw[0]).replace(" ", ":")
                    return mac

                case _:
                    return raw[0]

        except Exception as e:
            print(f"Error: {e}, raw={raw}")
            return None

class UnifiBase(BaseHost):

    host_category = "Access Point"
    vendor = "Unifi"
    model = "Unifi ap"

    def __init__(self, ip, ssh=None, snmp=None):
        super().__init__(ip, ssh, snmp)

        if snmp:
            self.poller_snmp = SNMPPoller_Unifi(snmp)

