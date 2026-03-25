from ..base_device import BaseHost

class TplinkBase(BaseHost):
    vendor = "TP-Link"

class TL_SG5412F(TplinkBase):
    host_category = "Switch"
    model = "TL-SG5412F"

    def lldp_info_builder(self):

        # Device does have LLDP support, but probably uses a vendor specific MIB

        lldp_info_dict = {
            "LLDP Status": "Use SSH/HTTP"
        }

        return lldp_info_dict