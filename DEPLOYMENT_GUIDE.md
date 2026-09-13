# 🚀 SentinelOneWay - Complete Deployment Guide

## Overview

This guide covers **multiple deployment options** for your SentinelOneWay MVP:

1. **Local Production Build** - Test production build locally
2. **Docker Deployment** - Containerized deployment (easiest)
3. **Cloud Deployment** - AWS, Azure, GCP, Heroku
4. **VPS Deployment** - DigitalOcean, Linode, Vultr

---

## 📋 Pre-Deployment Checklist

### ✅ Before Deploying:

- [ ] All features tested locally and working
- [ ] Frontend builds without errors
- [ ] Backend runs without errors
- [ ] Database has sample data
- [ ] Environment variables documented
- [ ] Security review completed
- [ ] Performance testing done

### ✅ System Requirements:

**Minimum:**
- **CPU:** 2 cores
- **RAM:** 2GB
- **Storage:** 10GB
- **OS:** Linux (Ubuntu 20.04+), Windows Server, or MacOS

**Recommended:**
- **CPU:** 4 cores
- **RAM:** 4GB
- **Storage:** 20GB
- **OS:** Ubuntu 22.04 LTS

---

## 🎯 Option 1: Local Production Build

**Best for:** Testing production build before cloud deployment

### Step 1: Build Frontend

```bash
cd C:/Users/Vimalraj/SentinelOneWay/frontend

# Install dependencies (if not done)
npm install

# Build for production
npm run build

# This creates: dist/ folder with optimized files
```

**Output:**
```
frontend/dist/
  ├── index.html
  ├── assets/
  │   ├── index-[hash].js
  │   ├── index-[hash].css
  │   └── ...
  └── ...
```

### Step 2: Test Production Build Locally

```bash
# Preview production build
npm run preview

# Opens at: http://localhost:4173
```

### Step 3: Configure Backend for Production

**File:** `backend/.env.production`

```env
# Database
DATABASE_URL=sqlite:///./sentineloneway_production.db

# CORS - Add production domain
CORS_ORIGINS=http://localhost:4173,https://yourdomain.com

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
```

### Step 4: Run Backend in Production Mode

```bash
cd C:/Users/Vimalraj/SentinelOneWay/backend

# Activate virtual environment
source venv/Scripts/activate  # Windows Git Bash
# OR
.\venv\Scripts\activate.bat  # Windows CMD

# Run with production settings
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Test:** Open `http://localhost:4173` and verify everything works!

---

## 🐳 Option 2: Docker Deployment (RECOMMENDED)

**Best for:** Easy deployment anywhere (local, cloud, VPS)

### Step 1: Check Docker Files

You already have these files:

```
SentinelOneWay/
├── docker-compose.yml
├── Dockerfile.backend
└── Dockerfile.frontend
```

### Step 2: Create Production Docker Compose

**File:** `docker-compose.production.yml`

```yaml
version: '3.8'

services:
  # Backend Service
  backend:
    build:
      context: ./backend
      dockerfile: ../Dockerfile.backend
    container_name: sentineloneway-backend
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
      - DATABASE_URL=sqlite:///./sentineloneway.db
      - CORS_ORIGINS=http://localhost:3000,http://frontend:3000
    volumes:
      - ./backend/data:/app/data
      - ./backend/models:/app/models
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - sentineloneway-network

  # Frontend Service
  frontend:
    build:
      context: ./frontend
      dockerfile: ../Dockerfile.frontend
    container_name: sentineloneway-frontend
    restart: unless-stopped
    ports:
      - "3000:80"
    environment:
      - VITE_API_BASE_URL=http://localhost:8000
    depends_on:
      - backend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - sentineloneway-network

networks:
  sentineloneway-network:
    driver: bridge

volumes:
  backend-data:
```

### Step 3: Build and Run with Docker

```bash
cd C:/Users/Vimalraj/SentinelOneWay

# Build images
docker-compose -f docker-compose.production.yml build

# Start services
docker-compose -f docker-compose.production.yml up -d

# Check status
docker-compose -f docker-compose.production.yml ps

# View logs
docker-compose -f docker-compose.production.yml logs -f

# Stop services
docker-compose -f docker-compose.production.yml down
```

**Access:**
- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:8000
- **Health Check:** http://localhost:8000/health

### Step 4: Verify Docker Deployment

```bash
# Check containers running
docker ps

# Should see:
# sentineloneway-frontend  (port 3000)
# sentineloneway-backend   (port 8000)

# Test backend
curl http://localhost:8000/health

# Test frontend (open in browser)
http://localhost:3000
```

---

## ☁️ Option 3: Cloud Deployment

### 3A. AWS Deployment

#### Using AWS EC2 (Virtual Machine)

**Step 1: Create EC2 Instance**

1. **Login to AWS Console:** https://console.aws.amazon.com
2. **Launch EC2 Instance:**
   - AMI: Ubuntu 22.04 LTS
   - Instance Type: t3.medium (2 vCPU, 4GB RAM)
   - Storage: 20GB
   - Security Group: Open ports 22, 80, 443, 8000

3. **Connect to Instance:**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

**Step 2: Install Docker on EC2**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose -y

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

**Step 3: Deploy Application**

```bash
# Clone or upload your project
git clone <your-repo-url>
cd SentinelOneWay

# Or use SCP to upload
# scp -i your-key.pem -r SentinelOneWay ubuntu@your-ec2-ip:~/

# Build and run
docker-compose -f docker-compose.production.yml up -d
```

**Step 4: Configure Nginx (Optional)**

```bash
# Install Nginx
sudo apt install nginx -y

# Create Nginx config
sudo nano /etc/nginx/sites-available/sentineloneway
```

**Nginx Config:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/sentineloneway /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**Step 5: Setup SSL (HTTPS)**

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
```

#### Using AWS Elastic Beanstalk (Easier)

**Step 1: Install EB CLI**

```bash
pip install awsebcli
```

**Step 2: Initialize EB**

```bash
cd C:/Users/Vimalraj/SentinelOneWay
eb init -p docker sentineloneway
```

**Step 3: Create Environment**

```bash
eb create sentineloneway-prod
```

**Step 4: Deploy**

```bash
eb deploy
```

**Step 5: Open Application**

```bash
eb open
```

---

### 3B. Azure Deployment

#### Using Azure Container Instances

**Step 1: Install Azure CLI**

Download from: https://aka.ms/installazurecliwindows

**Step 2: Login**

```bash
az login
```

**Step 3: Create Resource Group**

```bash
az group create --name SentinelOneWayRG --location eastus
```

**Step 4: Create Container Registry**

```bash
az acr create --resource-group SentinelOneWayRG \
  --name sentinelonewayregistry --sku Basic
```

**Step 5: Build and Push Images**

```bash
cd C:/Users/Vimalraj/SentinelOneWay

# Login to registry
az acr login --name sentinelonewayregistry

# Build and push backend
docker build -t sentinelonewayregistry.azurecr.io/backend:latest -f Dockerfile.backend ./backend
docker push sentinelonewayregistry.azurecr.io/backend:latest

# Build and push frontend
docker build -t sentinelonewayregistry.azurecr.io/frontend:latest -f Dockerfile.frontend ./frontend
docker push sentinelonewayregistry.azurecr.io/frontend:latest
```

**Step 6: Deploy Container Instances**

```bash
# Deploy backend
az container create --resource-group SentinelOneWayRG \
  --name sentineloneway-backend \
  --image sentinelonewayregistry.azurecr.io/backend:latest \
  --cpu 2 --memory 4 \
  --ports 8000 \
  --dns-name-label sentineloneway-api

# Deploy frontend
az container create --resource-group SentinelOneWayRG \
  --name sentineloneway-frontend \
  --image sentinelonewayregistry.azurecr.io/frontend:latest \
  --cpu 1 --memory 2 \
  --ports 80 \
  --dns-name-label sentineloneway-app
```

**Access:**
- Frontend: http://sentineloneway-app.eastus.azurecontainer.io
- Backend: http://sentineloneway-api.eastus.azurecontainer.io:8000

---

### 3C. Google Cloud Platform (GCP)

#### Using Cloud Run

**Step 1: Install gcloud CLI**

Download from: https://cloud.google.com/sdk/docs/install

**Step 2: Login and Setup**

```bash
gcloud auth login
gcloud config set project your-project-id
```

**Step 3: Build and Deploy Backend**

```bash
cd C:/Users/Vimalraj/SentinelOneWay/backend

# Build image
gcloud builds submit --tag gcr.io/your-project-id/sentineloneway-backend

# Deploy to Cloud Run
gcloud run deploy sentineloneway-backend \
  --image gcr.io/your-project-id/sentineloneway-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2
```

**Step 4: Build and Deploy Frontend**

```bash
cd C:/Users/Vimalraj/SentinelOneWay/frontend

# Update API URL in build
# Edit .env.production: VITE_API_BASE_URL=<backend-cloud-run-url>

# Build image
gcloud builds submit --tag gcr.io/your-project-id/sentineloneway-frontend

# Deploy to Cloud Run
gcloud run deploy sentineloneway-frontend \
  --image gcr.io/your-project-id/sentineloneway-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi
```

---

### 3D. Heroku (Simplest Cloud Option)

**Step 1: Install Heroku CLI**

Download from: https://devcenter.heroku.com/articles/heroku-cli

**Step 2: Login**

```bash
heroku login
```

**Step 3: Create Apps**

```bash
cd C:/Users/Vimalraj/SentinelOneWay

# Create backend app
heroku create sentineloneway-backend

# Create frontend app
heroku create sentineloneway-frontend
```

**Step 4: Deploy Backend**

```bash
cd backend

# Create Procfile
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Push to Heroku
git init
git add .
git commit -m "Deploy backend"
heroku git:remote -a sentineloneway-backend
git push heroku master
```

**Step 5: Deploy Frontend**

```bash
cd frontend

# Build static files
npm run build

# Create static.json for Heroku
echo '{
  "root": "dist/",
  "clean_urls": true,
  "routes": {
    "/**": "index.html"
  }
}' > static.json

# Deploy
git init
git add .
git commit -m "Deploy frontend"
heroku git:remote -a sentineloneway-frontend
heroku buildpacks:add heroku/nodejs
git push heroku master
```

---

## 🖥️ Option 4: VPS Deployment

**Best for:** Full control, cost-effective

### Using DigitalOcean Droplet

**Step 1: Create Droplet**

1. Go to: https://www.digitalocean.com
2. Create Droplet:
   - **Image:** Ubuntu 22.04
   - **Plan:** Basic ($12/month - 2GB RAM, 2 CPUs)
   - **Datacenter:** Closest to your users
   - **Authentication:** SSH Key

**Step 2: Connect to Droplet**

```bash
ssh root@your-droplet-ip
```

**Step 3: Initial Server Setup**

```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Install Nginx
apt install nginx -y

# Install Certbot (SSL)
apt install certbot python3-certbot-nginx -y
```

**Step 4: Upload Project**

```bash
# From your local machine
scp -r C:/Users/Vimalraj/SentinelOneWay root@your-droplet-ip:/opt/

# Or use Git
ssh root@your-droplet-ip
cd /opt
git clone <your-repo-url>
```

**Step 5: Deploy with Docker**

```bash
cd /opt/SentinelOneWay
docker-compose -f docker-compose.production.yml up -d
```

**Step 6: Configure Nginx**

```bash
# Create config
nano /etc/nginx/sites-available/sentineloneway
```

**(Use same Nginx config as AWS section above)**

```bash
# Enable site
ln -s /etc/nginx/sites-available/sentineloneway /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

**Step 7: Setup SSL**

```bash
certbot --nginx -d yourdomain.com
```

**Step 8: Setup Firewall**

```bash
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw enable
```

---

## 🔐 Security Checklist

### Essential Security Steps:

- [ ] **Change default credentials**
- [ ] **Use HTTPS (SSL certificate)**
- [ ] **Setup firewall (ufw, security groups)**
- [ ] **Disable root SSH login**
- [ ] **Use SSH keys (not passwords)**
- [ ] **Setup fail2ban** (prevent brute force)
- [ ] **Regular updates** (system, dependencies)
- [ ] **Environment variables** (never commit secrets)
- [ ] **CORS configuration** (restrict origins)
- [ ] **Rate limiting** (prevent abuse)

### Update Backend Security

**File:** `backend/main.py`

```python
# CORS - Update for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",  # Production frontend
        "http://localhost:5173",    # Local dev (remove in prod)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Update Frontend API URL

**File:** `frontend/.env.production`

```env
VITE_API_BASE_URL=https://api.yourdomain.com
```

---

## 📊 Monitoring & Maintenance

### Setup Monitoring

**1. System Monitoring (DigitalOcean, AWS CloudWatch)**
- CPU usage
- Memory usage
- Disk space
- Network traffic

**2. Application Monitoring**

```bash
# Install monitoring tools
pip install prometheus-client
```

**3. Log Management**

```bash
# View Docker logs
docker-compose logs -f --tail=100

# Setup log rotation
nano /etc/docker/daemon.json
```

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

### Backup Strategy

**Database Backup:**

```bash
# Backup SQLite database
docker exec sentineloneway-backend sqlite3 /app/sentineloneway.db ".backup '/app/backup.db'"

# Download backup
docker cp sentineloneway-backend:/app/backup.db ./backup-$(date +%Y%m%d).db
```

**Automated Backup Script:**

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR=/opt/backups
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
docker exec sentineloneway-backend sqlite3 /app/sentineloneway.db ".backup '/app/backup.db'"
docker cp sentineloneway-backend:/app/backup.db $BACKUP_DIR/backup-$DATE.db

# Keep only last 7 days
find $BACKUP_DIR -name "backup-*.db" -mtime +7 -delete

# Upload to cloud storage (optional)
# aws s3 cp $BACKUP_DIR/backup-$DATE.db s3://your-bucket/
```

**Setup Cron Job:**

```bash
crontab -e

# Add line (backup daily at 2 AM):
0 2 * * * /opt/scripts/backup.sh
```

---

## 🎯 Recommended Deployment Path

### For Demo/Testing:
1. ✅ **Docker Locally** (easiest to setup)
2. ✅ Test all features
3. ✅ Verify performance

### For Production:
1. ✅ **DigitalOcean Droplet** ($12/month)
   - Easy to manage
   - Good performance
   - Full control
   
2. ✅ **AWS EC2** (scalable)
   - Free tier available
   - Professional option
   - Easy to scale

3. ✅ **Heroku** (simplest)
   - Zero DevOps
   - Auto-scaling
   - Higher cost

---

## 📝 Quick Start Deployment (Docker)

**Complete deployment in 5 minutes:**

```bash
# 1. Navigate to project
cd C:/Users/Vimalraj/SentinelOneWay

# 2. Build Docker images
docker-compose build

# 3. Start services
docker-compose up -d

# 4. Check status
docker-compose ps

# 5. View logs
docker-compose logs -f

# 6. Access application
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
```

**Done! Your application is deployed!** 🎉

---

## 🆘 Troubleshooting

### Issue: Frontend can't connect to backend

**Solution:**
```bash
# Check backend is running
curl http://localhost:8000/health

# Check CORS settings in backend/main.py
# Check API URL in frontend/.env
```

### Issue: Database not persisting

**Solution:**
```bash
# Check Docker volumes
docker volume ls

# Ensure volume is mounted in docker-compose.yml
volumes:
  - ./backend/data:/app/data
```

### Issue: Out of memory

**Solution:**
```bash
# Check memory usage
docker stats

# Increase container memory in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G
```

---

## 📚 Additional Resources

- **Docker Documentation:** https://docs.docker.com
- **AWS EC2 Guide:** https://docs.aws.amazon.com/ec2
- **DigitalOcean Tutorials:** https://www.digitalocean.com/community/tutorials
- **Nginx Configuration:** https://nginx.org/en/docs
- **Let's Encrypt SSL:** https://letsencrypt.org

---

## ✅ Deployment Checklist

- [ ] Code is production-ready
- [ ] Environment variables configured
- [ ] Docker images build successfully
- [ ] Services start without errors
- [ ] Frontend can reach backend API
- [ ] WebSocket connections work
- [ ] Database persists data
- [ ] SSL certificate installed
- [ ] Firewall configured
- [ ] Monitoring setup
- [ ] Backups configured
- [ ] Documentation updated

---

## 🎉 Next Steps After Deployment

1. **Test all features** in production environment
2. **Setup monitoring** and alerts
3. **Configure backups** (daily recommended)
4. **Add custom domain** (if not done)
5. **Setup CI/CD** for easy updates
6. **Performance testing** under load
7. **Security audit** and penetration testing

---

**Your SentinelOneWay MVP is ready to deploy!** 🚀

Choose your deployment method and follow the steps above. Docker deployment is recommended for easiest setup!
