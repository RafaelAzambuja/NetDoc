# About
IT Infrastructure mapping and documentation tool based on implemented tools used in the following published papers:

[Gerenciamento da rede: infraestrutura e monitoramento do Hospital Universitário de Santa Maria (HUSM)](https://periodicos.ufn.edu.br/index.php/disciplinarumNT/article/view/4534)

[Implementação de um Mecanismo Para Detecção de Mensagens Router Advertisement Maliciosas e Servidores DHCPv6 Falsos em Redes de Equipamentos Legados](https://sol.sbc.org.br/index.php/errc/article/view/26057)

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

# Benchmark:
ICMP Discovery:
  IPv4 Only, max_multithread = 10, /24 Network, 42 Alive hosts, No Address Input Overlap: 44.105 seconds average

# Notes:
## Easy Setup
```
python3 -m venv some_dir
cd some_dir
pip3 install paramiko
git clone https://github.com/RafaelAzambuja/NetDoc.git src
source bin/activate
cd src
python3 main.py
```

## Branches
1. Create your own branches following the syntax: dev-"your name"
2. old-main is just for reference, code is currently being refactored

## New vendors and device models
1. Just extend Classes Host_Device, Switch, ..., as needed

# To do

## Mapping/Discovery
1. L2 Topology (RFC/ISO priority, fallback to vendor)
    1.1. LLDP
    1.2. FDB(dot1qTpFdbPort/dot1dTpFdbPort)
2. STP Topology

## Code Security
1. Safe Credential





