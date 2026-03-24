import time
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.file_handler import ConfigFile
from discovery.discovery_icmp import poll_icmp_active_hosts
from discovery.discovery_snmp import SNMPMgmt
# from discovery.discovery_ssh import test_ssh_on_host


class DiscoveryEngine:
    """ Network discovery engine responsible for:

    1. Collecting target subnets from the user
    2. Discovering alive hosts via ICMP
    3. Probing discovered hosts for services (SNMP, SSH, etc.)

    The engine performs ICMP scanning sequentially and service probing
    concurrently using a thread pool.
    """

    def __init__(self, cfg_file : ConfigFile):
        """ Initialize the discovery engine.

        Args:
            cfg_file (ConfigFile): Configuration file handler instance.
                Used to retrieve runtime options (e.g., max_threads).

        Notes:
            The number of worker threads is clamped between 1 and 128.
        """

        self.max_threads = max(1, min(128, int(cfg_file.read_cfg_file("options", "max_threads", fallback="10"))))
        self.cfg_file = cfg_file

    def get_subnets(self, subnets_input = None) -> list[str]:
        
        """ Prompt the user to enter one or more IPv4 addresses and/or subnets.

        The user is repeatedly prompted until valid input is provided.
        Entries must be whitespace-separated and may be either:

        - IPv4 address (e.g., 192.168.1.10)
        - IPv4 subnet in CIDR notation (e.g., 192.168.1.0/24)

        Example:
            192.168.0.0/24 172.16.230.2 10.23.0.0/16

        Returns:
            list[str]: A list of validated IPv4 networks in CIDR notation.
                       Single IP addresses are normalized to /32 networks.

        Raises:
            No exceptions are propagated. Validation errors are caught
            and the user is prompted again.
        """

        while True:
            if not subnets_input:
                subnets_input = input(
                    "Enter subnets/addresses separated by space.\n"
                    "Ex: 192.168.0.0/24 172.16.230.2 10.23.0.0/16:\n"
                ).strip()

            try:
                return self._validate_subnets(subnets_input)
            
            except ValueError as e:
                print(f"Error: {e}")

    def _validate_subnets(self, ip_address_list: str) -> list[str]:
        """
        Validate a whitespace-separated string of IPv4 or IPv6 addresses/subnets.

        Each entry may be:
            - A valid IPv4 or IPv6 address
            - A valid IPv4 or IPv6 network in CIDR notation (strict mode)

        Args:
            ip_address_list (str): Whitespace-separated IP addresses or subnets.

        Returns:
            list[str]: Normalized networks in CIDR notation.
                    Single IPs are converted to /32 (IPv4) or /128 (IPv6) networks.

        Raises:
            ValueError: If any entry is not a valid IP address or subnet.
        """

        # Time complexity: O(n log n)
        # start = time.perf_counter()
        ipv4_networks = []
        ipv6_networks = []

        for entry in ip_address_list.split():
            entry = entry.strip()
            if not entry:
                continue

            try:
                network = ipaddress.ip_network(entry, strict=True)
            except ValueError:
                try:
                    ip = ipaddress.ip_address(entry)
                    network = ipaddress.ip_network(f"{ip}/{ip.max_prefixlen}", strict=True)
                except ValueError:
                    raise ValueError(f"Invalid IPv4 or IPv6 address/subnet: {entry}")

            if network.version == 4:
                ipv4_networks.append(network)
            else:
                ipv6_networks.append(network)

        collapsed_v4 = list(ipaddress.collapse_addresses(ipv4_networks))
        collapsed_v6 = list(ipaddress.collapse_addresses(ipv6_networks))

        # elapsed = time.perf_counter() - start
        # print(f"[DEBUG] Subnet sorting took {elapsed:.3f} seconds")

        return [str(n) for n in (collapsed_v4 + collapsed_v6)]

    def discover_services(self, ip_addr_list : list[str]):

        hosts = self._icmp_phase(ip_addr_list)

        if not hosts:
            print("[INFO] No active hosts found.")
            return {}

        self._service_probe_phase(hosts)

        return hosts

    def _icmp_phase(self, subnets: list[str]) -> dict[str, dict]:

        hosts: dict[str, dict] = {}
        start = time.perf_counter()

        for subnet in subnets:
            print(f"[INFO] ICMP - Polling active hosts in {subnet}")
            alive_hosts = poll_icmp_active_hosts(subnet, self.cfg_file)

            for ip in alive_hosts:
                hosts[ip] = {
                    "icmp": True,
                    "snmp": None,
                    "ssh": None,
                    "http": None,
                }

        elapsed = time.perf_counter() - start
        #print(f"[DEBUG] Alive hosts in {subnet}: {alive_hosts}")
        print(f"[INFO] ICMP polling took {elapsed:.3f} seconds")

        return hosts

    def _probe_snmp(self, ip: str):
        print(f"[DEBUG] Trying SNMP on {ip}")
        snmp = SNMPMgmt(ip, self.cfg_file)

        if snmp.connect():
            print(f"[DEBUG] SNMP OK on {ip}")
            return snmp

        print(f"[DEBUG] SNMP FAILED on {ip}")
        return None

    def _service_probe_phase(self, hosts: dict[str, dict]) -> None:

        print("[INFO] Probing services (SNMP / SSH / HTTP)")
        start = time.perf_counter()

        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = {}

            for ip in hosts.keys():

                if self.cfg_file.read_cfg_file("service", "snmp"):
                    futures[
                        executor.submit(self._probe_snmp, ip)
                    ] = ("snmp", ip)

                # Future extensions:
                # SSH
                # futures[
                #     executor.submit(test_ssh_on_host, ip, self.cfg)
                # ] = ("ssh", ip)

                # HTTP
                # futures[
                #     executor.submit(test_http_on_host, ip, self.cfg)
                # ] = ("http", ip)

            for future in as_completed(futures):
                service, ip = futures[future]

                try:
                    result = future.result()

                    if result:
                        hosts[ip][service] = result
                except Exception as e:
                    print(f"[ERROR] {service} probe failed on {ip}: {e}")

        elapsed = time.perf_counter() - start
        print(f"[INFO] Service probing took {elapsed:.3f} seconds")
