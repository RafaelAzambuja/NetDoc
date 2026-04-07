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

    def rename_this_funtion(self, neighbors_lldp, neighbors_fdb):

            n_count = 0
            depth = 0

            for lldp_neighbor in neighbors_lldp:
                n_count += 1
                print(f"Neighbor {n_count}:")
                print(f"Remote Host ID: {lldp_neighbor['Neighbor']['Remote Host']}")
                print(f"Remote Host IP: {}")
                print(f"Local port: {lldp_neighbor['Local Port']}")
                print(f"Remote Port {lldp_neighbor['Neighbor']['Remote Port']}")

                self.rename_this_funtion()

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

        # 1. Find root.
        # 2. Place root.
        # 3. place root's neighbors.
        # 4. Place root's neighbors' neighbors.
        # 5. When finished, restart the list ignoring already placed devices

        devices_already = []
        for category, devices in self.data.items():
            for device in devices:
                if device in devices_already:
                    continue

                if root_ip == device.get("Base", {}).get("System Management IP Address"):
                    neighbors_lldp = device.get("LLDP", {}).get('Remote', [])
                    neighbors_fdb = device.get("FDB", [])

                    devices_already.extend(self.rename_this_funtion(root_ip ,neighbors_lldp, neighbors_fdb))
