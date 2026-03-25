from re import compile
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

    def lldp_get_remote_entry_list(self) -> dict:
        lldpRemChassisId_oid = ".1.0.8802.1.1.2.1.4.1.1.5"
        # 1.0.8802.1.1.2.1.4.1.1.5.timeMark.locPort.lldpRemIndex
        lldp_rem_entry_list = self.snmp_obj.snmpwalk(lldpRemChassisId_oid)

        regex = compile(
            r"iso\.0\.8802\.1\.1\.2\.1\.4\.1\.1\.5\.(\d+)\.(\d+)\.(\d+)\s*=\s*(.*)"
        )

        validos = {}
        if not lldp_rem_entry_list:
            return {}
        for lldp_rem_entry in lldp_rem_entry_list:
            m = regex.match(lldp_rem_entry)
            if not m:
                continue

            time_mark = int(m.group(1))
            local_port = int(m.group(2))
            rem_index = int(m.group(3))

            chave = (local_port, rem_index)

            # Mantém apenas o maior timemark para cada chave
            if chave not in validos or time_mark > validos[chave]:
                validos[chave] = time_mark

        # "timeMark.localPort.remIndex"

        data = {}
        for (local_port, rem_index), time_mark in validos.items():
            data[local_port] = {
                "Remote Host": self._normalize_snmp_string(self.snmp_obj.snmpget(".1.0.8802.1.1.2.1.4.1.1.5."+f"{time_mark}.{local_port}.{rem_index}")[0]),
                "Remote Port": self._normalize_snmp_string(self.snmp_obj.snmpget(".1.0.8802.1.1.2.1.4.1.1.7."+f"{time_mark}.{local_port}.{rem_index}")[0])
            }

        return data