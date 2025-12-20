# ☁️ AWS Deployment Guide

## Overview

This guide covers deploying your Hospitality AI Agent to AWS in production.

**Estimated Time:** 30-60 minutes
**Cost:** $25-100/month depending on traffic

---

## 🚀 **Option 1: Elastic Beanstalk (Recommended)**

### Prerequisites

1. **AWS Account** - Sign up at https://aws.amazon.com/
2. **EB CLI** - Install with:
   ```bash
   pip install awsebcli
   ```
3. **Environment Variables** - Your `.env` file ready

---

### Step 1: Initialize Elastic Beanstalk

```bash
# In your project root (Terminal 3):
eb init

# You'll be prompted:
# - Select region: us-east-1 (or your preferred region)
# - Application name: hospitality-ai-agent
# - Platform: Python 3.12
# - Do you want to set up SSH: Yes (recommended)
```

---

### Step 2: Create Environment

```bash
eb create production-env

# This will:
# - Create EC2 instance
# - Set up load balancer
# - Configure security groups
# - Deploy your app
```

**Wait 5-10 minutes** for environment creation.

---

### Step 3: Configure Environment Variables

```bash
# Set your Django secret key
eb setenv DJANGO_SECRET_KEY="your-secret-key-here"

# Set debug to false
eb setenv DJANGO_DEBUG="False"

# Set allowed hosts
eb setenv DJANGO_ALLOWED_HOSTS="your-domain.com,*.elasticbeanstalk.com"

# Set database URL (after RDS setup)
eb setenv DATABASE_URL="postgresql://user:pass@host:5432/dbname"
```

---

### Step 4: Set Up Database (RDS)

**Option A: Through AWS Console**
1. Go to RDS in AWS Console
2. Create PostgreSQL database
3. Choose Free Tier eligible options
4. Note down connection details

**Option B: Through EB CLI**
```bash
eb create-rds
# Follow prompts to create database
```

---

### Step 5: Collect Static Files

Update `config/settings.py`:

```python
# Add at the end of settings.py
if not DEBUG:
    STATIC_ROOT = BASE_DIR / "staticfiles"
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
```

Then:
```bash
python manage.py collectstatic --noinput
```

---

### Step 6: Deploy

```bash
# Deploy your app
eb deploy

# Open in browser
eb open
```

---

### Step 7: Run Migrations

```bash
# SSH into your instance
eb ssh

# Run migrations
cd /var/app/current
source /var/app/venv/*/bin/activate
python manage.py migrate

# Exit SSH
exit
```

---

### Step 8: Set Up Custom Domain (Optional)

1. Buy domain (Google Domains, Namecheap, etc.)
2. In EB Console, go to your environment
3. Configuration → Load Balancer → Add listener for HTTPS
4. Request SSL certificate through AWS Certificate Manager
5. Update DNS records to point to EB URL

---

## 🏗️ **Option 2: EC2 + RDS (More Control)**

### Architecture

```
┌─────────────────────────────────────┐
│  Route 53 (DNS)                     │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│  Application Load Balancer          │
│  (HTTPS, SSL Certificate)           │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│  EC2 Instance (t3.small)            │
│  - Django App (Gunicorn)            │
│  - Nginx (Reverse Proxy)            │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│  RDS PostgreSQL Database            │
│  (db.t3.micro)                      │
└─────────────────────────────────────┘
```

---

### Step 1: Launch EC2 Instance

1. **Go to EC2 Dashboard**
2. **Launch Instance**
   - Name: `hospitality-ai-server`
   - AMI: Ubuntu 22.04 LTS
   - Instance type: `t3.small` ($15/month)
   - Key pair: Create new (save the .pem file!)
   - Security group: Allow SSH (22), HTTP (80), HTTPS (443)

---

### Step 2: Connect to EC2

```bash
# From your local machine
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@your-ec2-ip
```

---

### Step 3: Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3.12 python3.12-venv python3-pip nginx postgresql-client git -y

# Install supervisor (process manager)
sudo apt install supervisor -y
```

---

### Step 4: Clone Your Repository

```bash
cd /home/ubuntu
git clone https://github.com/yourusername/hospitality_ai_agent.git
cd hospitality_ai_agent
```

---

### Step 5: Set Up Python Environment

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

---

### Step 6: Configure Environment Variables

```bash
sudo nano /etc/environment

# Add these lines:
DJANGO_SECRET_KEY="your-secret-key"
DJANGO_DEBUG="False"
DATABASE_URL="postgresql://user:pass@rds-endpoint:5432/dbname"
```

Reload:
```bash
source /etc/environment
```

---

### Step 7: Set Up Gunicorn

Create `/etc/supervisor/conf.d/hospitality-ai.conf`:

```ini
[program:hospitality-ai]
directory=/home/ubuntu/hospitality_ai_agent
command=/home/ubuntu/hospitality_ai_agent/venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3
user=ubuntu
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/hospitality-ai.log
```

Start:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start hospitality-ai
```

---

### Step 8: Configure Nginx

Create `/etc/nginx/sites-available/hospitality-ai`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /static/ {
        alias /home/ubuntu/hospitality_ai_agent/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/hospitality-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

### Step 9: Set Up SSL (HTTPS)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is set up automatically
```

---

### Step 10: Set Up RDS Database

1. **Go to RDS Dashboard**
2. **Create Database**
   - Engine: PostgreSQL 15
   - Templates: Free tier (for testing)
   - DB instance identifier: `hospitality-ai-db`
   - Master username: `postgres`
   - Master password: (set a strong password)
   - VPC: Same as EC2
   - Public access: No
   - Security group: Allow PostgreSQL (5432) from EC2

3. **Get connection details**
4. **Update DATABASE_URL** in environment

---

### Step 11: Run Migrations

```bash
cd /home/ubuntu/hospitality_ai_agent
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
```

---

### Step 12: Create Superuser

```bash
python manage.py createsuperuser
```

---

## 📊 **Cost Breakdown**

### Elastic Beanstalk (Simple)
- **EC2 t3.small:** $15/month
- **RDS db.t3.micro:** $15/month
- **Load Balancer:** $18/month
- **Data transfer:** $5-10/month
- **TOTAL:** ~$53-63/month

### EC2 + RDS (DIY)
- **EC2 t3.small:** $15/month
- **RDS db.t3.micro:** $15/month
- **EBS storage:** $2/month
- **Data transfer:** $5/month
- **TOTAL:** ~$37/month

### Free Tier (First Year)
- 750 hours EC2 t2.micro (free)
- 750 hours RDS db.t2.micro (free)
- 5GB storage (free)
- **TOTAL:** $0-5/month

---

## 🔒 **Security Checklist**

- [ ] DEBUG = False in production
- [ ] SECRET_KEY from environment variable (not hardcoded)
- [ ] ALLOWED_HOSTS configured properly
- [ ] HTTPS enabled (SSL certificate)
- [ ] Database has strong password
- [ ] SSH key-based authentication only
- [ ] Firewall rules (Security Groups) configured
- [ ] Regular backups enabled (RDS automatic backups)
- [ ] Monitoring enabled (CloudWatch)
- [ ] Log aggregation set up

---

## 🔄 **Deployment Workflow**

### For Elastic Beanstalk:
```bash
# 1. Make changes locally
git add .
git commit -m "Update feature"

# 2. Deploy to AWS
eb deploy

# 3. Verify
eb open
```

### For EC2:
```bash
# 1. SSH to server
ssh -i key.pem ubuntu@your-ip

# 2. Pull changes
cd /home/ubuntu/hospitality_ai_agent
git pull origin main

# 3. Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate
python manage.py collectstatic --noinput

# 5. Restart app
sudo supervisorctl restart hospitality-ai
```

---

## 📈 **Monitoring**

### CloudWatch (AWS)
- Set up alarms for:
  - High CPU usage (>80%)
  - High memory usage (>80%)
  - Error rates
  - Response time

### Application Monitoring
Add to `requirements.txt`:
```
sentry-sdk>=1.38.0  # Error tracking
django-prometheus>=2.3.1  # Metrics
```

---

## 🆘 **Troubleshooting**

### App won't start
```bash
# Check logs
eb logs  # For Elastic Beanstalk

# OR
sudo tail -f /var/log/hospitality-ai.log  # For EC2
```

### Database connection fails
- Check security group rules
- Verify DATABASE_URL format
- Test connection: `psql $DATABASE_URL`

### Static files not loading
```bash
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

### SSL certificate issues
```bash
sudo certbot renew --dry-run
```

---

## 🎯 **Quick Start Recommendation**

**For MVP (fastest):**
1. Use **Elastic Beanstalk**
2. Skip RDS initially (use SQLite)
3. Deploy in 30 minutes
4. Add RDS later when needed

**For production (best):**
1. Use **EC2 + RDS**
2. Set up monitoring
3. Configure backups
4. Use proper CI/CD

---

## 📚 **Additional Resources**

- AWS Free Tier: https://aws.amazon.com/free/
- Django Deployment Checklist: https://docs.djangoproject.com/en/stable/howto/deployment/checklist/
- AWS Well-Architected Framework: https://aws.amazon.com/architecture/well-architected/

---

**Need help?** Come back to this terminal and ask Claude! 🚀
