import json
from .file_handler import JsonFile


class TopologyEngine:

    def __init__(self, map_file : dict | JsonFile):

        if isinstance(map_file, JsonFile):
            self.data = map_file.load_data()
        
        elif isinstance(map_file, dict):
            self.data = map_file


    def elect_root(self):
        stats = {}

        for category, devices in self.data.items():
            for device in devices:
                ip = device.get("Base", {}).get("System Management IP Address")
                if not ip:
                    continue

                fdb_count = len(device.get("FDB", []))
                lldp_count = 0
                lldp = device.get("LLDP", {})
                lldp_count = len(lldp.get("Remote", []))

                stats[ip] = {
                    "category": category,
                    "fdb_count": fdb_count,
                    "lldp_count": lldp_count
                }

        max_fdb = max(stats.items(), key=lambda x: x[1]["fdb_count"], default=None)
        max_lldp = max(stats.items(), key=lambda x: x[1]["lldp_count"], default=None)

        return stats, max_fdb, max_lldp

    def analyze_link(self):
        pass

    def build_topology(self):
        stats, max_fdb, max_lldp = self.elect_root()

        if max_fdb[1]['fdb_count'] > 0:
            root_ip = max_fdb[0]
        
        elif max_lldp[1]['lldp_count'] > 0:
            root_ip = max_lldp[0]

        #else:
        #    pass


        #{
        #   "Host": "host_ip",
        #   "Neighbors": [
        #       {
        #           "Neighbor": "neighbor_ip_or_mac",
        #           "Local Port": "Local_port",
        #           "Remote Port": "Remote_port"
        #       }
        #   ]
        #}


        for category, devices in self.data.items():
            for device in devices:
                if root_ip == device.get("Base", {}).get("System Management IP Address"):
                    neighbors_lldp = device.get("LLDP", {}).get('Remote', [])
                    neighbors_fdb = device.get("FDB", [])

                    n_count = 0
                    for lldp_neighbor in neighbors_lldp:
                        n_count += 1
                        print(f"Neighbor {n_count}:")
                        print(f"Remote Host: {lldp_neighbor['Neighbor']['Remote Host']}")
                        print(f"Local port: {lldp_neighbor['Local Port']}")
                        print(f"Remote Port {lldp_neighbor['Neighbor']['Remote Port']}")

                    print(f"LLDP: {neighbors_lldp}\n")
                    print(neighbors_fdb)