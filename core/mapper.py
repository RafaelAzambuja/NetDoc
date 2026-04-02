import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.file_handler import ConfigFile, JsonFile
from core.devices.factory import create_device
from core.topology import *
from .discovery.discovery_network import DiscoveryEngine


class MapEngine:
    
    def __init__(self, cfg_file : ConfigFile):
        self.max_threads = max(1, min(128, int(cfg_file.read_cfg_file("options", "max_threads", fallback="10"))))
        self.discovery_engine = DiscoveryEngine(cfg_file)

    def process_host(self, host):
        new_data = host.device_doc_decision()
        mac = None

        if new_data:
            mac = new_data["Base"]["System MAC Address"]

        return host.host_category, host.ip, new_data, mac

    def process_fdb(self, host, ip, mac):

        if ip == host.ip:
            return None

        # Build vlan list everytime. Expensive
        result = host.fdb_lookup(mac)
        if not result:
            return None

        return {
            "host_ip": host.ip,
            "IP": ip,
            "MAC": mac,
            "VLAN": result[0],
            "Local Port": result[1]
        }

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


        # ------------------------------------------
        # Build Doc and Collect System MAC Address
        # ------------------------------------------

        data = {}
        ip_mac_dict = {}

        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = [executor.submit(self.process_host, host) for host in hosts]

            for future in as_completed(futures):
                category, ip, new_data, mac = future.result()

                if category not in data:
                    data[category] = []

                if mac:
                    ip_mac_dict[ip] = mac

                data[category].append(new_data)

        # ----------
        # Build FDB
        # ----------

        host_data = {}

        for host in hosts:
            host_data_list = data.get(host.host_category, [])
            for d in host_data_list:
                ip = d.get("Base", {}).get("System Management IP Address")
                if ip:
                    host_data[ip] = d
                    if "FDB" not in d:
                        d["FDB"] = []

        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = []

            for host in hosts:
                if host.ip not in host_data:
                    continue

                for ip, mac in ip_mac_dict.items():
                    futures.append(executor.submit(self.process_fdb, host, ip, mac))

            for future in as_completed(futures):
                result = future.result()
                if not result:
                    continue

                host_ip = result.pop("host_ip")
                host_data[host_ip]["FDB"].append(result)


        print(f"[INFO] MAP - Mapping took {time.perf_counter() - start_all:.3f} seconds")
        json_out = JsonFile()
        # Dumb. Fix
        json_out.create_json("map.json")
        json_out.save_all("map.json", data)
        #print(data)

        topology_engine = TopologyEngine(data)

        topology_engine.build_topology()

        return hosts
    
  