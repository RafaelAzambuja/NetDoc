import ipaddress
from subprocess import call, DEVNULL
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.file_handler import ConfigFile


def _test_icmp_host(ip: str, timeout: int) -> bool:
    """
    Ping an IP address. Supports IPv4 and IPv6 on Unix-like systems.
    Returns True if host is alive, False otherwise.
    """

    ip_obj = ipaddress.ip_address(ip)

    if ip_obj.version == 4:
        # IPv4 ping
        cmd = ["ping", "-c", "1", "-W", str(timeout), ip]
    else:
        # IPv6 ping
        cmd = ["ping", "-6", "-c", "1", "-W", str(timeout), ip]

    return call(cmd, stdout=DEVNULL, stderr=DEVNULL) == 0


def poll_icmp_active_hosts(subnet: str, cfg_file: ConfigFile) -> list[str]:
    """
    Scan a subnet (IPv4 or IPv6) and return a list of active hosts using ICMP.
    """

    try:
        network = ipaddress.ip_network(subnet, strict=True)
    except ValueError:
        return []

    timeout = int(cfg_file.read_cfg_file("icmp", "timeout", fallback='1'))
    max_threads = max(
        1, min(128, int(cfg_file.get("options", "max_threads", fallback="10")))
    )

    active_hosts: list[str] = []

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {
            executor.submit(_test_icmp_host, str(ip), timeout): str(ip)
            for ip in network.hosts()
        }

        for future in as_completed(futures):
            ip = futures[future]
            try:
                if future.result():
                    active_hosts.append(ip)
            except Exception:
                continue

    return active_hosts
