from ..discovery.discovery_snmp import SNMPMgmt
from .base_device import BaseHost
from .cisco.cisco_base import *
from .dell.dell_base import *
from .dlink.dlink_base import *
from .hp.hp_base import *
from .hpe.hpe_base import *
from .huawei.huawei_base import *
from .tplink.tplink_base import *


def create_device(hosts: dict) -> list:

    devices = []

    for ip, services in hosts.items():

        print(f"[DEBUG] Trying to create host {ip}")

        snmp_obj = services.get("snmp")
        ssh_obj = services.get("ssh")

        device = _identify_type_vendor_model(ip, ssh_obj, snmp_obj)

        if device:
            print(
                f"[DEBUG] Created host: "
                f"Host: {ip}, "
                f"Vendor: {device.vendor}, "
                f"Model: {device.model}"
            )
            devices.append(device)

    return devices

def _identify_type_vendor_model(ip, ssh, snmp : SNMPMgmt):

    """
    """
	
    # Identify by vendor OID
    if snmp:
        match snmp.vendor_oid:

            # Cisco
            case "iso.3.6.1.4.1.9.6.1.82.24.1":
                return Cisco_SF300_24(ip, ssh, snmp)

            case "iso.3.6.1.4.1.9.6.1.82.48.1":
                return Cisco_SF300_48(ip, ssh, snmp)
            
            case "iso.3.6.1.4.1.9.6.1.83.28.2":
                return Cisco_SG300_28PP(ip, ssh, snmp)

            # HP / Comware
            case "iso.3.6.1.4.1.11.2.3.7.11.184":
                return JL381A_1920S(ip, ssh, snmp)

            # D-Link
            case "iso.3.6.1.4.1.171.10.63.6":
                return DES_3028(ip, ssh, snmp)
            
            case "iso.3.6.1.4.1.171.10.63.7":
                return DES_3028P(ip, ssh, snmp)
            
            case "iso.3.6.1.4.1.171.10.64.1":
                return DES_3526(ip, ssh, snmp)
            
            case "iso.3.6.1.4.1.171.10.64.2":
                return DES_3550(ip, ssh, snmp)

            case "iso.3.6.1.4.1.171.10.75.5.2":
                return DES_1210_28_B1(ip, ssh, snmp)

            case "iso.3.6.1.4.1.171.10.75.18.1":
                return DES_1210_28_C1(ip, ssh, snmp)

            # Dell
            case "iso.3.6.1.4.1.674.10895.3063":
                return N1524(ip, ssh, snmp)

            # Huawei
            case "iso.3.6.1.4.1.2011.2.23.406":
                return S5720_28X_LI_AC(ip, ssh, snmp)

            case "iso.3.6.1.4.1.2011.2.23.444":
                return S5720_52X_PWR_LI_AC(ip, ssh, snmp)

            # TPLINK
            case "iso.3.6.1.4.1.11863.1.1.9":
                return TL_SG5412F(ip, ssh, snmp)

            # HPE
            case "iso.3.6.1.4.1.25506.11.1.169":
                return HPE1920_48G(ip, ssh, snmp)
            
            # Generic SNMP Device
            case _:
                return BaseHost(snmp)
                #print(f"[INFO] Unknown vendor for host {snmp.agent_interface}: {vendor_oid}")
                #return None

    # Identify by SSH prompt logic    
    elif ssh:
        # SSH polling SHOULD NOT be done here.
        pass