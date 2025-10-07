#!/usr/bin/env python3
"""
Docker Container Monitor - Webhook Push Script
Runs locally on Docker host and pushes data to TRMNL webhook
No server required!
"""

import os
import sys
import json
import time
import argparse
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Any

try:
    import docker
    import requests
except ImportError:
    print("ERROR: Missing required packages. Install with:")
    print("  pip install docker requests")
    sys.exit(1)


def format_uptime(started_at: str) -> str:
    """Format container uptime in human-readable format"""
    try:
        start_time = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
        uptime = datetime.now(start_time.tzinfo) - start_time

        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        if days > 0:
            return f"{days}d {hours}h"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    except:
        return "unknown"


def format_bytes(bytes_value: int) -> str:
    """Format bytes to human-readable string"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f}{unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f}TB"


def get_container_stats(client: docker.DockerClient, container: docker.models.containers.Container,
                        cpu_threshold: int, memory_threshold: int) -> Dict[str, Any]:
    """Get statistics for a single container"""
    try:
        # Get stats twice with a short delay for accurate CPU calculation
        stats1 = container.stats(stream=False)
        time.sleep(0.1)  # 100ms delay
        stats = container.stats(stream=False)

        # Calculate CPU percentage using the two measurements (matches Docker CLI calculation)
        cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                   stats1['cpu_stats']['cpu_usage']['total_usage']
        system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                      stats1['cpu_stats']['system_cpu_usage']

        cpu_percent = 0.0
        if system_delta > 0 and cpu_delta >= 0:
            # Get number of CPUs from online_cpus if available, otherwise use percpu_usage length
            num_cpus = stats['cpu_stats'].get('online_cpus',
                                              len(stats['cpu_stats']['cpu_usage'].get('percpu_usage', [1])))
            # Calculate percentage: (container CPU delta / system CPU delta) * number of CPUs * 100
            cpu_percent = (cpu_delta / system_delta) * num_cpus * 100.0

        # Calculate memory percentage
        memory_usage = stats['memory_stats'].get('usage', 0)
        memory_limit = stats['memory_stats'].get('limit', 1)
        memory_percent = (memory_usage / memory_limit) * 100.0 if memory_limit > 0 else 0.0

        # Network stats
        network_rx = 0
        network_tx = 0
        if 'networks' in stats:
            for interface, net_stats in stats['networks'].items():
                network_rx += net_stats.get('rx_bytes', 0)
                network_tx += net_stats.get('tx_bytes', 0)

        # Check for alerts
        alerts = []
        has_alert = False

        if cpu_percent >= cpu_threshold:
            alerts.append(f"High CPU usage: {cpu_percent:.1f}%")
            has_alert = True

        if memory_percent >= memory_threshold:
            alerts.append(f"High memory usage: {memory_percent:.1f}%")
            has_alert = True

        return {
            "cpu_percent": round(cpu_percent, 1),
            "memory_percent": round(memory_percent, 1),
            "memory_usage": format_bytes(memory_usage),
            "network_rx": format_bytes(network_rx),
            "network_tx": format_bytes(network_tx),
            "has_alert": has_alert,
            "alert_messages": alerts
        }
    except Exception as e:
        return {
            "cpu_percent": 0,
            "memory_percent": 0,
            "has_alert": False,
            "alert_messages": []
        }


def get_demo_data() -> Dict[str, Any]:
    """Generate realistic demo/sample data for testing"""
    return {
        "containers": [
            {
                "id": "abc123def456",
                "name": "nginx-web",
                "image": "nginx:alpine",
                "status": "running",
                "uptime": "3d 5h",
                "restart_count": 0,
                "cpu_percent": 12.5,
                "memory_percent": 8.3,
                "memory_usage": "256.0MB",
                "network_rx": "1.2GB",
                "network_tx": "856.0MB",
                "has_alert": False,
                "alert_messages": []
            },
            {
                "id": "def456ghi789",
                "name": "postgres-db",
                "image": "postgres:15-alpine",
                "status": "running",
                "uptime": "7d 12h",
                "cpu_percent": 25.8,
                "memory_percent": 42.1,
                "memory_usage": "1.3GB",
                "network_rx": "5.8GB",
                "network_tx": "3.2GB",
                "has_alert": False,
                "alert_messages": []
            },
            {
                "id": "ghi789jkl012",
                "name": "redis-cache",
                "image": "redis:7-alpine",
                "status": "running",
                "uptime": "5d 8h",
                "cpu_percent": 5.2,
                "memory_percent": 15.6,
                "memory_usage": "468.0MB",
                "network_rx": "2.1GB",
                "network_tx": "1.8GB",
                "has_alert": False,
                "alert_messages": []
            },
            {
                "id": "jkl012mno345",
                "name": "api-backend",
                "image": "node:20-alpine",
                "status": "running",
                "uptime": "1d 3h",
                "cpu_percent": 85.3,
                "memory_percent": 68.9,
                "memory_usage": "2.1GB",
                "network_rx": "892.0MB",
                "network_tx": "1.5GB",
                "has_alert": True,
                "alert_messages": [
                    "High CPU usage: 85.3%",
                    "High memory usage: 68.9%"
                ]
            },
            {
                "id": "mno345pqr678",
                "name": "grafana",
                "image": "grafana/grafana:latest",
                "status": "running",
                "uptime": "10d 2h",
                "cpu_percent": 8.7,
                "memory_percent": 22.4,
                "memory_usage": "672.0MB",
                "network_rx": "3.4GB",
                "network_tx": "2.9GB",
                "has_alert": False,
                "alert_messages": []
            },
            {
                "id": "vwx234yza567",
                "name": "elasticsearch",
                "image": "elasticsearch:8.10.0",
                "status": "exited",
                "uptime": "0",
                "cpu_percent": 0,
                "memory_percent": 0,
                "memory_usage": "0.0B",
                "network_rx": "12.0GB",
                "network_tx": "8.5GB",
                "has_alert": False,
                "alert_messages": []
            }
        ],
        "system": {
            "docker_version": "24.0.7",
            "containers_total": 10,
            "containers_running": 9,
            "containers_paused": 0,
            "containers_stopped": 1,
            "cpu_percent": round(psutil.cpu_percent(interval=0.1, percpu=False), 1),
            "memory_percent": round((psutil.virtual_memory().used / psutil.virtual_memory().total) * 100, 1)
        },
        "last_update": datetime.now().isoformat()
    }


def collect_docker_data(config: Dict[str, Any]) -> Dict[str, Any]:
    """Collect Docker container data"""
    docker_host = config.get('docker_host', 'unix:///var/run/docker.sock')
    docker_api_version = config.get('docker_api_version', '1.41')
    show_stopped = config.get('show_stopped', False)
    cpu_threshold = int(config.get('cpu_threshold', 80))
    memory_threshold = int(config.get('memory_threshold', 85))
    sort_by = config.get('sort_by', 'cpu')
    sort_order = config.get('sort_order', 'desc')

    # Connect to Docker
    client = docker.DockerClient(base_url=docker_host, version=docker_api_version)

    # Get system info
    info = client.info()

    # Get all containers
    containers_list = client.containers.list(all=show_stopped)

    # Process containers
    containers_data = []
    for container in containers_list:
        # Get restart count from container attrs
        restart_count = container.attrs.get('RestartCount', 0)

        container_info = {
            "id": container.short_id,
            "name": container.name,
            "status": container.status,
            "image": container.image.tags[0] if container.image.tags else container.image.short_id,
            "restart_count": restart_count,
        }

        # Get uptime for running containers
        if container.status == "running":
            started_at = container.attrs['State']['StartedAt']
            container_info["uptime"] = format_uptime(started_at)

            # Get stats for running containers
            stats = get_container_stats(client, container, cpu_threshold, memory_threshold)
            container_info.update(stats)
        else:
            container_info.update({
                "cpu_percent": 0,
                "memory_percent": 0,
                "has_alert": False,
                "alert_messages": []
            })

        containers_data.append(container_info)

    # Sort containers
    reverse = (sort_order == 'desc')
    if sort_by == 'cpu':
        containers_data.sort(key=lambda x: x.get('cpu_percent', 0), reverse=reverse)
    elif sort_by == 'memory':
        containers_data.sort(key=lambda x: x.get('memory_percent', 0), reverse=reverse)
    elif sort_by == 'name':
        containers_data.sort(key=lambda x: x.get('name', ''), reverse=reverse)
    elif sort_by == 'status':
        containers_data.sort(key=lambda x: x.get('status', ''), reverse=reverse)

    # Build response
    return {
        "containers": containers_data,
        "system": {
            "docker_version": info.get('ServerVersion', 'unknown'),
            "containers_total": info.get('Containers', 0),
            "containers_running": info.get('ContainersRunning', 0),
            "containers_paused": info.get('ContainersPaused', 0),
            "containers_stopped": info.get('ContainersStopped', 0),
            "cpu_percent": round(psutil.cpu_percent(interval=0.1, percpu=False), 1),
            "memory_percent": round((psutil.virtual_memory().used / psutil.virtual_memory().total) * 100, 1),
        },
        "last_update": datetime.now().isoformat()
    }


def push_to_webhook(webhook_url: str, data: Dict[str, Any], timeout: int = 10) -> bool:
    """Push data to TRMNL webhook"""
    try:
        # TRMNL expects data nested in merge_variables
        payload = {"merge_variables": data}
        
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=timeout,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to push to webhook: {e}", file=sys.stderr)
        return False


def load_config(config_file: str = None) -> Dict[str, Any]:
    """Load configuration from file or environment"""
    config = {}

    # Load from config file if provided
    if config_file and os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)

    # Override with environment variables
    env_mapping = {
        'TRMNL_WEBHOOK_URL': 'webhook_url',
        'DOCKER_HOST': 'docker_host',
        'DOCKER_API_VERSION': 'docker_api_version',
        'SHOW_STOPPED': 'show_stopped',
        'CPU_THRESHOLD': 'cpu_threshold',
        'MEMORY_THRESHOLD': 'memory_threshold',
        'SORT_BY': 'sort_by',
        'SORT_ORDER': 'sort_order',
    }

    for env_var, config_key in env_mapping.items():
        if env_var in os.environ:
            value = os.environ[env_var]
            # Convert booleans
            if config_key == 'show_stopped':
                value = value.lower() in ('true', '1', 'yes')
            # Convert numbers
            elif config_key in ('cpu_threshold', 'memory_threshold'):
                value = int(value)
            config[config_key] = value

    return config


def main():
    parser = argparse.ArgumentParser(
        description='Push Docker container stats to TRMNL webhook'
    )
    parser.add_argument(
        '--webhook-url',
        help='TRMNL webhook URL (or set TRMNL_WEBHOOK_URL env var)'
    )
    parser.add_argument(
        '--config',
        help='Path to JSON config file'
    )
    parser.add_argument(
        '--loop',
        action='store_true',
        help='Run continuously (for systemd service)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=30,
        help='Update interval in seconds when using --loop (default: 30)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print verbose output'
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Send demo/sample data (no Docker required)'
    )

    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # Get webhook URL
    webhook_url = args.webhook_url or config.get('webhook_url') or os.environ.get('TRMNL_WEBHOOK_URL')

    if not webhook_url:
        print("ERROR: Webhook URL required. Provide via --webhook-url, config file, or TRMNL_WEBHOOK_URL env var")
        sys.exit(1)

    # Get interval
    interval = config.get('refresh_interval', args.interval)

    try:
        while True:
            try:
                if args.verbose:
                    if args.demo:
                        print(f"[{datetime.now().isoformat()}] Generating demo data...")
                    else:
                        print(f"[{datetime.now().isoformat()}] Collecting Docker data...")

                # Collect data
                if args.demo:
                    data = get_demo_data()
                else:
                    data = collect_docker_data(config)

                if args.verbose:
                    print(f"  Found {len(data['containers'])} containers")
                    print(f"  Pushing to webhook...")

                # Push to webhook
                success = push_to_webhook(webhook_url, data)

                if success:
                    if args.verbose:
                        print(f"  ✓ Successfully pushed data to TRMNL")
                else:
                    print(f"  ✗ Failed to push data", file=sys.stderr)

            except docker.errors.DockerException as e:
                error_data = {
                    "error": {"message": f"Docker connection failed: {str(e)}"},
                    "containers": [],
                    "system": {}
                }
                push_to_webhook(webhook_url, error_data)
                if args.verbose:
                    print(f"  ✗ Docker error: {e}", file=sys.stderr)

            except Exception as e:
                if args.verbose:
                    print(f"  ✗ Unexpected error: {e}", file=sys.stderr)

            # Exit if not in loop mode
            if not args.loop:
                break

            # Wait for next iteration
            if args.verbose:
                print(f"  Waiting {interval} seconds...\n")
            time.sleep(interval)

    except KeyboardInterrupt:
        if args.verbose:
            print("\nShutdown requested... exiting")
        sys.exit(0)


if __name__ == "__main__":
    main()
