# 🔐 Environment Variables Guide

## 📋 Quick Reference

Environment variables are **settings that change based on where your app runs** (development, staging, production). They keep secrets out of your code.

---

## 🎯 **Required Variables for Production**

### 1. **DJANGO_SECRET_KEY** (Critical!)

**What it does:** Cryptographic signing key for Django (sessions, CSRF protection, password resets)

**Development:**
```bash
DJANGO_SECRET_KEY="dev-key-change-in-production-12345"
```

**Production:**
```bash
# Generate a new one:
python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Then use that generated key:
DJANGO_SECRET_KEY="+!j@^xcqejy%k8kx8orm5=0ds_*ua*4p4r3@y33$taup2)b+cd"
```

⚠️ **CRITICAL:**
- Must be **unique** in production
- Must be **secret** (never commit to git!)
- If compromised, **regenerate immediately**

---

### 2. **DJANGO_DEBUG** (Critical!)

**What it does:** Shows detailed error pages with code and stack traces

**Development:**
```bash
DJANGO_DEBUG=True
```

**Production:**
```bash
DJANGO_DEBUG=False
```

⚠️ **CRITICAL:**
- **MUST be False in production** (security risk!)
- When True, exposes your code, database queries, and secrets to users
- Can leak sensitive information to attackers

---

### 3. **DJANGO_ALLOWED_HOSTS** (Critical!)

**What it does:** List of domains allowed to access your app (prevents host header attacks)

**Development:**
```bash
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,*.ngrok-free.app
```

**Production:**
```bash
# Replace with YOUR actual domain(s)
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,*.elasticbeanstalk.com
```

**Format:** Comma-separated list (no spaces!)

⚠️ **CRITICAL:**
- Only add domains you own
- Use `*` only in development (never production!)
- Prevents DNS rebinding attacks

---

### 4. **DATABASE_URL** (Required for Production)

**What it does:** Database connection string

**Development:**
```bash
# Leave blank to use SQLite (default for development)
# DATABASE_URL=
```

**Production:**
```bash
# PostgreSQL format:
DATABASE_URL=postgresql://USERNAME:PASSWORD@HOST:PORT/DATABASE_NAME

# AWS RDS Example:
DATABASE_URL=postgresql://postgres:MySecurePass123@hospitality-db.c9akl53hjse.us-east-1.rds.amazonaws.com:5432/hospitalitydb
```

**Format:** `postgresql://user:password@host:port/database`

⚠️ **Don't use SQLite in production!** It's not designed for concurrent web traffic.

---

## 🔧 **Optional Variables**

### 5. **OPENAI_API_KEY** (If using AI features)

**What it does:** Authenticates with OpenAI API for chat/AI features

```bash
# Get your key at: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-proj-your-actual-key-here-abc123xyz
```

---

### 6. **CORS_ALLOWED_ORIGINS** (If you have a separate frontend)

**What it does:** Controls which frontend domains can make API requests

**Development:**
```bash
# Allow all (for development only)
CORS_ALLOW_ALL_ORIGINS=True
```

**Production:**
```bash
# Only allow your frontend domain
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CORS_ALLOW_ALL_ORIGINS=False
```

---

### 7. **Email Settings** (For notifications)

```bash
# Gmail Example:
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

---

### 8. **AWS S3** (For file uploads)

```bash
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCY
AWS_STORAGE_BUCKET_NAME=hospitality-media
AWS_S3_REGION_NAME=us-east-1
```

---

### 9. **Sentry** (Error tracking - highly recommended!)

```bash
# Free tier: https://sentry.io
SENTRY_DSN=https://abc123@o123456.ingest.sentry.io/7654321
```

---

## 📁 **File Locations**

Your project now has:

```
hospitality_ai_agent/
├── .env                 # Development (active now)
├── .env.production      # Production template
└── .gitignore           # Ensures .env files not committed
```

---

## 🚀 **How to Use**

### **Local Development**

1. **Edit `.env` file:**
   ```bash
   nano .env
   ```

2. **Django automatically reads it** (via `django-environ`)

3. **Restart your server:**
   ```bash
   python3 manage.py runserver
   ```

---

### **AWS Elastic Beanstalk Production**

**Don't use .env files!** Set variables via command line:

```bash
# Set all required variables:
eb setenv \
  DJANGO_SECRET_KEY="+!j@^xcqejy%k8kx8orm5=0ds_*ua*4p4r3@y33$taup2)b+cd" \
  DJANGO_DEBUG=False \
  DJANGO_ALLOWED_HOSTS="yourdomain.com,*.elasticbeanstalk.com" \
  DATABASE_URL="postgresql://user:pass@host:5432/db"

# Verify they're set:
eb printenv
```

---

### **AWS EC2 Production**

Add to `/etc/environment`:

```bash
# SSH to server
ssh -i your-key.pem ubuntu@your-server-ip

# Edit environment file
sudo nano /etc/environment

# Add variables:
DJANGO_SECRET_KEY="+!j@^xcqejy%k8kx8orm5=0ds_*ua*4p4r3@y33$taup2)b+cd"
DJANGO_DEBUG="False"
DJANGO_ALLOWED_HOSTS="yourdomain.com,www.yourdomain.com"
DATABASE_URL="postgresql://user:pass@host:5432/db"

# Save and reload
source /etc/environment

# Restart your app
sudo supervisorctl restart hospitality-ai
```

---

## ✅ **Pre-Deployment Checklist**

Before deploying to production, verify:

- [ ] `DJANGO_SECRET_KEY` is **different** from development
- [ ] `DJANGO_DEBUG=False` (not True!)
- [ ] `DJANGO_ALLOWED_HOSTS` contains your **actual domain**
- [ ] `DATABASE_URL` points to **PostgreSQL** (not SQLite)
- [ ] **No .env files** committed to git
- [ ] All secrets are **secure** and not shared publicly

---

## 🔒 **Security Best Practices**

### ✅ **DO:**
- ✅ Generate a **unique** SECRET_KEY for each environment
- ✅ Use **strong passwords** in DATABASE_URL
- ✅ Keep `.env` files in `.gitignore`
- ✅ Rotate secrets regularly (every 90 days)
- ✅ Use different keys for dev/staging/production

### ❌ **DON'T:**
- ❌ Commit `.env` files to git
- ❌ Share SECRET_KEY publicly
- ❌ Use DEBUG=True in production
- ❌ Use default/example passwords
- ❌ Reuse the development SECRET_KEY in production

---

## 🆘 **Troubleshooting**

### **Error: "SECRET_KEY not set"**

**Cause:** Django can't find DJANGO_SECRET_KEY

**Fix:**
```bash
# Check if .env exists:
ls -la .env

# Check if variable is set:
echo $DJANGO_SECRET_KEY

# Restart server after editing .env
```

---

### **Error: "DisallowedHost at /"**

**Cause:** Your domain not in ALLOWED_HOSTS

**Fix:**
```bash
# Add your domain to .env:
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Or for AWS EB:
eb setenv DJANGO_ALLOWED_HOSTS="yourdomain.com,*.elasticbeanstalk.com"
```

---

### **Database connection fails**

**Cause:** Invalid DATABASE_URL

**Fix:**
```bash
# Verify format:
DATABASE_URL=postgresql://USERNAME:PASSWORD@HOST:PORT/DATABASE

# Test connection:
psql $DATABASE_URL

# Common issues:
# - Wrong port (should be 5432 for PostgreSQL)
# - Special characters in password (URL-encode them)
# - Firewall blocking connection
```

---

## 📚 **Resources**

- [Django Environment Variables](https://docs.djangoproject.com/en/stable/topics/settings/#envvar-DJANGO_SETTINGS_MODULE)
- [django-environ Documentation](https://django-environ.readthedocs.io/)
- [12-Factor App Methodology](https://12factor.net/config)
- [AWS EB Environment Properties](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/environments-cfg-softwaresettings.html)

---

## 🎯 **Quick Commands**

```bash
# Generate new SECRET_KEY
python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Test with production settings locally
export DJANGO_DEBUG=False
export DJANGO_SECRET_KEY="test-key"
python manage.py runserver

# Check which variables Django is using
python manage.py shell
>>> from django.conf import settings
>>> print(settings.DEBUG)
>>> print(settings.SECRET_KEY[:10] + "...")

# AWS EB: View all environment variables
eb printenv

# AWS EB: Set multiple variables at once
eb setenv VAR1="value1" VAR2="value2"

# AWS EB: Remove a variable
eb setenv VAR1=
```

---

**Last Updated:** October 27, 2025
**File Locations:**
- Development: `.env`
- Production Template: `.env.production`
- This Guide: `docs/ENVIRONMENT_VARIABLES.md`
