from ..discovery.discovery_snmp import SNMPMgmt

class SNMPPoller:

    def __init__(self, snmp_obj : SNMPMgmt):

        if not snmp_obj:
            raise RuntimeError("SNMP failed")
        
        self.snmp_obj = snmp_obj

    def _normalize_snmp_string(self, value : str) -> str:
            """

            """
            if not value:
                return ""

            return value.strip('"')

    def baseInfo_get_sysName(self) -> str:
        """
        Get system name via SNMP GET (mib-2.system.sysName.0)

        :return: sysName.0 without surrounding quotes, if object type is STRING
        """

        sysName_oid = ".1.3.6.1.2.1.1.5.0"
        value = self.snmp_obj.snmpget(sysName_oid)
        if value[1] == "STRING":
            return self._normalize_snmp_string(value[0])

        return value[0]

    def lldp_get_local_chassis(self) -> str:
        lldpLocChassisId_oid = ".1.0.8802.1.1.2.1.3.2.0"

        local_chassis = self.snmp_obj.snmpget(lldpLocChassisId_oid)

        return self._normalize_snmp_string(local_chassis[0])