# Requirements
* Python3
* net-snmp
* paramiko

Technology/Protocol Support:

| Protocol      | Status              |
| ------------- | -------------       |
| IPv4          | Testing Required    |
| IPv6          | Testing Required    |
| SNMP v2c      | Implemented         |
| SNMP v3       | Testing Required    |
| SSH           | Not Implemented     |
| HTTP          | Not Implemented     |

| Technology    | Status              |
| ------------- | -------------       |
| Multithread   | Needs revision      |
| GUI           | Not Implemented     |

# To do

## Mapping/Discovery
1. L2 Topology (RFC/ISO priority, fallback to vendor)
    1.1. LLDP
    1.2. FDB(dot1qTpFdbPort/dot1dTpFdbPort)
2. STP Topology

## Code Security
1. Safe Credential


# Benchmark:
ICMP Discovery:
  IPv4 Only, max_multithread = 10, /24 Network, 42 Alive hosts, No Address Input Overlap: 44.105 seconds average


