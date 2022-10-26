import os
from schema import Schema, And, Optional, Use
import ipaddress

settings_schema = Schema(
    {
        "app": {
            "loglevel": lambda s: s
            in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            "log_to_file": bool,
            "logfile_path": lambda p: os.path.exists(p),
        },
        "schedule": {
            "frequency_in_minutes": int,
            "countdown_warning": int,
        },
        "server": {
            "port": int,
            "ip": Use(ipaddress.IPv4Address),
        },
        "backup": {
            "active_only": bool,
            "in_static_dir": bool,
            "static_dir": lambda p: os.path.exists(p),
        },
    },
    ignore_extra_keys=True,
)
