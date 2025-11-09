# pyhetznerdev Quick Reference

## Installation
```bash
pip install -e .
```

## Configuration
```bash
# Set API token (required)
export HETZNER_API_TOKEN="your-token"

# Set DNS token (optional)
export HETZNER_DNS_TOKEN="your-dns-token"

# Or use config file
pyhetznerdev config hetzner_api_token "your-token"
```

## Common Commands

### Create Server
```bash
# Basic
pyhetznerdev create myserver

# From snapshot
pyhetznerdev create myserver --snapshot dev-snapshot

# With existing IP
pyhetznerdev create myserver --floating-ip 1.2.3.4

# With DNS update
pyhetznerdev create myserver --dns-zone example.com

# Full example
pyhetznerdev create myserver \
  --server-type cx21 \
  --location fsn1 \
  --snapshot dev-ubuntu \
  --floating-ip 1.2.3.4 \
  --ssh-key mykey \
  --dns-zone example.com
```

### Delete Server
```bash
# Delete and keep IP (default)
pyhetznerdev delete myserver

# Delete and remove IP
pyhetznerdev delete myserver --delete-ip
```

### List Resources
```bash
pyhetznerdev list              # List servers
pyhetznerdev list-snapshots    # List snapshots
pyhetznerdev list-ips          # List floating IPs
```

### Manage Snapshots
```bash
# Create snapshot
pyhetznerdev create-snapshot myserver "Description"

# Replace old snapshot
pyhetznerdev create-snapshot myserver "New" --replace "Old"
```

### Configuration
```bash
pyhetznerdev config --show                           # Show config
pyhetznerdev config default_server_type cx21         # Set default
pyhetznerdev config snapshot_max_age_days 30         # Set max age
```

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `hetzner_api_token` | - | Hetzner Cloud API token (required) |
| `hetzner_dns_token` | - | Hetzner DNS API token (optional) |
| `default_server_type` | cx11 | Default server type |
| `default_location` | nbg1 | Default location |
| `default_image` | ubuntu-22.04 | Default image |
| `snapshot_max_age_days` | 30 | Max snapshot age before update |

## Server Types
- `cx11` - 1 vCPU, 2 GB RAM
- `cx21` - 2 vCPU, 4 GB RAM
- `cx31` - 2 vCPU, 8 GB RAM
- `cx41` - 4 vCPU, 16 GB RAM
- `cx51` - 8 vCPU, 32 GB RAM

## Locations
- `nbg1` - Nuremberg, Germany
- `fsn1` - Falkenstein, Germany
- `hel1` - Helsinki, Finland
- `ash` - Ashburn, USA
- `hil` - Hillsboro, USA

## Workflow Examples

### Daily Development
```bash
# Morning: Start server
pyhetznerdev create dev --snapshot my-dev --floating-ip 1.2.3.4

# Evening: Stop server (keeps IP)
pyhetznerdev delete dev
```

### Weekly Maintenance
```bash
# Update snapshot
pyhetznerdev create dev --snapshot my-dev  # Will prompt to update if old
pyhetznerdev create-snapshot dev "my-dev" --replace "my-dev"
pyhetznerdev delete dev
```

### First Time Setup
```bash
# Create base server
pyhetznerdev create dev --image ubuntu-22.04

# Configure environment, install packages, etc.
# ...

# Create snapshot
pyhetznerdev create-snapshot dev "my-dev-env"

# Delete server
pyhetznerdev delete dev
```
