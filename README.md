## About
IT Infrastructure mapping and documentation tool based on implemented tools used in the following published papers:

[Gerenciamento da rede: infraestrutura e monitoramento do Hospital Universitário de Santa Maria (HUSM)](https://periodicos.ufn.edu.br/index.php/disciplinarumNT/article/view/4534)

[Implementação de um Mecanismo Para Detecção de Mensagens Router Advertisement Maliciosas e Servidores DHCPv6 Falsos em Redes de Equipamentos Legados](https://sol.sbc.org.br/index.php/errc/article/view/26057)

### This is not...
... ❌ an orchestration tool;
... ❌ a vulnerability scan tool;
... ❌ a magic tool that will point out flaws in your network design.

## Requirements
* Python3
* net-snmp
* paramiko

## Easy Setup
```
python3 -m venv some_dir
cd some_dir
pip3 install paramiko
git clone https://github.com/RafaelAzambuja/NetDoc.git src
source bin/activate
cd src
mv config.ini.example config.ini
```
Edit config, then:
```
python3 main.py
```

## Technology/Protocol Support

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

## Benchmark
```
Option:
1 - Mapping
0 - Exit

Option: 1

Option:
1 - Build IT Infrastructure Documentation
0 - Return

Option: 1
Enter subnets/addresses separated by space.
Ex: 192.168.0.0/24 172.16.230.2 10.23.0.0/16:
10.10.0.0/25 192.168.200.0/24
[INFO] MAP - Mapping started.
[INFO] ICMP - Polling active hosts in 10.10.0.0/25
[INFO] ICMP - Polling active hosts in 192.168.200.0/24
[INFO] ICMP - Polling took 60.311 seconds
[INFO] SERVICES - Starting service probe
[INFO] SERVICES - Probe took 42.371 seconds
[INFO] MAP - Discovery took 102.682 seconds
[INFO] MAP - Identifying vendors.
[INFO] MAP - Vendor identification took 0.000498 seconds
[INFO] MAP - Mapping took 318.476 seconds
[INFO] Total alive hosts: 75
```





