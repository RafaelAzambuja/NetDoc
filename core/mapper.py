import time
from core.file_handler import ConfigFile, JsonFile
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
        # 4. Build base info for each host
        # 5. Build topology info

        ip_address_list = self.discovery_engine.get_subnets()

        start_all = time.perf_counter()
        print("[INFO] MAP - Mapping started.")

        # ----------
        # DISCOVERY
        # ----------

        start_discovery = time.perf_counter()
        host_service_dict = self.discovery_engine.discover_services(ip_address_list)
        print(f"[INFO] MAP - Discovery took {time.perf_counter() - start_discovery:.3f} seconds")

        # ----------------------
        # DEVICE CATEGORIZATION
        # ----------------------

        print("[INFO] MAP - Identifying vendors.")
        start_identify = time.perf_counter()
        hosts = create_device(host_service_dict)
        print(f"[INFO] MAP - Vendor identification took {time.perf_counter() - start_identify:.6f} seconds")

        data = {}

        # Possible Multithread below
        ip_mac_dict = {}
        for host in hosts:

            new_data = host.device_doc_decision()

            if not host.host_category in data:
                data.update({host.host_category: []})

            if new_data:
                ip_mac_dict[host.ip] = new_data["Base"]["System MAC Address"]

            data[host.host_category].append(new_data)

        # Possible Multithread above

        # Round 2: Covert remote chassis (port, remote port, remote chassis by subtype) to IP Addresses (by mac previously obtained) and interface names, if possible
        # Build FDB

        for host in hosts:
            host_data_list = data.get(host.host_category, [])
            
            host_data = next((d for d in host_data_list if d.get("Base", {}).get("System Management IP Address") == host.ip), None)
            
            if host_data is None:
                continue

            if "FDB" not in host_data:
                host_data["FDB"] = []

            for ip, mac in ip_mac_dict.items():
                if ip == host.ip:
                    continue

                result = host.fdb_lookup(mac)
                if result:
                    host_data["FDB"].append({
                        "IP": ip,
                        "MAC": mac,
                        "Local Port": result
                    })

        print(f"[INFO] MAP - Mapping took {time.perf_counter() - start_all:.3f} seconds")
        json_out = JsonFile()
        # Dumb. Fix
        json_out.create_json("map.json")
        json_out.save_all("map.json", data)
        #print(data)
        return hosts
    
  