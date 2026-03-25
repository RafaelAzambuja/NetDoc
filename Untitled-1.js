{ 
    'Unknown'; [
        {},
        {}
    ], 
    'Switch'; [
        {
            'Base': {
                'System Management IP Address': '10.10.0.11',
                'System MAC Address': 'F0:7D:68:FF:1A:28',
                'System Name': 'ufsm-221999',
                'System Model': 'DES 3028',
                'System Vendor': 'D-Link'
            }, 'LLDP': {
                'LLDP Status': 'Enabled',
                'LLDP Local Chassis': 'F0 7D 68 FF 1A 28',
                'Remote': []
            }
        },
        {
            'Base': {
                'System Management IP Address': '10.10.0.12',
                'System MAC Address': 'E8:F7:24:CA:A1:C4',
                'System Name': 'ufsm.pm.backbone',
                'System Model': '1920-48G',
                'System Vendor': 'HPE'
            }, 'LLDP': {
                'LLDP Status': 'Enabled',
                'LLDP Local Chassis': 'E8 F7 24 CA A1 C4',
                'Remote': [
                    {
                        'Local Port': 48,
                        'Neighbor': {
                            'Remote Host': '68 4F 64 D9 0D 6C',
                            'Remote Port': 'Gi1/0/23'
                        }
                    },
                    {
                        'Local Port': 13,
                        'Neighbor': {
                            'Remote Host': 'E8 F7 24 94 4E D4',
                            'Remote Port': 'GigabitEthernet1/0/48'
                        }
                    },
                    {
                        'Local Port': 45,
                        'Neighbor': {
                            'Remote Host': 'd8:b3:70:1a:fe:a1',
                            'Remote Port': 'D8 B3 70 1A FE A1' 
                        }
                    }
                ]
            }
        }
    ]
}
