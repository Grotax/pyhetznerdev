"""
Configuration management for pyhetznerdev
"""
import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any


class Config:
    """Manage configuration for pyhetznerdev"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._default_config_path()
        self.data = self._load_config()

    def _default_config_path(self) -> str:
        """Get the default config file path"""
        home = Path.home()
        config_dir = home / ".config" / "pyhetznerdev"
        config_dir.mkdir(parents=True, exist_ok=True)
        return str(config_dir / "config.yaml")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                return yaml.safe_load(f) or {}
        return {}

    def save(self) -> None:
        """Save configuration to file"""
        with open(self.config_path, "w") as f:
            yaml.dump(self.data, f, default_flow_style=False)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value"""
        self.data[key] = value

    def get_api_token(self) -> Optional[str]:
        """Get Hetzner API token from config or environment"""
        return self.get("hetzner_api_token") or os.getenv("HETZNER_API_TOKEN")

    def get_dns_api_token(self) -> Optional[str]:
        """Get Hetzner DNS API token from config or environment (for Cloud Console DNS)"""
        # Check for DNS-specific token first, fall back to main API token
        return self.get("hetzner_dns_api_token") or os.getenv("HETZNER_DNS_API_TOKEN") or self.get_api_token()

    def get_snapshot_max_age_days(self) -> int:
        """Get maximum snapshot age in days before refresh"""
        return self.get("snapshot_max_age_days", 30)

    def get_default_server_type(self) -> str:
        """Get default server type"""
        return self.get("default_server_type", "cx11")

    def get_default_location(self) -> str:
        """Get default server location"""
        return self.get("default_location", "nbg1")

    def get_default_image(self) -> str:
        """Get default server image"""
        return self.get("default_image", "ubuntu-22.04")
