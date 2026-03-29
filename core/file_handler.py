import json
from tempfile import NamedTemporaryFile
from os import replace
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
            "output": ["dir"],
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

class JsonFile:

    dir_path = ""

    def __init__(self,):

        
        # init sets path
        try:
            cfg_file = ConfigFile()
            cfg_file.validate_config()

            output_dir = Path(cfg_file.read_cfg_file("output", "dir"))

            if not output_dir.is_absolute():
                output_dir = Path(__file__).resolve().parent / output_dir

            self.dir_path = output_dir

        except FileNotFoundError as e:
            raise RuntimeError(f"[ERROR] Config file missing: {e}")
        except RuntimeError as e:
            raise RuntimeError(f"[ERROR] Invalid config: {e}")

    # Create a new json (map, topology)
    def create_json(self, file_name : str):

        file_path = Path(self.dir_path) / file_name

        file_path.parent.mkdir(parents=True, exist_ok=True)

        if file_path.exists() and file_path.is_file():
            file_path.unlink()

        file_path.touch()

    def load_data(self, file_name : str):

        file_path = Path(self.dir_path) / file_name

        if file_path.exists() and file_path.stat().st_size > 0:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def _atomic_write(self, file_name : str, data):
        file_path = Path(self.dir_path) / file_name
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=file_path.parent,
            delete=False
        ) as tmp:
            json.dump(data, tmp, indent=4)
            tmp_name = tmp.name

        replace(tmp_name, file_path)

    # fix
    def save_all(self, file_name, data):
        self._atomic_write(file_name, data)