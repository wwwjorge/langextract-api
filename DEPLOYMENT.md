# LangExtract API - Production Deployment Guide

This guide provides detailed instructions for deploying the LangExtract API in production environments using Docker and Portainer.

## 📋 Pre-Deployment Checklist

### Infrastructure Requirements

- [ ] Docker Engine 20.10+ installed
- [ ] Docker Compose 2.0+ installed
- [ ] Portainer CE/EE running (optional but recommended)
- [ ] Reverse proxy (Traefik/Nginx) configured
- [ ] SSL certificates available
- [ ] Domain name configured
- [ ] Firewall rules configured

### Security Requirements

- [ ] Strong API keys generated
- [ ] Environment variables secured
- [ ] Network isolation configured
- [ ] Backup strategy implemented
- [ ] Monitoring solution ready

## 🚀 Deployment Methods

### Method 1: Portainer Stack (Recommended)

#### Step 1: Prepare Environment

1. **Download deployment files:**
   ```bash
   wget https://github.com/wwwjorge/langextract-api/releases/latest/download/langextract-deployment.tar.gz
   tar -xzf langextract-deployment.tar.gz
   cd deployment/
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   nano .env  # Edit with your values
   ```

#### Step 2: Deploy via Portainer

1. **Access Portainer UI**
   - Navigate to your Portainer instance
   - Go to "Stacks" → "Add stack"

2. **Create Stack**
   - Name: `langextract-api-prod`
   - Build method: "Web editor"
   - Copy content from `portainer-stack.yml`

3. **Configure Environment Variables**
   ```env
   # Required Variables
   API_KEY=your-super-secure-api-key-here
   CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
   DOMAIN=api.yourdomain.com
   
   # API Keys
   OPENAI_API_KEY=sk-your-openai-key
   GEMINI_API_KEY=your-gemini-key
   CLOUDFLARE_API_TOKEN=your-cloudflare-token
   CLOUDFLARE_ACCOUNT_ID=your-account-id
   
   # Resource Limits
   CPU_LIMIT=2.0
   MEMORY_LIMIT=2G
   
   # Stack Configuration
   STACK_NAME=prod
   ENVIRONMENT=production
   MAINTAINER_EMAIL=admin@yourdomain.com
   ```

4. **Deploy Stack**
   - Click "Deploy the stack"
   - Monitor deployment logs
   - Verify health checks pass

#### Step 3: Verify Deployment

```bash
# Check container status
docker ps | grep langextract

# Check health
curl -f https://api.yourdomain.com/health

# Check logs
docker logs langextract-api-prod
```

### Method 2: Docker Compose

#### Step 1: Prepare Server

```bash
# Clone repository
git clone https://github.com/wwwjorge/langextract-api.git
cd langextract-api

# Make scripts executable
chmod +x scripts/prepare-deploy.sh
```

#### Step 2: Configure Environment

```bash
# Copy and edit environment file
cp .env.example .env
nano .env

# Validate configuration
./scripts/prepare-deploy.sh --check-only
```

#### Step 3: Deploy

```bash
# Production deployment
./scripts/prepare-deploy.sh

# Or manual deployment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Method 3: Manual Docker Run

```bash
# Create network
docker network create langextract-network

# Create volumes
docker volume create langextract-uploads-prod
docker volume create langextract-logs-prod

# Run container
docker run -d \
  --name langextract-api-prod \
  --network langextract-network \
  -p 8000:8000 \
  -v langextract-uploads-prod:/app/uploads \
  -v langextract-logs-prod:/app/logs \
  -e API_KEY="your-api-key" \
  -e CORS_ORIGINS="https://yourdomain.com" \
  --restart unless-stopped \
  ghcr.io/wwwjorge/langextract-api:latest
```

## 🔧 Configuration Details

### Environment Variables

#### Core Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `API_KEY` | ✅ | - | API authentication key |
| `CORS_ORIGINS` | ✅ | - | Allowed CORS origins |
| `DOMAIN` | ✅ | - | Your domain name |
| `DEFAULT_MODEL` | ❌ | `llama3.2:3b` | Default AI model |
| `LOG_LEVEL` | ❌ | `INFO` | Logging level |

#### Provider API Keys

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | ❌ | OpenAI API key |
| `GEMINI_API_KEY` | ❌ | Google Gemini API key |
| `ANTHROPIC_API_KEY` | ❌ | Anthropic API key |
| `CLOUDFLARE_API_TOKEN` | ❌ | Cloudflare API token |
| `CLOUDFLARE_ACCOUNT_ID` | ❌ | Cloudflare account ID |

#### Security Headers

| Variable | Default | Description |
|----------|---------|-------------|
| `X_FRAME_OPTIONS` | `SAMEORIGIN` | X-Frame-Options header |
| `REFERRER_POLICY` | `strict-origin-when-cross-origin` | Referrer policy |
| `X_XSS_PROTECTION` | `1; mode=block` | XSS protection |
| `X_CONTENT_TYPE_OPTIONS` | `nosniff` | Content type options |

### Resource Limits

#### Production Recommendations

```yaml
# High Traffic
CPU_LIMIT=4.0
MEMORY_LIMIT=4G
CPU_RESERVATION=1.0
MEMORY_RESERVATION=1G

# Medium Traffic
CPU_LIMIT=2.0
MEMORY_LIMIT=2G
CPU_RESERVATION=0.5
MEMORY_RESERVATION=512M

# Low Traffic
CPU_LIMIT=1.0
MEMORY_LIMIT=1G
CPU_RESERVATION=0.25
MEMORY_RESERVATION=256M
```

## 🔒 Security Hardening

### Container Security

1. **Non-root execution**
   ```dockerfile
   USER appuser:appuser
   ```

2. **Read-only filesystem**
   ```yaml
   read_only: true
   tmpfs:
     - /tmp:noexec,nosuid,size=100m
   ```

3. **Security options**
   ```yaml
   security_opt:
     - no-new-privileges:true
   ```

### Network Security

1. **Isolated network**
   ```yaml
   networks:
     langextract-network:
       driver: bridge
       ipam:
         config:
           - subnet: 172.22.0.0/16
   ```

2. **Firewall rules**
   ```bash
   # Allow only necessary ports
   ufw allow 80/tcp
   ufw allow 443/tcp
   ufw deny 8000/tcp  # Block direct API access
   ```

### API Security

1. **Strong API keys**
   ```bash
   # Generate secure API key
   openssl rand -hex 32
   ```

2. **Rate limiting**
   ```yaml
   # Traefik middleware
   - "traefik.http.middlewares.api-ratelimit.ratelimit.average=100"
   - "traefik.http.middlewares.api-ratelimit.ratelimit.burst=200"
   ```

## 📊 Monitoring & Observability

### Health Checks

```bash
# Manual health check
curl -f https://api.yourdomain.com/health

# Detailed health info
curl https://api.yourdomain.com/health | jq
```

### Log Monitoring

```bash
# View real-time logs
docker logs -f langextract-api-prod

# Export logs
docker logs --since="1h" langextract-api-prod > api-logs.txt
```

### Metrics Collection

```bash
# Container stats
docker stats langextract-api-prod

# Resource usage
docker exec langextract-api-prod ps aux
docker exec langextract-api-prod df -h
```

### Alerting Setup

1. **Health check monitoring**
   ```bash
   # Cron job for health checks
   */5 * * * * curl -f https://api.yourdomain.com/health || echo "API DOWN" | mail -s "API Alert" admin@yourdomain.com
   ```

2. **Log monitoring**
   ```bash
   # Monitor error logs
   docker logs langextract-api-prod 2>&1 | grep -i error
   ```

## 🔄 Maintenance & Updates

### Regular Updates

```bash
# Pull latest image
docker pull ghcr.io/wwwjorge/langextract-api:latest

# Update via Portainer
# 1. Go to Stacks → langextract-api-prod
# 2. Click "Update the stack"
# 3. Enable "Re-pull image and redeploy"
# 4. Click "Update"

# Update via Docker Compose
docker-compose pull
docker-compose up -d
```

### Backup Strategy

```bash
# Backup volumes
docker run --rm \
  -v langextract-uploads-prod:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/uploads-$(date +%Y%m%d).tar.gz /data

# Backup configuration
cp .env .env.backup.$(date +%Y%m%d)
cp docker-compose.yml docker-compose.yml.backup.$(date +%Y%m%d)
```

### Rollback Procedure

```bash
# Rollback to previous version
docker tag ghcr.io/wwwjorge/langextract-api:latest ghcr.io/wwwjorge/langextract-api:backup
docker pull ghcr.io/wwwjorge/langextract-api:v1.0.0
docker tag ghcr.io/wwwjorge/langextract-api:v1.0.0 ghcr.io/wwwjorge/langextract-api:latest
docker-compose up -d
```

## 🐛 Troubleshooting

### Common Issues

#### Container Won't Start

```bash
# Check logs
docker logs langextract-api-prod

# Check configuration
docker-compose config

# Validate environment
env | grep -E '^(API_|CORS_|OPENAI_|GEMINI_)'
```

#### Health Check Failures

```bash
# Test internal health check
docker exec langextract-api-prod curl -f http://localhost:8000/health

# Check port binding
netstat -tlnp | grep 8000

# Check container networking
docker network inspect langextract-network
```

#### Performance Issues

```bash
# Check resource usage
docker stats langextract-api-prod

# Check disk space
df -h
docker system df

# Clean up unused resources
docker system prune -f
```

#### SSL/TLS Issues

```bash
# Test SSL certificate
openssl s_client -connect api.yourdomain.com:443 -servername api.yourdomain.com

# Check Traefik logs
docker logs traefik

# Verify DNS resolution
nslookup api.yourdomain.com
```

### Emergency Procedures

#### Service Recovery

```bash
# Quick restart
docker restart langextract-api-prod

# Full redeploy
docker-compose down
docker-compose up -d

# Emergency rollback
docker run -d --name langextract-api-emergency \
  -p 8000:8000 \
  -e API_KEY="$API_KEY" \
  ghcr.io/wwwjorge/langextract-api:stable
```

#### Data Recovery

```bash
# Restore from backup
docker run --rm \
  -v langextract-uploads-prod:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/uploads-20240101.tar.gz -C /
```

## 📞 Support

For production support:

- **Critical Issues**: Create GitHub issue with "critical" label
- **General Support**: GitHub Discussions
- **Security Issues**: Email security@yourdomain.com
- **Documentation**: Check README.md and API docs

## 📋 Post-Deployment Checklist

- [ ] Health checks passing
- [ ] SSL certificate valid
- [ ] API endpoints responding
- [ ] Logs being collected
- [ ] Monitoring alerts configured
- [ ] Backup strategy implemented
- [ ] Documentation updated
- [ ] Team notified of deployment
- [ ] Performance baseline established
- [ ] Security scan completed

---

**Remember**: Always test deployments in a staging environment before production!