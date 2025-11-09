"""
DNS management module for pyhetznerdev
"""
import requests
from typing import Optional, Dict, Any, List


class DNSManager:
    """Manage Hetzner DNS records"""

    def __init__(self, api_token: str):
        """Initialize DNSManager with API token"""
        self.api_token = api_token
        self.base_url = "https://dns.hetzner.com/api/v1"
        self.headers = {
            "Auth-API-Token": api_token,
            "Content-Type": "application/json",
        }

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Any:
        """Make API request"""
        url = f"{self.base_url}/{endpoint}"
        
        if method == "GET":
            response = requests.get(url, headers=self.headers)
        elif method == "POST":
            response = requests.post(url, headers=self.headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=self.headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=self.headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json() if response.text else None

    def get_zones(self) -> List[Dict[str, Any]]:
        """Get all DNS zones"""
        result = self._request("GET", "zones")
        return result.get("zones", []) if result else []

    def get_zone_by_name(self, zone_name: str) -> Optional[Dict[str, Any]]:
        """Get zone by name"""
        zones = self.get_zones()
        for zone in zones:
            if zone.get("name") == zone_name:
                return zone
        return None

    def get_records(self, zone_id: str) -> List[Dict[str, Any]]:
        """Get all records for a zone"""
        result = self._request("GET", f"records?zone_id={zone_id}")
        return result.get("records", []) if result else []

    def find_record(
        self, zone_id: str, name: str, record_type: str = "A"
    ) -> Optional[Dict[str, Any]]:
        """Find a specific DNS record"""
        records = self.get_records(zone_id)
        for record in records:
            if record.get("name") == name and record.get("type") == record_type:
                return record
        return None

    def create_or_update_record(
        self,
        zone_name: str,
        record_name: str,
        ip_address: str,
        record_type: str = "A",
        ttl: int = 3600,
    ) -> Dict[str, Any]:
        """Create or update a DNS record"""
        # Get zone
        zone = self.get_zone_by_name(zone_name)
        if not zone:
            raise ValueError(f"DNS zone '{zone_name}' not found")
        
        zone_id = zone["id"]
        
        # Check if record exists
        existing_record = self.find_record(zone_id, record_name, record_type)
        
        if existing_record:
            # Update existing record
            if existing_record.get("value") != ip_address:
                data = {
                    "value": ip_address,
                    "ttl": ttl,
                    "type": record_type,
                    "name": record_name,
                    "zone_id": zone_id,
                }
                result = self._request("PUT", f"records/{existing_record['id']}", data)
                return result.get("record", existing_record)
            return existing_record
        else:
            # Create new record
            data = {
                "value": ip_address,
                "ttl": ttl,
                "type": record_type,
                "name": record_name,
                "zone_id": zone_id,
            }
            result = self._request("POST", "records", data)
            return result.get("record", {})

    def delete_record(self, record_id: str) -> None:
        """Delete a DNS record"""
        self._request("DELETE", f"records/{record_id}")

    def update_server_dns(
        self, zone_name: str, server_name: str, ip_address: str
    ) -> Optional[Dict[str, Any]]:
        """Update DNS record for a server if IP has changed"""
        try:
            return self.create_or_update_record(zone_name, server_name, ip_address)
        except Exception as e:
            # DNS is optional, so we just return None on error
            print(f"Warning: Could not update DNS: {e}")
            return None
