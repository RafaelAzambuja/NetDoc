import json
from .file_handler import JsonFile


class TopologyEngine:

    def __init__(self, map_file : dict | JsonFile):

        if isinstance(map_file, JsonFile):
            self.data = map_file.load_data()
        
        elif isinstance(map_file, dict):
            self.data = map_file


    def analyze_devices(self):
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

    def build_topology(self):
        stats, max_fdb, max_lldp = self.analyze_devices()

        # Network root?
        print("Device with most FDB:", max_fdb)
        print("Device with most LLDP:", max_lldp)
