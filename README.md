# pyhetznerdev

Create development resources in the Hetzner cloud with ease.

A command-line tool for managing Hetzner Cloud development servers with support for:
- Easy server creation and deletion
- Automatic snapshot management with age checking
- Floating IP management and reuse
- DNS record updates
- Simple CLI interface

## Features

- ✅ **Easy Server Creation**: Create servers with a single command
- ✅ **Floating IP Support**: Reuse existing floating IPs or create new ones
- ✅ **Snapshot-Based Deployment**: Create servers from snapshots by default
- ✅ **Automatic Snapshot Updates**: Check if snapshots are outdated (30 days) and update them
- ✅ **DNS Integration**: Automatically update DNS records when servers are created
- ✅ **IP Retention**: Keep floating IPs when servers are deleted (default behavior)
- ✅ **Nice CLI**: Clean command-line interface using Click

## Installation

```bash
pip install -e .
```

For development:
```bash
pip install -e ".[dev]"
```

## Configuration

### API Tokens

You need a Hetzner Cloud API token. You can set it in two ways:

1. Environment variable:
```bash
export HETZNER_API_TOKEN="your-token-here"
```

2. Configuration file:
```bash
pyhetznerdev config hetzner_api_token "your-token-here"
```

For DNS features, you also need a Hetzner DNS API token:
```bash
export HETZNER_DNS_TOKEN="your-dns-token-here"
# or
pyhetznerdev config hetzner_dns_token "your-dns-token-here"
```

### Configuration Options

View current configuration:
```bash
pyhetznerdev config --show
```

Set configuration values:
```bash
pyhetznerdev config default_server_type cx21
pyhetznerdev config default_location fsn1
pyhetznerdev config default_image ubuntu-22.04
pyhetznerdev config snapshot_max_age_days 30
```

Configuration is stored in `~/.config/pyhetznerdev/config.yaml`

## Usage

### Create a Server

Basic server creation:
```bash
pyhetznerdev create myserver
```

Create with specific options:
```bash
pyhetznerdev create myserver \
  --server-type cx21 \
  --location fsn1 \
  --snapshot my-dev-snapshot \
  --floating-ip 1.2.3.4 \
  --ssh-key mykey \
  --dns-zone example.com
```

Create from a snapshot (with automatic outdated check):
```bash
pyhetznerdev create myserver --snapshot dev-ubuntu
```

Create from base image (no snapshot):
```bash
pyhetznerdev create myserver --image ubuntu-22.04 --no-update-snapshot
```

### Delete a Server

Delete and keep floating IP (default):
```bash
pyhetznerdev delete myserver
```

Delete and remove floating IP:
```bash
pyhetznerdev delete myserver --delete-ip
```

### List Resources

List all servers:
```bash
pyhetznerdev list
```

List all snapshots (shows which are outdated):
```bash
pyhetznerdev list-snapshots
```

List all floating IPs:
```bash
pyhetznerdev list-ips
```

### Manage Snapshots

Create a snapshot from a running server:
```bash
pyhetznerdev create-snapshot myserver "My development snapshot"
```

Create and replace an old snapshot:
```bash
pyhetznerdev create-snapshot myserver "Updated dev snapshot" --replace "old-snapshot-name"
```

## How It Works

### Snapshot Management

When creating a server with `--snapshot`:
1. The tool checks if the snapshot exists
2. If found, it checks the snapshot age against `snapshot_max_age_days` (default: 30)
3. If outdated, you're prompted to update it
4. A temporary server is created from the old snapshot
5. The server is powered off and a new snapshot is created
6. The old snapshot is deleted
7. The temporary server is cleaned up
8. Your actual server is created from the fresh snapshot

### Floating IP Management

- When creating a server with `--floating-ip`, the tool checks if that IP exists in your account
- If the IP exists, it's assigned to the new server
- When deleting a server, floating IPs are kept by default (use `--delete-ip` to remove them)
- This allows you to maintain a stable IP for your development environment

### DNS Updates

When `--dns-zone` is specified:
- The tool automatically creates or updates an A record for your server
- The record name matches the server name
- If the IP changes, the DNS record is updated automatically
- Requires `HETZNER_DNS_TOKEN` to be set

## Examples

### Typical Development Workflow

1. **First time setup**:
```bash
# Set your API token
export HETZNER_API_TOKEN="your-token"

# Create initial server
pyhetznerdev create devserver --image ubuntu-22.04

# SSH in and configure your development environment
# ...

# Create a snapshot
pyhetznerdev create-snapshot devserver "my-dev-env"
```

2. **Daily use**:
```bash
# Create server from snapshot (reusing IP if you have one)
pyhetznerdev create devserver --snapshot my-dev-env --floating-ip 1.2.3.4

# Work on your project
# ...

# Delete server when done (IP is kept)
pyhetznerdev delete devserver
```

3. **Weekly maintenance**:
```bash
# Create server (tool will detect outdated snapshot and offer to update)
pyhetznerdev create devserver --snapshot my-dev-env

# Manually update snapshot
pyhetznerdev create-snapshot devserver "my-dev-env" --replace "my-dev-env"
```

## Development

Install development dependencies:
```bash
pip install -e ".[dev]"
```

Run tests:
```bash
pytest
```

Format code:
```bash
black pyhetznerdev/
```

Lint:
```bash
flake8 pyhetznerdev/
```

## License

MIT
