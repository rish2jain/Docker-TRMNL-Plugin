# Docker Monitor for TRMNL

Monitor your Docker containers in real-time on your TRMNL e-ink display with comprehensive statistics, health monitoring, and system metrics.

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Docker Engine with API access
- TRMNL account with Docker Monitor plugin installed

### Installation

1. **Clone this repository:**
```bash
git clone https://github.com/rish2jain/Docker-TRMNL-Plugin.git
cd Docker-TRMNL-Plugin
```

2. **Install Python dependencies:**
```bash
pip install docker requests psutil
```

3. **Get your webhook URL from TRMNL:**
   - Go to https://usetrmnl.com/plugins
   - Find "Docker Monitor" plugin
   - Copy your webhook URL

4. **Run the script:**
```bash
python3 webhook_push.py --webhook-url "YOUR_WEBHOOK_URL"
```

## 📋 Setup Options

### Option 1: Manual Execution (Testing)

```bash
python3 webhook_push.py \
  --webhook-url "YOUR_WEBHOOK_URL" \
  --verbose
```

### Option 2: Systemd (Linux - Recommended)

Create service file `/etc/systemd/system/docker-trmnl.service`:

```ini
[Unit]
Description=Docker TRMNL Monitor
After=docker.service

[Service]
Type=oneshot
User=YOUR_USER
WorkingDirectory=/path/to/Docker-TRMNL-Plugin
ExecStart=/usr/bin/python3 webhook_push.py --webhook-url "YOUR_WEBHOOK_URL"

[Install]
WantedBy=multi-user.target
```

Create timer file `/etc/systemd/system/docker-trmnl.timer`:

```ini
[Unit]
Description=Docker TRMNL Monitor Timer

[Timer]
OnBootSec=1min
OnUnitActiveSec=5min

[Install]
WantedBy=timers.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable docker-trmnl.timer
sudo systemctl start docker-trmnl.timer
```

### Option 3: Cron (Any Unix)

Add to crontab (`crontab -e`):

```bash
*/5 * * * * cd /path/to/Docker-TRMNL-Plugin && /usr/bin/python3 webhook_push.py --webhook-url "YOUR_WEBHOOK_URL" >> /var/log/docker-trmnl.log 2>&1
```

### Option 4: Demo Mode (No Docker Required)

Preview the plugin without Docker:

```bash
python3 webhook_push.py \
  --webhook-url "YOUR_WEBHOOK_URL" \
  --demo \
  --verbose
```

## ⚙️ Configuration

The plugin is configured through the TRMNL web interface at https://usetrmnl.com/plugins

### Available Settings:

| Setting | Description | Default |
|---------|-------------|---------|
| **Max Containers** | Maximum containers to display | 10 |
| **Show Stopped** | Include stopped containers | No |
| **Container Filter** | Regex filter for container names | "" |
| **Sort By** | Sort criteria (name, cpu, memory, status) | cpu |
| **Sort Order** | Sort order (asc, desc) | desc |
| **CPU Threshold** | CPU alert threshold (%) | 80 |
| **Memory Threshold** | Memory alert threshold (%) | 85 |
| **Show Networks** | Display network statistics | Yes |

## 🔧 Docker Access

### Local Docker (Default)
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in for changes to take effect
```

The script uses `unix:///var/run/docker.sock` by default.

### Remote Docker Host
Set environment variable:
```bash
export DOCKER_HOST="tcp://your-docker-host:2376"
```

**Security Note:** Use TLS for remote connections.

## 🐛 Troubleshooting

### Permission Denied
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Test access
docker ps
```

### Can't Connect to Docker
```bash
# Check Docker is running
sudo systemctl status docker

# Check socket permissions
ls -la /var/run/docker.sock
```

### Webhook Fails
```bash
# Test webhook manually
curl -X POST "YOUR_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

### Debug Mode
```bash
# Run with verbose output
python3 webhook_push.py --webhook-url "YOUR_WEBHOOK_URL" --verbose
```

## 📊 What Gets Displayed

The plugin shows:
- **Container Stats**: CPU, Memory, Status for each container
- **System Metrics**: Total/Running/Stopped containers, System CPU/Memory
- **Visual Indicators**: ● for running, ■ for stopped, ⚠ for alerts
- **Alert Thresholds**: Configurable warnings for high CPU/Memory usage

## 🎨 Layout Views

The plugin automatically optimizes for your TRMNL screen configuration:
- **Full Layout**: Comprehensive dashboard view
- **Half Horizontal**: Balanced split view
- **Half Vertical**: Portrait orientation
- **Quadrant**: Compact quick overview

Templates are managed through TRMNL - no local configuration needed!

## 🔒 Security

- **Local Docker**: Requires docker group membership
- **Remote Docker**: Use TLS and proper authentication
- **Network**: Consider firewall rules for remote access
- **Data Privacy**: Container names may contain sensitive information

## 📚 Additional Resources

- **TRMNL Community**: https://community.usetrmnl.com
- **Plugin Dashboard**: https://usetrmnl.com/plugins
- **Documentation**: https://docs.usetrmnl.com

## 🆘 Support

- **GitHub Issues**: https://github.com/rish2jain/Docker-TRMNL-Plugin/issues
- **TRMNL Community**: https://community.usetrmnl.com

## 📄 License

MIT License - See LICENSE file for details

---

**Made with ❤️ for the TRMNL community**

*Monitor your Docker infrastructure on beautiful e-ink displays!*
