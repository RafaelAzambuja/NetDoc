from re import compile
from ..discovery.discovery_snmp import SNMPMgmt
from ..common import convert_hex_to_oid, convert_hex_to_utf8


class SNMPPoller:

    def __init__(self, snmp_obj : SNMPMgmt):

        if not snmp_obj:
            raise RuntimeError("SNMP failed")
        
        self.snmp_obj = snmp_obj

    def _normalize_snmp_string(self, value : str) -> str:
            """

            """
            # if None
            if not value:
                return ""

            # else, remove trailing space, tab space, new line

            return value.rstrip()

    # ---------------
    # Base Info
    # ---------------

    def baseInfo_get_sys_mac(self) -> str:
        '''

        '''

        dot1dBaseBridgeAddress_oid = ".1.3.6.1.2.1.17.1.1.0"

        result = self.snmp_obj.snmpget(dot1dBaseBridgeAddress_oid)
        value_type = result[1]
        value = self._normalize_snmp_string(result[0])

        match value_type:

            case 'STRING':
                value = ' '.join(f"{ord(c):02x}" for c in value)
                value = value.replace(" ", ":")
                return value

            case 'Hex-STRING':
                value = value.replace(" ", ":")
                return value

            case _:
                return value

    def baseInfo_get_sysName(self) -> str:
        '''Get system name via SNMP GET (mib-2.system.sysName.0)

        :return: sysName.0 without surrounding quotes, if object type is STRING
        '''

        sysName_oid = ".1.3.6.1.2.1.1.5.0"

        result = self.snmp_obj.snmpget(sysName_oid)
        value_type = result[1]
        value = self._normalize_snmp_string(result[0])

        match value_type:

            case 'STRING':
                return value

            case 'Hex-STRING':
                value = convert_hex_to_utf8(value)
                return value

            case _:
                return value

    def baseInfo_get_sysLocation(self) -> str:
        '''Get system location via SNMP GET (mib-2.system.sysLocation.0)

        :return: sysLocation.0 without surrounding quotes, if object type is STRING
        '''

        sysLocation_oid = ".1.3.6.1.2.1.1.6.0"

        result = self.snmp_obj.snmpget(sysLocation_oid)
        value_type = result[1]
        value = self._normalize_snmp_string(result[0])

        match value_type:

            case 'STRING':
                return value

            case 'Hex-STRING':
                value = convert_hex_to_utf8(value)
                return value
            
            case _:
                return value

    # ---------------
    # VLAN
    # ---------------

    def vlan_get_static_list(self) -> list:
        '''
        
        '''

        vlanStaticEntry_oid = ".1.3.6.1.2.1.17.7.1.4.3.1.1"

        result = self.snmp_obj.snmpwalk(vlanStaticEntry_oid)
        vlan_entry_list = []

        for entry in result:
            parts = entry.split()
            oid = parts[0]
            value_type = parts[2]

            vlan_vid = oid.split('.')[13]
            vlan_name = vlan_name = " ".join(parts[3:])

            vlan_name = self._normalize_snmp_string(vlan_name)

            match value_type:
                case 'Hex-String':
                    vlan_name = convert_hex_to_utf8(vlan_name)

            vlan_entry_list.append({
                "VID": vlan_vid,
                "Name": vlan_name
            })
        
        return vlan_entry_list

    # ---------------
    # INTERFACES
    # ---------------

    def interface_get_list(self) -> list:

        ifType_oid = ".1.3.6.1.2.1.2.2.1.3"
        
        result = self.snmp_obj.snmpwalk(ifType_oid)

        if not result:
            return []

        iface_list_dict = []
        
        for entry in result:

            object_instance, _, _, if_type, *_ = entry.split()
            if_index = object_instance.rsplit('.', 1)[-1]

            data = {
                "Interface ifIndex": if_index,
                "Interface Description": self.interface_get_name(if_index),
                "Interface Alias": self.interface_get_alias(if_index),
                "Interface Type": self._identify_interface_type(if_type)[0],
                "Interface Physical Address": self.interface_get_phyAddress(if_index)
            }

            iface_list_dict.append(data)
        
        return iface_list_dict

    def _identify_interface_type(self, interface_type) -> tuple:

        # Not sure about 'scope'
        match interface_type:
            case '1': # Undefined. Usually CPU.
                return ("Other", "Other")
            
            case '6': # ethernetCsmacd (RFC 3635).
                return ("ethernetCsmacd", "Port")
            
            case '24': # softwareLoopback
                return ("softwareLoopback", "Loopback")
            
            case '53': # Proprietary Virtual/Internal
                return ("propVirtual", "Proprietary")
            
            case '117': # gigabitEthernet. Obsolet. should return ethernetCsmacd
                return ("gigabitEthernet", "Port")
            
            case '131': # tunnel
                return ("tunnel", "Tunnel")
            
            case '135': # l2vlan 802.1Q
                return ("l2vlan", "VLAN")
            
            case '136': # l3ipvlan. vlan "with IP"
                return ("l3ipvlan", "VLAN")
            
            case '161': # IEEE 802.3ad Link Aggregate
                return ("LAG 802.3ad", "Link Aggregation")
            
            case _:
                return (interface_type, "Unknown")

    def interface_get_name(self, instance) -> str:
        """
        Get interface textual name via SNMP GET (mib-2.ifMIB.ifName.instance)

        :return: If value is STRING: ifName.instance without surrounding quotes
        :return: If value is Hex-STRING: ifName.instance converted to UTF-8
        """

        ifName_oid = ".1.3.6.1.2.1.31.1.1.1.1."
        value = self.snmp_obj.snmpget(ifName_oid+instance)

        if not value[0]:
            return ""

        if value[1] == "STRING":
            return self._normalize_snmp_string(value[0])

        if value[1] == "Hex-STRING":
            return convert_hex_to_utf8(value[0])

        return value[0]

    def interface_get_type(self, instance) -> dict:
        """
        Get interface enumerated value for IANAifType-MIB DEFINITIONS via SNMP GET (mib-2.ifMIB.ifType.instance)

        :return:
        """

        ifType_oid = ".1.3.6.1.2.1.2.2.1.3."
        value = self.snmp_obj.snmpget(ifType_oid+instance)

        return value[0] # Hopefully type is always INTEGER

    def interface_get_phyAddress(self, instance) -> str:
        """

        """

        ifPhyAddress_oid = ".1.3.6.1.2.1.2.2.1.6."
        value = self.snmp_obj.snmpget(ifPhyAddress_oid+instance)

        if any(value):
            return value[0].replace(" ", ":").strip(':') # Hopefully type is always Hex-STRING
        return ""

    def interface_get_alias(self, instance) -> str:
        """

        """

        ifAlias_oid = ".1.3.6.1.2.1.31.1.1.1.18."
        value = self.snmp_obj.snmpget(ifAlias_oid+instance)

        if value[1] == "STRING":
            return self._normalize_snmp_string(value[0])

        if value[1] == "Hex-STRING":
            return convert_hex_to_utf8(value[0])

        return value[0]

    # ---------------
    # TOPOLOGY
    # ---------------

    def lldp_normalize_chassis_id_subtype(self, chassis : tuple, chassis_id_subtype : str) -> tuple:
        match chassis_id_subtype:

            case '1': # entPhysicalAlias (stack member?)

                if chassis[1] == "STRING":
                    chassis = self._normalize_snmp_string(chassis[0])
                elif chassis[1] == "Hex-STRING":
                    chassis = chassis[0].replace(" ", ":").strip('"')
                
                return (chassis, "chassisComponent")
            
            case '2': # ifAlias

                if chassis[1] == "STRING":
                    chassis = self._normalize_snmp_string(chassis[0])
                elif chassis[1] == "Hex-STRING":
                    chassis = convert_hex_to_utf8(chassis[0])
                #     chassis = chassis[0].replace(" ", ":").strip('"')
                
                return (chassis, "interfaceAlias")
            
            case '3': # entPhysicalAlias (port)

                if chassis[1] == "STRING":
                    chassis = self._normalize_snmp_string(chassis[0])
                elif chassis[1] == "Hex-STRING":
                    chassis = chassis[0].replace(" ", ":").strip('"')
                return (chassis, "portComponent")
            
            case '4': # unicast source address

                if chassis[1] == "STRING":
                    chassis = self._normalize_snmp_string(chassis[0])
                elif chassis[1] == "Hex-STRING":
                    chassis = chassis[0].replace(" ", ":").strip('"')
                return (chassis, "macAddress")
            
            case '5': # network address

                if chassis[1] == "STRING":
                    chassis = self._normalize_snmp_string(chassis[0])
                # elif local_chassis[1] == "Hex-STRING": # Haven't found this case yet.
                #
                return (chassis, "networkAddress")
            
            case '6': # ifName

                if chassis[1] == "STRING":
                    chassis = self._normalize_snmp_string(chassis[0])
                # elif local_chassis[1] == "Hex-STRING": # Haven't found this case yet.
                #
                return (chassis, "interfaceName")
            
            case '7': # Locally Assigned

                if chassis[1] == "STRING":
                    chassis = self._normalize_snmp_string(chassis[0])
                # elif local_chassis[1] == "Hex-STRING": # Haven't found this case yet.
                # Probable conversion to utf8
                return (chassis, "local")
            
            case _:
                return (chassis[0], f"Unknown Subtype: {chassis_id_subtype}")

    def lldp_normalize_port_subtype(self, port, port_subtype):
        
        match port_subtype:
            case '1':

                if port[1] == "STRING":
                    port = self._normalize_snmp_string(port[0])
                elif port[1] == "Hex-STRING":
                    port = convert_hex_to_utf8(port[0])
                #    port = port[0].replace(" ", ":").strip('"')

                return (port, "interfaceAlias")
            
            case '2':

                if port[1] == "STRING":
                    port = self._normalize_snmp_string(port[0])
                elif port[1] == "Hex-STRING":
                    port = port[0].replace(" ", ":").strip('"')

                return (port, "portComponent")
            
            case '3':

                if port[1] == "STRING":
                    port = self._normalize_snmp_string(port[0])
                elif port[1] == "Hex-STRING":
                    port = port[0].replace(" ", ":").strip('"')
                
                return (port, "macAddress")
            
            case '4':
                
                if port[1] == "STRING":
                    port = self._normalize_snmp_string(port[0])

                return (port, "networkAddress")
            
            case '5':

                if port[1] == "STRING":
                    port = self._normalize_snmp_string(port[0])
                elif port[1] == "Hex-STRING":
                    port = convert_hex_to_utf8(port[0])
                    # port = port[0].replace(" ", ":").strip('"')
                return (port, "interfaceName")
            
            case '6':
                
                if port[1] == "STRING":
                    port = self._normalize_snmp_string(port[0])
                elif port[1] == "Hex-STRING":
                    port = convert_hex_to_utf8(port[0])

                return (port, "agentCircuitId")
            
            case '7':
                if port[1] == "STRING":
                    port = self._normalize_snmp_string(port[0])
                return (port, "local")
            
            case _:
                return (port[0], "Unknown port subtype")

    def lldp_get_local_chassis(self) -> tuple | None:
        lldpLocChassisId_oid = ".1.0.8802.1.1.2.1.3.2.0"

        local_chassis = self.snmp_obj.snmpget(lldpLocChassisId_oid)

        return (self._normalize_snmp_string(local_chassis[0]), local_chassis[1])

    def lldp_get_local_chassis_subtype(self) -> str | None:
        lldpLocChassisIdSubtype_oid = ".1.0.8802.1.1.2.1.3.1.0"

        local_chassis_id_subtype = self.snmp_obj.snmpget(lldpLocChassisIdSubtype_oid)
        
        if local_chassis_id_subtype[0]:
            return local_chassis_id_subtype[0]
        
        return None

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
        lldpRemPortIdSubtype_oid = ".1.0.8802.1.1.2.1.4.1.1.6."
        value = self.snmp_obj.snmpget(lldpRemPortIdSubtype_oid+instance)
        if not value:
            return ""

        return value[0]

    def fdb_lookup(self, mac) -> tuple:
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