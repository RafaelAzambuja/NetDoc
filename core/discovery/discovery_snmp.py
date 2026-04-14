from core.file_handler import ConfigFile
from subprocess import run

class SNMPMgmt:
    """
    """

    def __init__(self, snmp_agent_interface: str, cfg_file: ConfigFile):
        """
        """

        # Sim, dados sensíveis expostos na classe. Depois verificar maneira mais segura e eficiente

        self.agent_interface = snmp_agent_interface
        self.snmp_timeout = str(cfg_file.read_cfg_file("snmp", "timeout", fallback="3"))
        self.snmp_retries = str(cfg_file.read_cfg_file("snmp", "retries", fallback="1"))
        self.get_command = None
        self.getnext_command = None
        self.walk_command = None
        self.sec_level = str(cfg_file.read_cfg_file("snmpv3", "security_level"))
        self.snmp_user = str(cfg_file.read_cfg_file("snmpv3", "user"))
        self.auth_opt = str(cfg_file.read_cfg_file("snmpv3", "auth_option"))
        self.auth_pass = str(cfg_file.read_cfg_file("snmpv3", "auth_password"))
        self.priv_opt = str(cfg_file.read_cfg_file("snmpv3", "priv_option"))
        self.priv_pass = str(cfg_file.read_cfg_file("snmpv3", "priv_password"))
        self.use_v3 = str(cfg_file.read_cfg_file("snmpv3", "use_v3").lower())
        self.use_v2c = str(cfg_file.read_cfg_file("snmpv2c", "use_v2c").lower())
        self.communities_raw = cfg_file.read_cfg_file("snmpv2c", "communities")

    def connect(self) -> bool:
        '''

        '''
        # SNMPv3
        if self.use_v3 == "true":

            base_cmd = ["snmpget",
                        "v3",
                        "-r", self.snmp_retries,
                        "-t", self.snmp_timeout,
                        "-l", self.sec_level,
                        "-u", self.snmp_user,
                        "-a", self.auth_opt,
                        "-A", self.auth_pass,
                        "-x", self.priv_opt,
                        "-X", self.priv_pass,
                        self.agent_interface
                    ]

            output = run(base_cmd + ["1.3.6.1.2.1.1.2.0"], capture_output=True, text=True) # add timeout?

            if self.validate_snmp(output.stdout, output.returncode):

                self.version = "v3"
                self.vendor_oid = output.stdout.split()[3]

                self._prepare_commands(base_cmd)

                return True

        # SNMPv2c
        if self.use_v2c == "true":
            communities = [c.strip() for c in self.communities_raw.split(",") if c.strip()]

            for community in communities:
                base_cmd = [
                    "snmpget",
                    "-v2c",
                    "-r", self.snmp_retries,
                    "-t", self.snmp_timeout,
                    "-c", community,
                    self.agent_interface
                ]

                output = run(base_cmd + ["1.3.6.1.2.1.1.2.0"], capture_output=True, text=True) # add timeout?

                if self.validate_snmp(output.stdout, output.returncode):

                    self.version = "v2c"
                    self.vendor_oid = output.stdout.split()[3]

                    self._prepare_commands(base_cmd)

                    return True

        return False

    def validate_snmp(self, response: str, return_code: int) -> bool:

        invalid_snmp_strings = (
        "No Such Object",
        "No Such Instance",
        "Timeout"
    )

        if return_code != 0 or not response:
            return False

        return not any(err in response for err in invalid_snmp_strings)

    def _prepare_commands(self, base_cmd: list[str]):
        self.get_command = base_cmd.copy()

        self.getnext_command = base_cmd.copy()
        self.getnext_command[0] = "snmpgetnext"

        self.walk_command = base_cmd.copy()
        self.walk_command[0] = "snmpwalk"
        self.walk_command.insert(2, "-Cc")

    def _parse_snmp_line(self, line: str) -> tuple[str, str, str]:

        try:
            oid_part, value_part = line.split(" = ", 1)

            # Case: TYPE exists
            if ": " in value_part:
                value_type, value = value_part.split(": ", 1)
            else:
                # Case: no TYPE (e.g. "", No Such Object, etc.)
                value_type = None
                value = value_part

            # Normalize value (optional but recommended)
            value = value.strip().strip('"')

            return oid_part.strip(), value, value_type

        except ValueError:
            return None, None, None
        
    def snmpget(self, oid: str) -> tuple[str, str]:
        '''
        Perform SNMP GetRequest.

        Args:
            oid (str): Object Identifier.

        Returns:
            tuple[Optional[str], Optional[str]]:
                (value, value_type) if successful,
                (None, None) otherwise.

        Example output:
            iso.3.6.1.2.1.1.5.0 = STRING: "hostname"
        '''


        command = self.get_command + [oid]
        output = run(command, capture_output=True, text=True)

        if self.validate_snmp(output.stdout, output.returncode):
            line = output.stdout.strip()
            _, value, value_type = self._parse_snmp_line(line)
            return value, value_type

        return None, None

    def snmpgetnext(self, oid: str) -> tuple[str, str]:
        '''
        Perform SNMP GetNextRequest.

        Args:
            oid (str): Object Identifier.

        Returns:
            tuple[Optional[str], Optional[str]]:
                (value, value_type) if successful,
                (None, None) otherwise.
        '''

        command = self.getnext_command + [oid]
        output = run(command, capture_output=True, text=True)

        if self.validate_snmp(output.stdout, output.returncode):
            line = output.stdout.strip()
            _, value, value_type = self._parse_snmp_line(line)
            return value, value_type

        return None, None

    def snmpwalk(self, oid: str) -> list[str]:
        
        # Utilizar snmpbulkwalk?

        ''' Perform SNMP Walk.

        Args:
            oid (str): Root Object Identifier.

        Returns:
            Optional[list[str]]:
                List of response lines if successful,
                None otherwise.
        '''

        command = self.walk_command + [oid]
        output = run(command, capture_output=True, text=True)

        if self.validate_snmp(output.stdout, output.returncode):
            lines = output.stdout.strip().split('\n')
            results = []

            for line in lines:
                oid_part, value, value_type = self._parse_snmp_line(line)

                if oid_part is not None:
                    results.append({
                        "oid": oid_part,
                        "value": value,
                        "type": value_type
                    })

            return results

        return None
