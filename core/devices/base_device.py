from ..pollers.snmp_poller import SNMPPoller

class BaseHost:

    host_category = "Unknown"
    vendor = None
    model = None
    
    def __init__(self, ip, ssh = None, snmp = None):

        # Older implementations would try to scan sockets to identify services
        # We chose to just set a "management address" with whatever came from icmp_phase

        self.ip = ip
        self.snmp = snmp
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
                data["LLDP"] = self.lldp_info_builder()
                # Fix logic below
                lldp_neighbor_list = self.lldp_get_remote_list()
                if self.lldp_get_local_chassis():
                    data["LLDP"]["Remote"] = []

                    for loc_port, neighbor_info in lldp_neighbor_list.items():
                        data["LLDP"]["Remote"].append({
                            "Local Port": loc_port,
                            "Neighbor": neighbor_info
                        })

        return data

    def general_baseInfo_builder(self) -> dict:

        # Info that can be polled from the vast majority of IT Devices

        base_info_dict = {
            "System Management IP Address": self.ip,
            "System Name": self.baseInfo_get_sysName(),
            "System Model": self.model,
            "System Vendor": self.vendor
        }

        return base_info_dict

    def baseInfo_get_sysName(self) -> str:
        """
        """

        # Unknow vendor = No fallback to SSH, HTTP, etc.
        try:
            poller_snmp = SNMPPoller(self.snmp)
            sys_name = poller_snmp.baseInfo_get_sysName()

        # except:
            # poller_ssh = ...
            # sys_name = poller_ssh.baseInfo_get_sysName(self.ssh)

        finally:
            return sys_name

    def lldp_info_builder(self):

        lldp_info_dict = {
            "LLDP Status": "Enabled", # Just set to 'enabled' for now 
            "LLDP Local Chassis": self.lldp_get_local_chassis()
        }

        return lldp_info_dict
        
    def lldp_get_local_chassis(self) -> dict:

        try:
            poller_snmp = SNMPPoller(self.snmp)
            lldp_local_chassis = poller_snmp.lldp_get_local_chassis()

        # except:

        finally:
            return lldp_local_chassis
    
    def lldp_get_remote_list(self) -> dict:

        try:
            poller_snmp = SNMPPoller(self.snmp)
            lldp_remote = poller_snmp.lldp_get_remote_entry_list()

        # except:

        finally:
            return lldp_remote
    