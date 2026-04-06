from ..pollers.snmp_poller import SNMPPoller


class BaseHost:

    host_category = "Unknown"
    vendor = None
    model = None
    
    def __init__(self, ip, ssh = None, snmp = None):

        # Older implementations would try to scan sockets to identify services
        # We chose to just set a "management address" with whatever came from icmp_phase

        self.ip = ip
        self.poller_snmp = SNMPPoller(snmp)
        self.ssh = ssh
        self.host_category = self.host_category
        self.vendor = self.vendor
        self.model = self.model

        if snmp and not self.vendor:
            self.vendor = snmp.vendor_oid


    def device_doc_decision(self):

        data = {}
        match self.host_category:
            case "Switch":
                data["Base"] = self.general_baseInfo_builder()
                data["Interfaces"] = self.interface_get_list()
                data["VLANS"] = self.vlan_get_static_list()
                #data["LLDP"] = self.lldp_info_builder()
                ## Fix logic below
                #lldp_neighbor_list = self.lldp_get_remote_list()
                #if self.lldp_get_local_chassis():
                #    data["LLDP"]["Remote"] = []

                #    for loc_port, neighbor_info in lldp_neighbor_list.items():
                #        data["LLDP"]["Remote"].append({
                #            "Local Port": loc_port,
                #            "Neighbor": neighbor_info
                #        })

            case "Access Point":
                data["Base"] = self.general_baseInfo_builder()
                data["Interfaces"] = self.interface_get_list()
                #data["LLDP"] = self.lldp_info_builder()
                ## Fix logic below
                #lldp_neighbor_list = self.lldp_get_remote_list()
                # if self.lldp_get_local_chassis():
                #     data["LLDP"]["Remote"] = []

                #     for loc_port, neighbor_info in lldp_neighbor_list.items():
                #         data["LLDP"]["Remote"].append({
                #             "Local Port": loc_port,
                #             "Neighbor": neighbor_info
                #         })
        return data

    # ---------------
    # Base Info
    # ---------------

    def general_baseInfo_builder(self) -> dict:

        # Info that can be polled from the vast majority of IT Devices

        base_info_dict = {
            "System Management IP Address": self.ip,
            "System MAC Address": self.baseInfo_get_sys_mac(), # System MAC can be: LLDP Chassis, MAC of L3 Interface (i.e. vlan interface), MAC of the lowest index port in if-MIB, or bridge address (dot1dBaseBridgeAddress)
            "System Name": self.baseInfo_get_sysName(),
            "System Location": self.baseInfo_get_sysLocation(),
            "System Model": self.model,
            "System Vendor": self.vendor
        }

        return base_info_dict

    def baseInfo_get_sys_mac(self) -> str:
        """
        """

        # Unknow vendor = No fallback to SSH, HTTP, etc.
        try:
            sys_mac = self.poller_snmp.baseInfo_get_sys_mac()

        except:
            sys_mac = self.poller_snmp.baseInfo_vendor_get_sys_mac()
        # except:
            # poller_ssh = ...

        finally:
            return sys_mac

    def baseInfo_get_sysName(self) -> str:
        """
        """

        # Unknow vendor = No fallback to SSH, HTTP, etc.
        try:
            sys_name = self.poller_snmp.baseInfo_get_sysName()

        # except:
            # poller_ssh = ...

        finally:
            return sys_name

    def baseInfo_get_sysLocation(self):

        # Unknow vendor = No fallback to SSH, HTTP, etc.
        try:
            sys_location = self.poller_snmp.baseInfo_get_sysLocation()

        # except:
            # poller_ssh = ...

        finally:
            return sys_location

    # ---------------
    # VLAN
    # ---------------

    def vlan_get_static_list(self) -> list:
        """
        """
        
        # Check VLAN auto create

        try:
            vlan_list = self.poller_snmp.vlan_get_static_list()

        # except:
            # poller_ssh = ...

        except:
            vlan_list = []
        finally:
            return vlan_list

    # ---------------
    # INTERFACES
    # ---------------

    def interface_get_list(self) -> list:
        """
        """

        try:
            iface_list = self.poller_snmp.interface_get_list()

        # except:
            # poller_ssh = ...

        finally:
            return iface_list

    # ---------------
    # TOPOLOGY
    # ---------------

    def lldp_info_builder(self) -> dict:

        lldp_info_dict = {}

        local_chassis = self.lldp_get_local_chassis()
        local_chassis_subtype = self.lldp_get_local_chassis_subtype()

        if local_chassis and local_chassis_subtype:
            chassis_info = self.lldp_normalize_subtype(local_chassis, local_chassis_subtype)

            lldp_info_dict = {
                "LLDP Status": "Enabled", # Needs logic to identify globally disabled
                "LLDP Local Chassis": chassis_info[0],
                "LLDP Local Chassis Subtype": chassis_info[1],
            }

            return lldp_info_dict
        
        return { "LLDP Status": "Unsupported" }
    
    def lldp_get_local_chassis(self) -> dict:

        try:
            lldp_local_chassis = self.poller_snmp.lldp_get_local_chassis()

        # except:

        finally:
            return lldp_local_chassis

    def lldp_get_local_chassis_subtype(self) -> dict:

        try:
            lldp_local_chassis_subtype = self.poller_snmp.lldp_get_local_chassis_subtype()

        # except:

        finally:
            return lldp_local_chassis_subtype

    def lldp_normalize_subtype(self, chassis, subtype):

        # SNMP because of _normalize_snmp_string. Needs fix.
        return self.poller_snmp.lldp_normalize_chassis_id_subtype(chassis, subtype)

    def lldp_get_remote_list(self) -> dict:

        try:
            lldp_remote = self.poller_snmp.lldp_get_remote_entry_list()

        # except:

        finally:
            return lldp_remote

    def fdb_lookup(self, mac) -> tuple:
        fdb_local_port = ()
        try:
            fdb_local_port = self.poller_snmp.fdb_lookup(mac)

        # except:

        finally:
            # vlan, local_port
            return fdb_local_port