"""
DNS management module for pyhetznerdev
"""
from typing import Optional, Dict, Any, List
from hcloud import Client
from hcloud.primary_ips.domain import PrimaryIP


class DNSManager:
    """Manage Hetzner Cloud DNS records (via Cloud Console)"""

    def __init__(self, api_token: str):
        """Initialize DNSManager with API token"""
        self.client = Client(token=api_token)

    def get_primary_ip_by_ip(self, ip_address: str) -> Optional[PrimaryIP]:
        """Get primary IP resource by IP address"""
        primary_ips = self.client.primary_ips.get_all()
        for primary_ip in primary_ips:
            if primary_ip.ip == ip_address:
                return primary_ip
        return None

    def update_dns_ptr(
        self,
        ip_address: str,
        dns_ptr: str,
    ) -> Optional[Dict[str, Any]]:
        """Update DNS PTR record for an IP address"""
        try:
            # Find the primary IP resource
            primary_ip = self.get_primary_ip_by_ip(ip_address)
            
            if not primary_ip:
                print(f"Warning: Primary IP {ip_address} not found in cloud console")
                return None
            
            # Update DNS PTR
            self.client.primary_ips.change_dns_ptr(
                primary_ip,
                dns_ptr=dns_ptr,
                ip=ip_address
            )
            
            return {"ip": ip_address, "dns_ptr": dns_ptr}
            
        except Exception as e:
            print(f"Warning: Could not update DNS PTR: {e}")
            return None

    def update_server_dns(
        self, zone_name: str, server_name: str, ip_address: str
    ) -> Optional[Dict[str, Any]]:
        """Update DNS PTR record for a server"""
        # Construct FQDN
        fqdn = f"{server_name}.{zone_name}"
        
        try:
            return self.update_dns_ptr(ip_address, fqdn)
        except Exception as e:
            # DNS is optional, so we just return None on error
            print(f"Warning: Could not update DNS: {e}")
            return None

