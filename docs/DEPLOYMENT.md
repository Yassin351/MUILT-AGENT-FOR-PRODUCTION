# 🚀 Deployment Guide

## Production Deployment Checklist

### Pre-Deployment
- [ ] All tests passing (70%+ coverage)
- [ ] Environment variables configured
- [ ] API keys obtained and secured
- [ ] Dependencies installed
- [ ] Tesseract OCR installed
- [ ] Logs directory created
- [ ] Security audit completed

### Deployment Options

## Option 1: Local/On-Premise Deployment

### Requirements
- Ubuntu 20.04+ / Windows Server 2019+
- Python 3.9+
- 4GB RAM minimum (8GB recommended)
- 20GB disk space
- Tesseract OCR

### Steps

1. **Setup Environment**
```bash
# Create application user
sudo useradd -m -s /bin/bash procurement
sudo su - procurement

# Clone repository
git clone <repo-url> /opt/procurement
cd /opt/procurement

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
# Copy and edit environment file
cp .env.sample .env
nano .env

# Set production values
ENVIRONMENT=production
LOG_LEVEL=INFO
MAX_RETRIES=5
TIMEOUT_SECONDS=60
```

3. **Install System Dependencies**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y tesseract-ocr python3-dev build-essential

# CentOS/RHEL
sudo yum install -y tesseract python3-devel gcc
```

4. **Setup Systemd Service**
```bash
sudo nano /etc/systemd/system/procurement.service
```

```ini
[Unit]
Description=Kenya Smart Procurement AI
After=network.target

[Service]
Type=simple
User=procurement
WorkingDirectory=/opt/procurement
Environment="PATH=/opt/procurement/venv/bin"
ExecStart=/opt/procurement/venv/bin/streamlit run ui/app.py --server.port=8501 --server.address=0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable procurement
sudo systemctl start procurement
sudo systemctl status procurement
```

5. **Setup Nginx Reverse Proxy**
```bash
sudo apt-get install -y nginx

sudo nano /etc/nginx/sites-available/procurement
```

```nginx
server {
    listen 80;
    server_name procurement.example.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/procurement /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

6. **Setup SSL (Optional but Recommended)**
```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d procurement.example.com
```

---

## Option 2: Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8501

# Run application
CMD ["streamlit", "run", "ui/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  procurement:
    build: .
    ports:
      - "8501:8501"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
      - ./.env:/app/.env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Deploy with Docker
```bash
# Build image
docker build -t procurement-ai .

# Run container
docker run -d \
  --name procurement \
  -p 8501:8501 \
  -v $(pwd)/logs:/app/logs \
  --env-file .env \
  procurement-ai

# Or use docker-compose
docker-compose up -d
```

---

## Option 3: Cloud Deployment (Render)

### render.yaml (Already included)
```yaml
services:
  - type: web
    name: kenya-procurement-ai
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run ui/app.py --server.port=$PORT --server.address=0.0.0.0
    envVars:
      - key: GOOGLE_API_KEY
        sync: false
      - key: ENVIRONMENT
        value: production
      - key: LOG_LEVEL
        value: INFO
```

### Deploy to Render
1. Push code to GitHub
2. Connect repository to Render
3. Add environment variables in Render dashboard
4. Deploy automatically

---

## Option 4: AWS Deployment

### EC2 Deployment
```bash
# Launch EC2 instance (t3.medium recommended)
# SSH into instance
ssh -i key.pem ubuntu@<instance-ip>

# Follow local deployment steps
# Configure security group to allow port 80/443
```

### ECS Deployment
```bash
# Build and push Docker image
aws ecr create-repository --repository-name procurement-ai
docker tag procurement-ai:latest <account-id>.dkr.ecr.<region>.amazonaws.com/procurement-ai:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/procurement-ai:latest

# Create ECS task definition and service
aws ecs create-cluster --cluster-name procurement-cluster
# ... (full ECS setup)
```

---

## Post-Deployment

### 1. Verify Deployment
```bash
# Check service status
curl http://your-domain.com/_stcore/health

# Check logs
tail -f logs/procurement_*.log

# Run health check
python -c "from core.resilience import health_monitor; print(health_monitor.check_health())"
```

### 2. Setup Monitoring

**Log Monitoring:**
```bash
# Install log aggregation (optional)
sudo apt-get install -y logrotate

# Configure logrotate
sudo nano /etc/logrotate.d/procurement
```

```
/opt/procurement/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 procurement procurement
}
```

**Application Monitoring:**
- Setup uptime monitoring (UptimeRobot, Pingdom)
- Configure error alerting
- Monitor API usage and quotas

### 3. Backup Strategy
```bash
# Backup configuration
tar -czf backup-$(date +%Y%m%d).tar.gz .env logs/ data/

# Automated backup script
cat > /opt/procurement/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/procurement"
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf $BACKUP_DIR/backup_$DATE.tar.gz /opt/procurement/.env /opt/procurement/logs
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +30 -delete
EOF

chmod +x /opt/procurement/backup.sh

# Add to crontab
crontab -e
# Add: 0 2 * * * /opt/procurement/backup.sh
```

### 4. Security Hardening
```bash
# Setup firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Disable root login
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no

# Setup fail2ban
sudo apt-get install -y fail2ban
sudo systemctl enable fail2ban
```

### 5. Performance Tuning
```bash
# Increase file descriptors
sudo nano /etc/security/limits.conf
# Add:
# procurement soft nofile 65536
# procurement hard nofile 65536

# Optimize Python
export PYTHONOPTIMIZE=1
```

---

## Scaling Considerations

### Horizontal Scaling
- Deploy multiple instances behind load balancer
- Use Redis for session management
- Implement request queuing

### Vertical Scaling
- Increase RAM for larger workloads
- Add CPU cores for parallel processing
- Optimize database queries

### Caching
- Implement Redis for API response caching
- Cache market data for 1-hour intervals
- Use CDN for static assets

---

## Rollback Procedure

```bash
# Stop service
sudo systemctl stop procurement

# Restore from backup
cd /opt/procurement
tar -xzf /backup/procurement/backup_YYYYMMDD.tar.gz

# Restart service
sudo systemctl start procurement

# Verify
sudo systemctl status procurement
```

---

## Maintenance Windows

**Recommended Schedule:**
- Updates: Sunday 2:00 AM - 4:00 AM EAT
- Backups: Daily 2:00 AM EAT
- Log rotation: Daily 3:00 AM EAT
- Health checks: Every 5 minutes

---

## Support Contacts

**Technical Issues:**
- Email: support@procurement.example.com
- Slack: #procurement-support

**Emergency:**
- On-call: +254-XXX-XXXXXX
- Escalation: team-lead@example.com

---

## Deployment Verification Checklist

- [ ] Application accessible via URL
- [ ] Health check endpoint responding
- [ ] Logs being written correctly
- [ ] API keys working
- [ ] SSL certificate valid
- [ ] Monitoring alerts configured
- [ ] Backup script running
- [ ] Performance acceptable
- [ ] Security scan passed
- [ ] Documentation updated
