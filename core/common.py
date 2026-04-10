import re


def convert_hex_to_oid(hex_string) -> str:

    '''
		Converter MAC no formato XX:XX:XX:XX:XX:XX | xx:xx:xx:xx:xx:xx | xxxx-xxxx-xxxx | xx-xx-xx-xx-xx-xx para decimal no formato de OID.
	'''
    
    mac_regex = r'([0-9a-fA-F]{2})[:-]([0-9a-fA-F]{2})[:-]([0-9a-fA-F]{2})[:-]([0-9a-fA-F]{2})[:-]([0-9a-fA-F]{2})[:-]([0-9a-fA-F]{2})'

    match = re.match(mac_regex, hex_string)

    if match:
        parts = match.groups()
        decimal_parts = [str(int(part, 16)) for part in parts]
        mac_oid = '.'.join(decimal_parts)
        return "." + mac_oid
    else:
        raise ValueError("Formato de MAC Inválido.")


def convert_hex_to_utf8(hex_string: str) -> str:
    """
    """

    hex_string = hex_string.replace(" ", "").replace("\n", "")
    return bytes.fromhex(hex_string).decode("utf-8")

def convert_port_list(port_list: list) -> list:
    res = ""
    offset = 1
    for j in port_list:
        res += str(bin(int(j, 16))[2:].zfill(8))+" "

    res = res.split()

    port_index_vlan = ""
    for j in res:
        for i in range(0, len(j)):
            if j[i] == '1':
                port_index_vlan += str(int(i) + offset)+" "
        offset += 8

    return port_index_vlan.split()