from re import compile
from ..discovery.discovery_snmp import SNMPMgmt
from ..common import normalize_result, convert_hex_to_oid, convert_hex_to_utf8, convert_port_list
from ..constants import *


class SNMPPoller:

    def __init__(self, snmp_obj : SNMPMgmt):

        if not snmp_obj:
            raise RuntimeError("SNMP failed")
        
        self.snmp_obj = snmp_obj

    # ---------------
    # Base Info
    # ---------------

    def baseInfo_get_sysName(self, oid : str = SYS_NAME_OID) -> str:
        '''Get system name via SNMP GET (mib-2.system.sysName.0)

        '''

        value, value_type = self.snmp_obj.snmpget(oid)
        value = normalize_result(value, value_type, "utf8")

        return value

    def baseInfo_get_sysLocation(self, oid : str = SYS_LOCATION_OID) -> str:
        '''Get system location via SNMP GET (mib-2.system.sysLocation.0)

        '''

        value, value_type = self.snmp_obj.snmpget(oid)
        value = normalize_result(value, value_type, "utf8")

        return value

    def baseInfo_get_sys_mac(self, oid : str = BRIDGE_ADDRESS_OID) -> str:
        '''

        '''

        value, value_type = self.snmp_obj.snmpget(oid)
        value = normalize_result(value, value_type, "mac")

        return value

    # ---------------
    # VLAN
    # ---------------

    def vlan_get_static_list(self, oid : str = VLAN_STATIC_ENTRY_OID) -> list:
        '''
        
        '''

        result = self.snmp_obj.snmpwalk(oid)
        vlan_entry_list = []

        for entry in result:
            vlan_id, vlan_name, value_type = entry
            vlan_id = vlan_id.rsplit('.', 1)[-1]
            vlan_name = normalize_result(vlan_name, value_type, "utf8")

            vlan_entry_list.append({
                "VID": vlan_id,
                "Name": vlan_name
            })
        
        return vlan_entry_list

    def vlan_get_interface_pvid(self, port_index : str, oid : str = VLAN_PORT_VID) -> str:
        '''
        
        '''

        value, value_type = self.snmp_obj.snmpget(oid + '.' + port_index)
        value = normalize_result(value, value_type, "mac")

        return value
    
    def vlan_get_untagged(self, vid : str, oid : str = VLAN_UNTAGGED_PORTS) -> list:
        '''
        
        '''

        result = self.snmp_obj.snmpget(oid + '.' + vid)
        
        if not result[1]:
            return []

        port_list = result[0].split()
        port_list = convert_port_list(port_list)

        #port_untagged_dict = {"VID": vid, "if Indexes": port_list}
        
        #return port_untagged_dict
        return port_list

    def vlan_get_tagged(self, vid : str, oid : str = VLAN_EGRESS_PORTS) -> dict:
        '''
        
        '''

        result = self.snmp_obj.snmpget(oid + '.' + vid)

        if not result[1]:
            return []

        port_list = result[0].split()
        port_list = convert_port_list(port_list)
		
        port_untagged_dict = self.vlan_get_untagged(vid)
        port_egress_dict = {"VID": vid, "if Indexes": port_list}

        for port_egress in reversed(port_egress_dict["if Indexes"]):
            if port_egress in port_untagged_dict["if Indexes"]:
                port_egress_dict["if Indexes"].remove(port_egress)
        
        return port_egress_dict

    # ---------------
    # INTERFACES
    # ---------------

    def interface_get_list(self) -> list:
        
        result = self.snmp_obj.snmpwalk(INTERFACE_TYPE_OID)

        if not result:
            return []

        iface_list_dict = []
        
        for entry in result:
            if_index, if_type, value_type = entry
            if_index = if_index.rsplit('.', 1)[-1]
            if_type = normalize_result(if_type, value_type, "utf8")

            data = {
                "Interface ifIndex": if_index,
                "Interface Description": self.interface_get_name(if_index),
                "Interface Alias": self.interface_get_alias(if_index),
                "Interface Type": self._identify_interface_type(if_type)[0],
                "Interface Physical Address": self.interface_get_phyAddress(if_index),
                "PVID": self.vlan_get_interface_pvid(if_index),
            }

            iface_list_dict.append(data)
        
        return iface_list_dict

    def _identify_interface_type(self, interface_type: str) -> tuple:
        if interface_type in INTERFACE_TYPE_MAP:
            return INTERFACE_TYPE_MAP[interface_type]
        return (interface_type, "Unknown")

    def interface_get_name(self, port_index : str, oid = INTERFACE_NAME_OID) -> str:
        """Get interface textual name via SNMP GET (mib-2.ifMIB.ifName.instance)

        :return: If value is STRING: ifName.instance without surrounding quotes
        :return: If value is Hex-STRING: ifName.instance converted to UTF-8
        """

        value, value_type = self.snmp_obj.snmpget(oid + '.' + port_index)
        value = normalize_result(value, value_type, "utf8")

        return value

    def interface_get_type(self, port_index : str, oid = INTERFACE_TYPE_OID) -> dict:
        """Get interface enumerated value for IANAifType-MIB DEFINITIONS via SNMP GET (mib-2.ifMIB.ifType.instance)

        :return:
        """

        value, value_type = self.snmp_obj.snmpget(oid + '.' + port_index)
        value = normalize_result(value, value_type, "utf8")

        return value

    def interface_get_phyAddress(self, port_index, oid = INTERFACE_PHYSICAL_ADDRESS_OID) -> str:
        """

        """

        value, value_type = self.snmp_obj.snmpget(oid + '.' + port_index)
        value = normalize_result(value, value_type, "mac")

        return value

    def interface_get_alias(self, port_index, oid = INTERFACE_ALIAS_OID) -> str:
        """

        """

        value, value_type = self.snmp_obj.snmpget(oid + '.' + port_index)
        value = normalize_result(value, value_type, "utf8")

        return value

    # ---------------
    # TOPOLOGY
    # ---------------

    def lldp_normalize_chassis_id_subtype(self, chassis : tuple, subtype : str) -> tuple:
        value, value_type = chassis

        label, mode = LLDP_CHASSIS_SUBTYPE_MAP.get(
            subtype,
            (f"Unknown Subtype: {subtype}", None)
        )

        value = normalize_result(value, value_type, mode)

        return (value, label)

    def lldp_normalize_port_subtype(self, port, port_subtype):
        
        value, value_type = port

        label, mode = LLDP_PORT_SUBTYPE_MAP.get(
            port_subtype,
            (f"Unknown Subtype: {port_subtype}", None)
        )

        value = normalize_result(value, value_type, mode)

        return (value, label)

    def lldp_get_local_chassis(self, oid = LLDP_CHASSIS_ID_OID) -> tuple | None:
        '''

        '''

        chassis_id, chassis_id_value_type = self.snmp_obj.snmpget(oid)
        chassis_subtype, chassis_subtype_value_type = self.lldp_get_local_chassis_subtype()

        mapped_type, mode = self.lldp_normalize_chassis_id_subtype(chassis_id, chassis_subtype)

        chassis_id = normalize_result(chassis_id, chassis_id_value_type, mode)
        
        return chassis_id, mapped_type

    def lldp_get_local_chassis_subtype(self, oid = LLDP_CHASSIS_ID_SUBTYPE_OID) -> str | None:
        '''
        
        '''

        value, value_type = self.snmp_obj.snmpget(LLDP_CHASSIS_ID_SUBTYPE_OID)

        return value, value_type

    def lldp_get_remote_entry_list(self) -> dict:


        # Remote Man Addr is unreliable

        lldpRemChassisId_oid = ".1.0.8802.1.1.2.1.4.1.1.5"
        lldpRemChassisIdSubtype_oid = ".1.0.8802.1.1.2.1.4.1.1.4."

        
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

            time_mark = str(m.group(1))
            local_port = str(m.group(2))
            rem_index = str(m.group(3))

            chave = (local_port, rem_index)

            if chave not in validos or time_mark > validos[chave]:
                validos[chave] = time_mark

        # 1.0.8802.1.1.2.1.4.1.1.5.timeMark.locPort.lldpRemIndex
        # "timeMark.localPort.remIndex"

        data = {}
        for (local_port, rem_index), time_mark in validos.items():

            remote_chassis = self.snmp_obj.snmpget(".1.0.8802.1.1.2.1.4.1.1.5."+f"{time_mark}.{local_port}.{rem_index}")
            remote_chassis_subtype = self.snmp_obj.snmpget(lldpRemChassisIdSubtype_oid+f"{time_mark}.{local_port}.{rem_index}")[0]
            remote_port = self.snmp_obj.snmpget(".1.0.8802.1.1.2.1.4.1.1.7."+f"{time_mark}.{local_port}.{rem_index}")
            remote_port_subtype = self.lldp_get_remote_port_id_subtype(f"{time_mark}.{local_port}.{rem_index}")[0]

            remote_chassis_info = self.lldp_normalize_chassis_id_subtype(remote_chassis, remote_chassis_subtype)
            remote_port_info = self.lldp_normalize_port_subtype(remote_port, remote_port_subtype)

            local_port = self.interface_get_name(local_port)

            data[local_port] = {
                "Remote Host": remote_chassis_info[0],
                "Remote Chassis Subtype": remote_chassis_info[1],
                "Remote Port": remote_port_info[0],
                "Remote Port Subtype": remote_port_info[1]
            }

        return data


    def lldp_get_remote_port_id_subtype(self, instance):
        '''
        
        '''

        lldpRemPortIdSubtype_oid = ".1.0.8802.1.1.2.1.4.1.1.6."

        value, value_type = self.snmp_obj.snmpget(lldpRemPortIdSubtype_oid+instance)
        value = self._normalize_snmp_string(value)

        return value

    def fdb_lookup(self, mac) -> tuple:
        '''
        
        '''
        
        dot1qTpFdbPort_oid = ".1.3.6.1.2.1.17.7.1.2.2.1.2."

        vlan_list = self.vlan_get_static_list()
        mac = convert_hex_to_oid(mac)

        # !!!!!!!!!!!!!!!!!
        # Bug here: Cisco switches won't return vlan 1 in vlan static list
        # !!!!!!!!!!!!!!!!!

        for vlan in vlan_list:
            portIndex = self.snmp_obj.snmpget(dot1qTpFdbPort_oid+vlan["VID"]+mac)
            if portIndex[0]:
                local_port = self.interface_get_name(portIndex[0])
                return (vlan["VID"], local_port)
        
        return ""