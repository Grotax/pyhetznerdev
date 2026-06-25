"""
Command-line interface for pyhetznerdev
"""
import click
import sys
from typing import Optional
from .config import Config
from .server import ServerManager
from .dns import DNSManager


@click.group()
@click.version_option(version="0.1.0")
@click.option("--config", "-c", help="Path to config file")
@click.pass_context
def main(ctx, config):
    """pyhetznerdev - Manage Hetzner Cloud development servers"""
    ctx.ensure_object(dict)
    ctx.obj["config"] = Config(config)


@main.command()
@click.argument("name")
@click.option("--server-type", "-t", default=None, help="Server type (e.g., cx11, cx21)")
@click.option("--location", "-l", default=None, help="Server location (e.g., nbg1, fsn1)")
@click.option("--image", "-i", default=None, help="Base image (e.g., ubuntu-22.04)")
@click.option("--snapshot", "-s", default=None, help="Snapshot name to use")
@click.option("--floating-ip", "-f", default=None, help="Existing floating IP address")
@click.option("--ssh-key", "-k", multiple=True, help="SSH key name (can be used multiple times)")
@click.option("--dns-zone", "-d", default=None, help="DNS zone for automatic record creation")
@click.option(
    "--update-snapshot/--no-update-snapshot",
    default=True,
    help="Check and update snapshot if outdated",
)
@click.pass_context
def create(
    ctx,
    name,
    server_type,
    location,
    image,
    snapshot,
    floating_ip,
    ssh_key,
    dns_zone,
    update_snapshot,
):
    """Create a new development server"""
    config = ctx.obj["config"]
    
    # Get API token
    api_token = config.get_api_token()
    if not api_token:
        click.echo("Error: HETZNER_API_TOKEN not set. Set it in config or environment.", err=True)
        sys.exit(1)
    
    # Use defaults from config if not specified
    server_type = server_type or config.get_default_server_type()
    location = location or config.get_default_location()
    
    # Initialize server manager
    mgr = ServerManager(api_token)
    
    # Handle snapshot logic
    snapshot_obj = None
    snapshot_name_to_use = snapshot
    
    if snapshot:
        click.echo(f"Looking for snapshot: {snapshot}")
        snapshot_obj = mgr.find_snapshot(snapshot)
        
        if not snapshot_obj:
            click.echo(f"Warning: Snapshot '{snapshot}' not found. Using base image instead.")
            image = image or config.get_default_image()
        elif update_snapshot:
            # Check if snapshot is outdated
            max_age = config.get_snapshot_max_age_days()
            if mgr.is_snapshot_outdated(snapshot_obj, max_age):
                click.echo(f"Snapshot is older than {max_age} days.")
                if click.confirm("Do you want to update it?"):
                    click.echo("Creating temporary server to update snapshot...")
                    
                    # Create temporary server from snapshot
                    temp_name = f"{name}-temp-snapshot-update"
                    temp_server = mgr.create_server(
                        name=temp_name,
                        server_type=server_type,
                        location=location,
                        image=snapshot_obj,
                    )
                    
                    click.echo("Updating snapshot...")
                    new_snapshot = mgr.update_server_and_snapshot(
                        temp_name,
                        snapshot_obj.description or snapshot,
                        old_snapshot=snapshot_obj,
                    )
                    
                    click.echo("Cleaning up temporary server...")
                    mgr.delete_server(temp_name, keep_floating_ip=False)
                    
                    snapshot_obj = new_snapshot
                    click.echo(f"Snapshot updated: {new_snapshot.id}")
    else:
        # No snapshot specified, use image
        image = image or config.get_default_image()
    
    # Create the server
    click.echo(f"Creating server '{name}'...")
    click.echo(f"  Type: {server_type}")
    click.echo(f"  Location: {location}")
    if snapshot_obj:
        click.echo(f"  Snapshot: {snapshot_obj.description or snapshot_obj.id}")
    else:
        click.echo(f"  Image: {image}")
    if floating_ip:
        click.echo(f"  Floating IP: {floating_ip}")
    
    try:
        server = mgr.create_server(
            name=name,
            server_type=server_type,
            location=location,
            image=image if not snapshot_obj else snapshot_obj,
            floating_ip=floating_ip,
            ssh_keys=list(ssh_key) if ssh_key else None,
        )
        
        click.echo(f"\n✓ Server created successfully!")
        click.echo(f"  ID: {server.id}")
        click.echo(f"  Name: {server.name}")
        click.echo(f"  Status: {server.status}")
        
        # Get IP address
        if server.public_net.ipv4:
            ip_address = server.public_net.ipv4.ip
            click.echo(f"  IPv4: {ip_address}")
            
            # Update DNS if zone specified
            if dns_zone:
                dns_token = config.get_dns_api_token()
                if dns_token:
                    click.echo(f"\nUpdating DNS PTR record for '{dns_zone}'...")
                    dns_mgr = DNSManager(dns_token)
                    try:
                        result = dns_mgr.update_server_dns(dns_zone, name, ip_address)
                        if result:
                            click.echo(f"✓ DNS PTR record updated: {name}.{dns_zone} -> {ip_address}")
                    except Exception as e:
                        click.echo(f"Warning: Could not update DNS: {e}", err=True)
                else:
                    click.echo("Warning: DNS zone specified but HETZNER_DNS_API_TOKEN not set", err=True)
        
        if server.public_net.ipv6:
            click.echo(f"  IPv6: {server.public_net.ipv6.ip}")
        
    except Exception as e:
        click.echo(f"Error creating server: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("name")
@click.option(
    "--keep-ip/--delete-ip",
    default=True,
    help="Keep floating IP after deletion (default: keep)",
)
@click.option("--delete-volumes/--keep-volumes", default=False, help="Delete attached volumes")
@click.confirmation_option(prompt="Are you sure you want to delete this server?")
@click.pass_context
def delete(ctx, name, keep_ip, delete_volumes):
    """Delete a development server"""
    config = ctx.obj["config"]
    
    # Get API token
    api_token = config.get_api_token()
    if not api_token:
        click.echo("Error: HETZNER_API_TOKEN not set. Set it in config or environment.", err=True)
        sys.exit(1)
    
    # Initialize server manager
    mgr = ServerManager(api_token)
    
    try:
        click.echo(f"Deleting server '{name}'...")
        mgr.delete_server(name, keep_floating_ip=keep_ip, delete_volumes=delete_volumes)
        click.echo(f"✓ Server '{name}' deleted successfully!")
        if keep_ip:
            click.echo("  Floating IP kept for reuse")
        
    except Exception as e:
        click.echo(f"Error deleting server: {e}", err=True)
        sys.exit(1)


@main.command()
@click.pass_context
def list(ctx):
    """List all servers"""
    config = ctx.obj["config"]
    
    # Get API token
    api_token = config.get_api_token()
    if not api_token:
        click.echo("Error: HETZNER_API_TOKEN not set. Set it in config or environment.", err=True)
        sys.exit(1)
    
    # Initialize server manager
    mgr = ServerManager(api_token)
    
    try:
        servers = mgr.list_servers()
        
        if not servers:
            click.echo("No servers found.")
            return
        
        click.echo(f"\nServers ({len(servers)}):")
        click.echo("-" * 80)
        
        for server in servers:
            click.echo(f"Name: {server.name}")
            click.echo(f"  ID: {server.id}")
            click.echo(f"  Status: {server.status}")
            click.echo(f"  Type: {server.server_type.name}")
            click.echo(f"  Location: {server.datacenter.location.name}")
            if server.public_net.ipv4:
                click.echo(f"  IPv4: {server.public_net.ipv4.ip}")
            if server.image:
                click.echo(f"  Image: {server.image.description or server.image.name}")
            click.echo()
        
    except Exception as e:
        click.echo(f"Error listing servers: {e}", err=True)
        sys.exit(1)


@main.command()
@click.pass_context
def list_snapshots(ctx):
    """List all snapshots"""
    config = ctx.obj["config"]
    
    # Get API token
    api_token = config.get_api_token()
    if not api_token:
        click.echo("Error: HETZNER_API_TOKEN not set. Set it in config or environment.", err=True)
        sys.exit(1)
    
    # Initialize server manager
    mgr = ServerManager(api_token)
    
    try:
        snapshots = mgr.list_snapshots()
        
        if not snapshots:
            click.echo("No snapshots found.")
            return
        
        max_age = config.get_snapshot_max_age_days()
        click.echo(f"\nSnapshots ({len(snapshots)}):")
        click.echo("-" * 80)
        
        for snapshot in snapshots:
            outdated = mgr.is_snapshot_outdated(snapshot, max_age)
            status = "⚠ OUTDATED" if outdated else "✓ Current"
            
            click.echo(f"{snapshot.description or snapshot.name or snapshot.id}")
            click.echo(f"  ID: {snapshot.id}")
            click.echo(f"  Created: {snapshot.created}")
            click.echo(f"  Status: {status}")
            if snapshot.created_from:
                click.echo(f"  Created from: {snapshot.created_from.name}")
            click.echo()
        
    except Exception as e:
        click.echo(f"Error listing snapshots: {e}", err=True)
        sys.exit(1)


@main.command()
@click.pass_context
def list_ips(ctx):
    """List all floating IPs"""
    config = ctx.obj["config"]
    
    # Get API token
    api_token = config.get_api_token()
    if not api_token:
        click.echo("Error: HETZNER_API_TOKEN not set. Set it in config or environment.", err=True)
        sys.exit(1)
    
    # Initialize server manager
    mgr = ServerManager(api_token)
    
    try:
        ips = mgr.list_floating_ips()
        
        if not ips:
            click.echo("No floating IPs found.")
            return
        
        click.echo(f"\nFloating IPs ({len(ips)}):")
        click.echo("-" * 80)
        
        for ip in ips:
            click.echo(f"IP: {ip.ip}")
            click.echo(f"  ID: {ip.id}")
            click.echo(f"  Type: {ip.type}")
            click.echo(f"  Location: {ip.home_location.name}")
            if ip.server:
                click.echo(f"  Assigned to: {ip.server.name}")
            else:
                click.echo(f"  Assigned to: (none)")
            if ip.description:
                click.echo(f"  Description: {ip.description}")
            click.echo()
        
    except Exception as e:
        click.echo(f"Error listing floating IPs: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("server_name")
@click.argument("snapshot_description")
@click.option(
    "--replace",
    "-r",
    default=None,
    help="Name of old snapshot to replace",
)
@click.pass_context
def create_snapshot(ctx, server_name, snapshot_description, replace):
    """Create a snapshot from a server"""
    config = ctx.obj["config"]
    
    # Get API token
    api_token = config.get_api_token()
    if not api_token:
        click.echo("Error: HETZNER_API_TOKEN not set. Set it in config or environment.", err=True)
        sys.exit(1)
    
    # Initialize server manager
    mgr = ServerManager(api_token)
    
    try:
        # Find old snapshot if specified
        old_snapshot = None
        if replace:
            old_snapshot = mgr.find_snapshot(replace)
            if not old_snapshot:
                click.echo(f"Warning: Old snapshot '{replace}' not found")
        
        click.echo(f"Creating snapshot from server '{server_name}'...")
        new_snapshot = mgr.update_server_and_snapshot(
            server_name, snapshot_description, old_snapshot
        )
        
        click.echo(f"✓ Snapshot created successfully!")
        click.echo(f"  ID: {new_snapshot.id}")
        click.echo(f"  Description: {new_snapshot.description}")
        
        if old_snapshot:
            click.echo(f"  Old snapshot '{replace}' deleted")
        
    except Exception as e:
        click.echo(f"Error creating snapshot: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("key", required=False)
@click.argument("value", required=False)
@click.option("--show", "-s", is_flag=True, help="Show all configuration")
@click.pass_context
def config(ctx, key, value, show):
    """Manage configuration settings"""
    cfg = ctx.obj["config"]
    
    if show:
        # Show all config (hide tokens)
        click.echo("Current configuration:")
        click.echo(f"  Config file: {cfg.config_path}")
        click.echo()
        
        for k, v in cfg.data.items():
            if "token" in k.lower() or "secret" in k.lower():
                display_value = "***" if v else "(not set)"
            else:
                display_value = v
            click.echo(f"  {k}: {display_value}")
        
        # Show environment variables
        click.echo("\nEnvironment variables:")
        import os
        if os.getenv("HETZNER_API_TOKEN"):
            click.echo("  HETZNER_API_TOKEN: ***")
        if os.getenv("HETZNER_DNS_API_TOKEN"):
            click.echo("  HETZNER_DNS_API_TOKEN: ***")
        if os.getenv("HETZNER_DNS_TOKEN"):
            click.echo("  HETZNER_DNS_TOKEN: *** (deprecated, use HETZNER_DNS_API_TOKEN)")
        
        return
    
    if not key:
        click.echo("Usage: pyhetznerdev config KEY [VALUE]")
        click.echo("   or: pyhetznerdev config --show")
        return
    
    if value:
        # Set config value
        cfg.set(key, value)
        cfg.save()
        click.echo(f"✓ Configuration updated: {key}")
    else:
        # Get config value
        val = cfg.get(key)
        if val:
            if "token" in key.lower() or "secret" in key.lower():
                click.echo("***")
            else:
                click.echo(val)
        else:
            click.echo(f"Configuration key '{key}' not set")


if __name__ == "__main__":
    main()
