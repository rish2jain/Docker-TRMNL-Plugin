# Docker Monitor - Quick Start (Webhook Mode)

**⚡ 3-Minute Setup - No Server Required!**

---

## 🚀 Installation

### Step 1: Get Webhook URL

```
1. Go to: https://usetrmnl.com/plugins
2. Find: Docker Monitor plugin
3. Copy: Webhook URL
```

### Step 2: Install Dependencies

```bash
pip install docker requests
```

### Step 3: Choose Setup Method

#### **Linux (systemd)** ⭐ Recommended

```bash
chmod +x setup_systemd.sh
./setup_systemd.sh
```

#### **Any Unix (cron)**

```bash
chmod +x setup_cron.sh
./setup_cron.sh
```

#### **Manual Test**

```bash
python3 bin/webhook_push.py \
  --webhook-url "YOUR_WEBHOOK_URL" \
  --verbose
```

---

## 📋 Configuration

### Basic Config

```json
{
  "webhook_url": "https://usetrmnl.com/api/custom_plugins/UUID/webhook",
  "docker_host": "unix:///var/run/docker.sock",
  "show_stopped": false,
  "cpu_threshold": 80,
  "memory_threshold": 85
}
```

### Environment Variables

```bash
export TRMNL_WEBHOOK_URL="YOUR_WEBHOOK_URL"
export DOCKER_HOST="unix:///var/run/docker.sock"
export CPU_THRESHOLD="80"
```

---

## 🔧 Common Commands

### Systemd

```bash
# View logs
sudo journalctl -u docker-trmnl.service -f

# Restart
sudo systemctl restart docker-trmnl.service

# Status
sudo systemctl status docker-trmnl.service
```

### Cron

```bash
# View logs
tail -f ~/docker-trmnl-plugin/logs/docker-trmnl.log

# Test manually
~/docker-trmnl-plugin/bin/cron_wrapper.sh

# Edit schedule
crontab -e
```

---

## 🐛 Troubleshooting

### Docker Access Issues

```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Test access
docker ps
```

### Can't Connect

```bash
# Test webhook
curl -X POST "YOUR_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'

# Check internet
ping usetrmnl.com
```

### Missing Dependencies

```bash
pip3 install docker requests
```

---

## 🎬 Demo Mode

Want to preview the plugin before connecting Docker?

```bash
python3 bin/webhook_push.py \
  --webhook-url "YOUR_WEBHOOK_URL" \
  --demo \
  --verbose
```

This sends sample container data to see how it looks on your TRMNL display.

## 📚 Full Documentation

- **[WEBHOOK_SETUP.md](WEBHOOK_SETUP.md)** - Complete webhook guide
- **[README.md](README.md)** - Full plugin documentation

---

## ✅ Success Checklist

- [ ] Webhook URL obtained from TRMNL
- [ ] Python packages installed (`docker`, `requests`)
- [ ] Docker access verified (`docker ps` works)
- [ ] Setup script completed successfully
- [ ] Service/cron is running
- [ ] Data appears on TRMNL device

**Done!** Your Docker stats are now pushing to TRMNL! 🎉
