from pathlib import Path
from configparser import ConfigParser, NoSectionError, NoOptionError

# Yes. We are trading code security and perfomance for sanity and simplicity.
# No Schemas and no thorough validation.

class ConfigFile:
    def __init__(self):
        self.cfg_file_path = Path(__file__).resolve().parent.parent / "config.ini"

        if not self.cfg_file_path.exists():
            raise FileNotFoundError(f"[WARN] Could not find config file: {self.cfg_file_path}")

        self.cfg_file = ConfigParser()
        self.cfg_file.read(self.cfg_file_path)

    def validate_config(self):
        '''
        Validate the structure of config.ini
        Raises RuntimeError if sections or keys are missing.
        '''

        if not self.cfg_file.sections():
            raise RuntimeError("[WARN] Config file is empty or unreadable")

        structure = {
            "output": ["json", "csv"],
            "icmp": ["timeout"],
            "service": ["snmp", "ssh", "http"],
            "snmp": ["timeout", "retries"],
            "snmpv2c": ["use_v2c", "communities"],
            "snmpv3": ["use_v3", "user", "security_level", "auth_option",
                       "auth_password", "priv_option", "priv_password"],
            "options": ["max_threads"]
        }

        missing_sections = []
        missing_keys = {}

        for section, keys in structure.items():
            if not self.cfg_file.has_section(section):
                missing_sections.append(section)
            else:
                for key in keys:
                    if not self.cfg_file.has_option(section, key):
                        missing_keys.setdefault(section, []).append(key)

        if missing_sections:
            raise RuntimeError(f"[WARN] Missing sections: {missing_sections}")
        if missing_keys:
            raise RuntimeError(f"[WARN] Missing keys: {missing_keys}")

    def read_cfg_file(self, section: str, key: str, fallback=None) -> str:
        try:
            return self.cfg_file.get(section, key, fallback=fallback)
        except (NoSectionError, NoOptionError) as e:
            if fallback is not None:
                return fallback
            raise KeyError(f"[WARN] Missing '{key}' in section '{section}'") from e
        except ValueError as e:
            raise ValueError(f"[WARN] Invalid value for '{key}' in section '{section}': {e}")
