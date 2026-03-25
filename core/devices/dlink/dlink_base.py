from ..base_device import BaseHost
# from utils.common import fix_port_list, convert_hex_to_utf8

class DlinkBase(BaseHost):
    vendor = "D-Link"

class DES_3028(DlinkBase):
    host_category = "Switch"
    model = "DES 3028"

class DES_3028P(DlinkBase):
    host_category = "Switch"
    model = "DES 3028P"

class DES_3526(DlinkBase):
    host_category = "Switch"
    model = "DES 3526"

    def lldp_info_builder(self):

        lldp_info_dict = {
            "LLDP Support": "Device has no LLDP Support"
        }

        return lldp_info_dict

class DES_3550(DlinkBase):
    host_category = "Switch"
    model = "DES 3550"

    def lldp_info_builder(self):

        lldp_info_dict = {
            "LLDP Support": "Device has no LLDP Support"
        }

        return lldp_info_dict

class DES_1210_28(DlinkBase):
    host_category = "Switch"

    # def ipv4_get_info_list(self) -> list:
    #     """
    #     Usually, the MAC of the vlan interface is the MAC of the first port.
    #     Don't know if this model supports multiple IP addresses
    #     """

    #     ipAdEntAddr_oid = ".1.3.6.1.2.1.4.20.1.1"
    #     ipAdEntIfIndex_oid = ".1.3.6.1.2.1.4.20.1.2."
    #     ipAdEntNetMask_oid = ".1.3.6.1.2.1.4.20.1.3."

    #     ip_addr_list = self.snmp.snmpwalk(ipAdEntAddr_oid)

    #     ip_info_dict_list = []

    #     for entry in ip_addr_list:
    #         ip_addr = entry.split()[3]
    #         ip_net_mask = self.snmp.snmpget(ipAdEntNetMask_oid+ip_addr)[0]
    #         if_index = self.snmp.snmpget(ipAdEntIfIndex_oid+ip_addr)[0]
    #         if_descr = self.interface_get_name(if_index) # Remover depois
    #         if_phy_address = self.snmp.snmpgetnext(".1.3.6.1.2.1.2.2.1.6")[0].replace(" ", ":").strip(':')

    #         ip_info_dict_list.append({"Address": ip_addr,
    #                                     "Netmask": ip_net_mask,
    #                                     "MAC Address": if_phy_address,
    #                                     "Interface Index": if_index,
    #                                     "Interface Description": if_descr # Remover depois
    #                                 })

    #     return ip_info_dict_list

class DES_1210_28_B1(DES_1210_28):
    
    model = "DES-1210-28 B1"

    def lldp_info_builder(self):

        lldp_info_dict = {
            "LLDP Status": "Device has no LLDP Support"
        }

        return lldp_info_dict

    # def vlan_get_interface_pvid(self, instance) -> str:
    #     dot1qVlanPvid_oid = ".1.3.6.1.4.1.171.10.75.5.2.7.7.1.1."
    #     value = self.snmp.snmpget(dot1qVlanPvid_oid+instance)

    #     return value[0] # Hopefully type is always INTEGER

    # def vlan_get_name(self, instance) -> str:
    #     vlanStaticName_oid = ".1.3.6.1.4.1.171.10.75.5.2.7.6.1.1."
    #     value = self.snmp.snmpget(vlanStaticName_oid+instance)

    #     if value[1] == "STRING":
    #         return self._normalize_snmp_string(value[0])

    #     if value[1] == "Hex-STRING":
    #         return convert_hex_to_utf8(value[0])

    #     return value[0]
    
    # def vlan_get_static_list(self) -> list:
    #     # iso.3.6.1.4.1.171.10.75.5.2.7.6.1.1.20 = STRING: "UBQ"
    #     # iso.3.6.1.4.1.171.10.75.5.2.7.6.1.1.216 = STRING: "P2"
    #     vlanStaticEntry_oid = ".1.3.6.1.4.1.171.10.75.5.2.7.6.1.1"
    #     vlan_entries = self.snmp.snmpwalk(vlanStaticEntry_oid)
    #     vlan_entry_list = []

    #     for vlan_entry in vlan_entries:
    #         vlan_vid = vlan_entry.split()[0].split('.')[15]
    #         vlan_name = self.vlan_get_name(vlan_vid)
    #         vlan_entry_dict = {"VID": vlan_vid,
    #                            "Name": vlan_name}
    #         vlan_entry_list.append(vlan_entry_dict)
        
    #     return vlan_entry_list

    # def vlan_get_untagged(self, vid) -> dict:
    #     '''
    #     '''
    #     dot1qVlanStaticUntaggedPorts_oid = ".1.3.6.1.4.1.171.10.75.5.2.7.6.1.4."

    #     port_list = self.snmp.snmpget(dot1qVlanStaticUntaggedPorts_oid+vid)[0].split()
    #     port_list = fix_port_list(port_list)

    #     port_untagged_dict = {"VID": vid, "if Indexes": port_list}
        
    #     return port_untagged_dict

    # def vlan_get_tagged(self, vid) -> dict:
    #     dot1qVlanStaticEgressPorts_oid = ".1.3.6.1.4.1.171.10.75.5.2.7.6.1.2."

    #     port_list = self.snmp.snmpget(dot1qVlanStaticEgressPorts_oid+vid)[0].split()
    #     port_list = fix_port_list(port_list)
		
    #     port_untagged_dict = self.vlan_get_untagged(vid)

    #     port_egress_dict = {"VID": vid, "if Indexes": port_list}

    #     for port_egress in reversed(port_egress_dict["if Indexes"]):
    #         if port_egress in port_untagged_dict["if Indexes"]:
    #             port_egress_dict["if Indexes"].remove(port_egress)
        
    #     return port_egress_dict


class DES_1210_28_C1(DES_1210_28):

    model = "DES-1210-28 C1"


    # def vlan_get_interface_pvid(self, instance) -> str:
    #     dot1qVlanPvid_oid = ".1.3.6.1.4.1.171.10.75.18.1.7.7.1.1."
    #     value = self.snmp.snmpget(dot1qVlanPvid_oid+instance)

    #     return value[0] # Hopefully type is always INTEGER

    # def vlan_get_name(self, instance) -> str:
    #     vlanStaticName_oid = ".1.3.6.1.4.1.171.10.75.18.1.7.6.1.1."
    #     value = self.snmp.snmpget(vlanStaticName_oid+instance)

    #     if value[1] == "STRING":
    #         return self._normalize_snmp_string(value[0])

    #     if value[1] == "Hex-STRING":
    #         return convert_hex_to_utf8(value[0])

    #     return value[0]

    # def vlan_get_static_list(self) -> list:
    #     vlanStaticEntry_oid = ".1.3.6.1.4.1.171.10.75.18.1.7.6.1.1"
    #     vlan_entries = self.snmp.snmpwalk(vlanStaticEntry_oid)
    #     vlan_entry_list = []

    #     for vlan_entry in vlan_entries:
    #         vlan_vid = vlan_entry.split()[0].split('.')[15]
    #         vlan_name = self.vlan_get_name(vlan_vid)
    #         vlan_entry_dict = {"VID": vlan_vid,
    #                            "Nome": vlan_name}
    #         vlan_entry_list.append(vlan_entry_dict)
        
    #     return vlan_entry_list

    # def vlan_get_untagged(self, vid) -> dict:
    #     '''
    #     '''
    #     dot1qVlanStaticUntaggedPorts_oid = ".1.3.6.1.4.1.171.10.75.18.1.7.6.1.4."

    #     port_list = self.snmp.snmpget(dot1qVlanStaticUntaggedPorts_oid+vid)[0].split()
    #     port_list = fix_port_list(port_list)

    #     port_untagged_dict = {"VID": vid, "if Indexes": port_list}
        
    #     return port_untagged_dict

    # def vlan_get_tagged(self, vid) -> dict:
    #     dot1qVlanStaticEgressPorts_oid = ".1.3.6.1.4.1.171.10.75.18.1.7.6.1.2."

    #     port_list = self.snmp.snmpget(dot1qVlanStaticEgressPorts_oid+vid)[0].split()
    #     port_list = fix_port_list(port_list)
		
    #     port_untagged_dict = self.vlan_get_untagged(vid)

    #     port_egress_dict = {"VID": vid, "if Indexes": port_list}

    #     for port_egress in reversed(port_egress_dict["if Indexes"]):
    #         if port_egress in port_untagged_dict["if Indexes"]:
    #             port_egress_dict["if Indexes"].remove(port_egress)
        
    #     return port_egress_dict