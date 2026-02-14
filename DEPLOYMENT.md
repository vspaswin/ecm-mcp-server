# ECM MCP Server Deployment Guide

## Table of Contents
1. [Local Development](#local-development)
2. [Production Deployment](#production-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Monitoring and Maintenance](#monitoring-and-maintenance)

## Local Development

### Prerequisites
- Python 3.10+
- Git
- Virtual environment tool (venv or conda)
- Access to ECM API

### Setup Steps

1. **Clone Repository**
   ```bash
   git clone https://github.com/vspaswin/ecm-mcp-server.git
   cd ecm-mcp-server
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate  # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

5. **Run Server**
   ```bash
   python src/server.py
   ```

### Development Tools

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Lint code
flake8 src/ tests/

# Format code
black src/ tests/
```

## Production Deployment

### Server Requirements
- CPU: 2+ cores
- RAM: 4GB minimum
- Storage: 10GB minimum
- Network: Stable connection to ECM API
- OS: Linux (Ubuntu 20.04+ recommended)

### Installation

1. **System Setup**
   ```bash
   sudo apt update
   sudo apt install python3.10 python3.10-venv git
   ```

2. **Create Service User**
   ```bash
   sudo useradd -m -s /bin/bash ecmserver
   sudo su - ecmserver
   ```

3. **Install Application**
   ```bash
   git clone https://github.com/vspaswin/ecm-mcp-server.git
   cd ecm-mcp-server
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   nano .env  # Edit configuration
   ```

5. **Set Permissions**
   ```bash
   chmod 600 .env
   chmod +x src/server.py
   ```

### Systemd Service

Create `/etc/systemd/system/ecm-mcp-server.service`:

```ini
[Unit]
Description=ECM MCP Server
After=network.target

[Service]
Type=simple
User=ecmserver
WorkingDirectory=/home/ecmserver/ecm-mcp-server
Environment="PATH=/home/ecmserver/ecm-mcp-server/venv/bin"
EnvironmentFile=/home/ecmserver/ecm-mcp-server/.env
ExecStart=/home/ecmserver/ecm-mcp-server/venv/bin/python src/server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ecm-mcp-server
sudo systemctl start ecm-mcp-server
sudo systemctl status ecm-mcp-server
```

## Docker Deployment

### Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/

# Create non-root user
RUN useradd -m -u 1000 ecmserver && chown -R ecmserver:ecmserver /app
USER ecmserver

# Run server
CMD ["python", "src/server.py"]
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  ecm-mcp-server:
    build: .
    container_name: ecm-mcp-server
    restart: unless-stopped
    environment:
      - ECM_API_URL=${ECM_API_URL}
      - ECM_USERNAME=${ECM_USERNAME}
      - ECM_PASSWORD=${ECM_PASSWORD}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    volumes:
      - ./logs:/app/logs
    networks:
      - ecm-network

networks:
  ecm-network:
    driver: bridge
```

### Build and Run

```bash
# Build image
docker build -t ecm-mcp-server:latest .

# Run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Cloud Deployment

### AWS ECS

1. **Create ECR Repository**
   ```bash
   aws ecr create-repository --repository-name ecm-mcp-server
   ```

2. **Push Docker Image**
   ```bash
   # Authenticate
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
   
   # Tag and push
   docker tag ecm-mcp-server:latest <account>.dkr.ecr.us-east-1.amazonaws.com/ecm-mcp-server:latest
   docker push <account>.dkr.ecr.us-east-1.amazonaws.com/ecm-mcp-server:latest
   ```

3. **Create ECS Task Definition**
   - Use Fargate launch type
   - Configure environment variables from Secrets Manager
   - Set resource limits (0.5 vCPU, 1GB RAM minimum)

4. **Create ECS Service**
   - Deploy to VPC with ECM API access
   - Configure auto-scaling if needed
   - Set up health checks

### Google Cloud Run

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/ecm-mcp-server
gcloud run deploy ecm-mcp-server \
  --image gcr.io/PROJECT_ID/ecm-mcp-server \
  --platform managed \
  --region us-central1 \
  --set-env-vars ECM_API_URL=$ECM_API_URL
```

### Azure Container Instances

```bash
# Create resource group
az group create --name ecm-mcp-rg --location eastus

# Deploy container
az container create \
  --resource-group ecm-mcp-rg \
  --name ecm-mcp-server \
  --image ecmmcpserver.azurecr.io/ecm-mcp-server:latest \
  --environment-variables \
    ECM_API_URL=$ECM_API_URL \
  --secure-environment-variables \
    ECM_USERNAME=$ECM_USERNAME \
    ECM_PASSWORD=$ECM_PASSWORD
```

## Monitoring and Maintenance

### Logging

**Configure logging in production:**

```python
# config/settings.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    handler = RotatingFileHandler(
        'logs/ecm-mcp-server.log',
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    logging.getLogger().addHandler(handler)
```

### Health Monitoring

**Set up health check endpoint:**

```bash
# Simple health check
curl http://localhost:8000/health

# With monitoring tool
watch -n 30 'curl -s http://localhost:8000/health | jq .'
```

### Metrics Collection

**Use Prometheus for metrics:**

```python
# Add to server.py
from prometheus_client import Counter, Histogram, start_http_server

api_requests = Counter('ecm_api_requests_total', 'Total API requests')
api_duration = Histogram('ecm_api_duration_seconds', 'API request duration')

start_http_server(9090)  # Metrics endpoint
```

### Backup and Recovery

1. **Configuration Backup**
   ```bash
   # Backup .env and configs
   tar -czf config-backup-$(date +%Y%m%d).tar.gz .env config/
   ```

2. **Log Rotation**
   ```bash
   # /etc/logrotate.d/ecm-mcp-server
   /home/ecmserver/ecm-mcp-server/logs/*.log {
       daily
       rotate 7
       compress
       delaycompress
       notifempty
       create 0640 ecmserver ecmserver
   }
   ```

### Updates and Maintenance

1. **Update Application**
   ```bash
   cd /home/ecmserver/ecm-mcp-server
   git pull origin main
   source venv/bin/activate
   pip install -r requirements.txt --upgrade
   sudo systemctl restart ecm-mcp-server
   ```

2. **Security Updates**
   ```bash
   # Check for vulnerabilities
   pip-audit
   
   # Update dependencies
   pip list --outdated
   pip install --upgrade <package>
   ```

### Performance Tuning

1. **Connection Pooling**
   ```python
   # In ecm_client.py
   limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)
   client = httpx.AsyncClient(limits=limits)
   ```

2. **Caching**
   ```python
   # Add caching for frequently accessed data
   from functools import lru_cache
   
   @lru_cache(maxsize=128)
   async def get_metadata_schema(document_type: str):
       # Cache schema lookups
       pass
   ```

3. **Rate Limiting**
   ```python
   # Implement rate limiting to protect ECM API
   from aiolimiter import AsyncLimiter
   
   rate_limit = AsyncLimiter(max_rate=100, time_period=60)
   ```

## Security Hardening

1. **Firewall Configuration**
   ```bash
   sudo ufw allow from 10.0.0.0/8 to any port 8000
   sudo ufw enable
   ```

2. **SSL/TLS**
   - Use HTTPS for all ECM API connections
   - Validate SSL certificates
   - Use TLS 1.2 or higher

3. **Secrets Management**
   - Use environment variables for sensitive data
   - Consider AWS Secrets Manager, Azure Key Vault, or HashiCorp Vault
   - Never commit credentials to version control

4. **Access Control**
   - Implement role-based access control (RBAC)
   - Audit log all operations
   - Rotate credentials regularly

## Troubleshooting

### Common Issues

1. **Connection Refused**
   ```bash
   # Check if service is running
   sudo systemctl status ecm-mcp-server
   
   # Check logs
   sudo journalctl -u ecm-mcp-server -f
   ```

2. **Authentication Failures**
   ```bash
   # Verify credentials
   echo $ECM_USERNAME
   echo $ECM_PASSWORD
   
   # Test API connection
   curl -u $ECM_USERNAME:$ECM_PASSWORD $ECM_API_URL/health
   ```

3. **Performance Issues**
   ```bash
   # Monitor resource usage
   htop
   
   # Check API response times
   time curl $ECM_API_URL/health
   ```

## Support

For deployment assistance:
- GitHub Issues: https://github.com/vspaswin/ecm-mcp-server/issues
- Documentation: README.md and examples/
