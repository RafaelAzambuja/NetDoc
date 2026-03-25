from core.file_handler import ConfigFile
from core.devices.factory import create_device
from .discovery.discovery_network import DiscoveryEngine


class MapEngine:
    
    def __init__(self, cfg_file : ConfigFile):
        self.cfg_file = cfg_file
        self.discovery_engine = DiscoveryEngine(self.cfg_file)
    
    def run_documentation(self):
        
        # Workflow:
        # 1. Obtain IP Address list
        # 2. Obtain dict of hosts and available services
        # 3. Create host objects, based on available services.
        # 4. Build base ID Info (Implmentation needed)
        # 5. Build base info for each host

        ip_address_list = self.discovery_engine.get_subnets()
        host_service_dict = self.discovery_engine.discover_services(ip_address_list)

        hosts = create_device(host_service_dict)

        #

        data = {}

        ip_mac_dict = {}
        for host in hosts:

            new_data = host.device_doc_decision()
            print
            if not host.host_category in data:
                data.update({host.host_category: []})

            if new_data:
                ip_mac_dict[host.ip] = {"mac": new_data["Base"]["System MAC Address"]}

            print(ip_mac_dict)

            data[host.host_category].append(new_data)

        # Round 2: Covert remote chassis (port, remote port, remote chassis by subtype) to IP Addresses (by mac previously obtained) and interface names, if possible
        # Build FDB

        print(data)
        return hosts
    
  