"""
Server management module for pyhetznerdev
"""
from datetime import datetime, timedelta
from typing import Optional, List
from hcloud import Client
from hcloud.servers.domain import Server
from hcloud.images.domain import Image
from hcloud.server_types.domain import ServerType
from hcloud.locations.domain import Location
from hcloud.floating_ips.domain import FloatingIP
from hcloud.actions.domain import Action
import time


class ServerManager:
    """Manage Hetzner Cloud servers for development"""

    def __init__(self, api_token: str):
        """Initialize ServerManager with API token"""
        self.client = Client(token=api_token)

    def find_snapshot(self, name_pattern: str) -> Optional[Image]:
        """Find a snapshot by name pattern"""
        images = self.client.images.get_all(type="snapshot")
        for image in images:
            if name_pattern in image.description or name_pattern in (image.name or ""):
                return image
        return None

    def is_snapshot_outdated(self, snapshot: Image, max_age_days: int = 30) -> bool:
        """Check if snapshot is older than max_age_days"""
        if not snapshot.created:
            return True
        
        snapshot_age = datetime.now(snapshot.created.tzinfo) - snapshot.created
        return snapshot_age > timedelta(days=max_age_days)

    def create_snapshot(self, server: Server, description: str) -> Image:
        """Create a snapshot from a server"""
        # Create snapshot
        response = server.create_image(description=description, type="snapshot")
        action = response.action
        image = response.image
        
        # Wait for snapshot to complete
        action.wait_until_finished()
        
        return image

    def find_or_create_floating_ip(self, ip_address: Optional[str] = None, 
                                    location: Optional[str] = None) -> FloatingIP:
        """Find existing floating IP or create a new one"""
        if ip_address:
            # Try to find existing IP
            ips = self.client.floating_ips.get_all()
            for ip in ips:
                if ip.ip == ip_address:
                    return ip
            raise ValueError(f"Floating IP {ip_address} not found")
        
        # Create new floating IP
        if not location:
            location = "nbg1"
        
        response = self.client.floating_ips.create(
            type="ipv4",
            description="Development server IP",
            home_location=Location(name=location)
        )
        return response.floating_ip

    def create_server(
        self,
        name: str,
        server_type: str = "cx11",
        location: str = "nbg1",
        image: Optional[str] = None,
        snapshot_name: Optional[str] = None,
        floating_ip: Optional[str] = None,
        ssh_keys: Optional[List[str]] = None,
        user_data: Optional[str] = None,
    ) -> Server:
        """Create a new server"""
        
        # Determine image to use
        image_obj = None
        if snapshot_name:
            # Try to use snapshot
            image_obj = self.find_snapshot(snapshot_name)
            if not image_obj:
                raise ValueError(f"Snapshot '{snapshot_name}' not found")
        elif image:
            image_obj = image
        else:
            image_obj = "ubuntu-22.04"
        
        # Get SSH keys if specified
        ssh_key_objects = []
        if ssh_keys:
            for key_name in ssh_keys:
                key = self.client.ssh_keys.get_by_name(key_name)
                if key:
                    ssh_key_objects.append(key)
        
        # Create server
        response = self.client.servers.create(
            name=name,
            server_type=ServerType(name=server_type),
            image=image_obj,
            location=Location(name=location),
            ssh_keys=ssh_key_objects if ssh_key_objects else None,
            user_data=user_data,
        )
        
        server = response.server
        action = response.action
        
        # Wait for server to be created
        action.wait_until_finished()
        
        # Attach floating IP if specified
        if floating_ip:
            fip = self.find_or_create_floating_ip(floating_ip)
            fip.assign(server).wait_until_finished()
        
        # Refresh server to get updated info
        server = self.client.servers.get_by_id(server.id)
        
        return server

    def delete_server(
        self,
        server_name: str,
        keep_floating_ip: bool = True,
        delete_volumes: bool = False,
    ) -> None:
        """Delete a server"""
        server = self.client.servers.get_by_name(server_name)
        if not server:
            raise ValueError(f"Server '{server_name}' not found")
        
        # Unassign floating IPs if keeping them
        if keep_floating_ip:
            # Refresh server to get floating IPs
            server = self.client.servers.get_by_id(server.id)
            floating_ips = self.client.floating_ips.get_all()
            for fip in floating_ips:
                if fip.server and fip.server.id == server.id:
                    fip.unassign().wait_until_finished()
        
        # Delete server
        response = server.delete()
        if response.action:
            response.action.wait_until_finished()

    def update_server_and_snapshot(
        self,
        server_name: str,
        snapshot_description: str,
        old_snapshot: Optional[Image] = None,
    ) -> Image:
        """Update server packages and create/replace snapshot"""
        server = self.client.servers.get_by_name(server_name)
        if not server:
            raise ValueError(f"Server '{server_name}' not found")
        
        # Power off server for snapshot
        if server.status == "running":
            server.power_off().wait_until_finished()
            # Give it a moment to fully shut down
            time.sleep(5)
        
        # Create new snapshot
        new_snapshot = self.create_snapshot(server, snapshot_description)
        
        # Delete old snapshot if provided
        if old_snapshot:
            old_snapshot.delete()
        
        # Power server back on
        server.power_on().wait_until_finished()
        
        return new_snapshot

    def get_server(self, name: str) -> Optional[Server]:
        """Get server by name"""
        return self.client.servers.get_by_name(name)

    def list_servers(self) -> List[Server]:
        """List all servers"""
        return self.client.servers.get_all()

    def list_snapshots(self) -> List[Image]:
        """List all snapshots"""
        return self.client.images.get_all(type="snapshot")

    def list_floating_ips(self) -> List[FloatingIP]:
        """List all floating IPs"""
        return self.client.floating_ips.get_all()
