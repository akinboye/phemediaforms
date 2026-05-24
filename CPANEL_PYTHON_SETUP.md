# Using cPanel Python Setup (Passenger)

Step-by-step guide to deploy the PHEMEDAA Forms Portal using cPanel's built-in Python App Manager.

## What is cPanel Python Setup?

cPanel's Python App Manager (powered by Passenger) automatically manages your Python application, including:
- Virtual environment creation
- Dependency installation
- Auto-restart on crashes
- Process monitoring
- Easy updates

## Prerequisites

✓ cPanel access  
✓ SSH access enabled  
✓ Python 3.7+ available on your hosting  
✓ Application already cloned to cPanel  

## Step 1: Access cPanel Python App Manager

1. **Log into cPanel**
2. Go to: **Software** → **Setup Python App**
   - (Or search for "Python" in cPanel search bar)
   - Alternative names: "Node.js App", "Setup Node.js App"

If you don't see it, contact your hosting provider - it must be installed.

## Step 2: Create a New Python Application

### Option A: Automatic Setup (Easiest)

Click **Create Application** and fill in:

| Field | Value |
|-------|-------|
| **Python Version** | 3.9+ (select latest available) |
| **Application Root** | `/home/username/public_html/phemediaforms` |
| **Application Startup File** | `wsgi.py` |
| **Application Environment** | `production` |
| **Application URL** | `yourdomain.com` (or subdomain) |

Then click **Create**

### Option B: Manual Configuration

If "Create Application" isn't available:

1. **Create Application Root Directory**:
```bash
mkdir -p ~/public_html/phemediaforms
cd ~/public_html/phemediaforms
git clone https://github.com/akinboye/phemediaforms.git .
```

2. **Create `wsgi.py` file** (required for cPanel):
```bash
cat > wsgi.py << 'EOF'
"""
WSGI Application Entry Point for cPanel Passenger
"""
import sys
import os

# Add project to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Load application
from app import app as application

if __name__ == '__main__':
    application.run()
EOF
```

3. **Create `tmp/restart.txt`** (for app restart):
```bash
mkdir -p tmp
touch tmp/restart.txt
```

4. **Set Permissions**:
```bash
chmod 755 ~/public_html/phemediaforms
chmod 755 ~/public_html/phemediaforms/tmp
chmod 644 ~/public_html/phemediaforms/wsgi.py
```

## Step 3: cPanel Automatic Setup Process

When you click "Create" in cPanel, it will automatically:

```
✓ Create Python virtual environment
✓ Install pip/setuptools/wheel
✓ Create configuration files:
  - /etc/passenger/standalone/*/passenger.conf
  - .htaccess (for routing)
✓ Install Passenger application server
✓ Start monitoring your app
✓ Set up auto-restart on crash
```

**You'll see output like:**
```
Successfully created application
Application User: nobody
Application Group: nogroup
Application Root: /home/username/public_html/phemediaforms
Startup File: wsgi.py
Node Version: (shows Python version)
Status: active
```

## Step 4: Install Python Dependencies

cPanel provides a Package Manager to install dependencies.

### Method 1: Via cPanel (Easiest)

1. In **Setup Python App**, find your application
2. Click **Edit** next to your app
3. Click **Run "pip install" Requirements**
   - It will read `requirements.txt` and install all packages
   - Shows progress: "Installing packages..."

### Method 2: Via SSH Terminal

```bash
# Navigate to your app
cd ~/public_html/phemediaforms

# Activate virtual environment (cPanel created it)
source venv/bin/activate

# Install requirements
pip install --upgrade pip
pip install -r requirements.txt
```

**What gets installed:**
```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
SQLAlchemy==2.0.48
Flask-WTF==1.2.1
PyMySQL==1.1.0
pymysql==1.1.0
(+ other dependencies)
```

## Step 5: Configure Database

### Via SSH:

```bash
cd ~/public_html/phemediaforms
source venv/bin/activate

# Create database and tables
python setup_mysql.py

# Create admin users
python init_admins.py
```

**Output should show:**
```
✓ Database 'phemedaa_forms' created
✓ All tables created successfully
✓ SuperAdmin created (admin / admin123)
✓ Admin user created (user / user123)
```

## Step 6: Configure .htaccess (Important)

cPanel should create this automatically, but verify it exists:

**File: `/home/username/public_html/phemediaforms/.htaccess`**

```apache
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteRule ^(.*)$ index.html [L]
</IfModule>

# Passenger configuration
<IfModule mod_passenger.c>
  PassengerEnabled on
  PassengerAppType wsgi
  PassengerStartupFile wsgi.py
  PassengerAppRoot /home/username/public_html/phemediaforms
</IfModule>
```

## Step 7: View Application Status

### In cPanel:

1. Go to **Setup Python App**
2. Click **Details** for your application
3. See:
   - **Status**: Green = Running
   - **PID**: Process ID
   - **Memory**: Usage
   - **Uptime**: How long it's been running

### Via SSH:

```bash
# Check if Passenger process is running
ps aux | grep passenger

# View application logs
tail -f ~/public_html/phemediaforms/tmp/passenger.*/error.log

# View startup messages
journalctl -u passenger
```

## Step 8: Test Your Application

### Visit Your Application:
```
https://yourdomain.com
```

### Check Home Page:
- Should see form selection interface
- All form links working

### Test Admin Login:
```
URL: https://yourdomain.com/admin_login
Username: admin
Password: admin123
```

### Verify Database Connection:
```bash
# Via SSH, test MySQL connection
cd ~/public_html/phemediaforms
source venv/bin/activate
python -c "from app import db; print('✓ Database connection OK')"
```

## Step 9: Restart Application

### Method 1: Via cPanel UI
1. Go to **Setup Python App**
2. Click **Edit** for your application
3. Click **Restart Application**

### Method 2: Via SSH (Touch restart file)
```bash
touch ~/public_html/phemediaforms/tmp/restart.txt
```

The application will restart automatically in ~1 second.

## Step 10: Configure Email (Optional but Recommended)

### Update Email Settings

Edit `app.py` to use cPanel's mail server:

```python
# Option 1: Use external PHEMEDAA mail server
MAIL_SERVER = 'mail.phemediaa.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = 'admin@phemediaa.com'
MAIL_PASSWORD = '@phemediaadmin123456_'

# Option 2: Use cPanel local mail
MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_USE_TLS = False
MAIL_USERNAME = 'your-email@yourdomain.com'
MAIL_PASSWORD = 'your-email-password'
```

Then restart the application:
```bash
touch ~/public_html/phemediaforms/tmp/restart.txt
```

## Managing Your Application

### View Active Applications

In **Setup Python App**, you'll see a list of all running applications:

```
Application Root               | Python | Status | Actions
─────────────────────────────────────────────────────────
/home/username/public_html/... | 3.9    | ▲      | Edit | Delete | Restart
```

### Edit Application Settings

Click **Edit** to:
- Change Python version
- Change startup file
- View environment variables
- Manage dependencies
- View logs

### Delete Application

Click **Delete** to remove the application from cPanel management. **Note**: Files remain, only cPanel management is removed.

## Troubleshooting

### Application Won't Start

**Check error log:**
```bash
tail -f ~/public_html/phemediaforms/tmp/passenger.*/error.log
```

**Common errors:**
- Missing `wsgi.py` → Create it
- Missing dependencies → Run `pip install -r requirements.txt`
- Database connection error → Check MySQL credentials in `app.py`
- Permission issues → Run `chmod 755` on directories

### Blank Page or 500 Error

```bash
# View detailed error
cat ~/public_html/phemediaforms/tmp/passenger.*/error.log

# Or check cPanel error log
tail -f ~/logs/error_log
```

### Dependencies Not Installed

```bash
# Via SSH, reinstall
source ~/public_html/phemediaforms/venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

### Application Slow or High Memory

**Check processes:**
```bash
ps aux | grep python
ps aux | grep passenger
```

**Restart the application:**
```bash
touch ~/public_html/phemediaforms/tmp/restart.txt
```

### MySQL Connection Issues

```bash
# Test connection
source ~/public_html/phemediaforms/venv/bin/activate
python << EOF
from app import app, db
with app.app_context():
    try:
        db.engine.execute("SELECT 1")
        print("✓ MySQL connection OK")
    except Exception as e:
        print(f"✗ Connection error: {e}")
EOF
```

## Performance Tuning

### Set Environment Variables

Create `~/public_html/phemediaforms/.env`:

```
FLASK_ENV=production
PYTHONUNBUFFERED=1
WORKERS=4
```

Then restart:
```bash
touch ~/public_html/phemediaforms/tmp/restart.txt
```

### Monitor Resources

In cPanel:
1. Go to **Resource Monitor**
2. Track CPU and memory usage
3. Optimize if needed

## Updating the Application

### Pull Latest Changes

```bash
cd ~/public_html/phemediaforms
git pull origin master
source venv/bin/activate
pip install -r requirements.txt
touch tmp/restart.txt
```

### Rollback Previous Version

```bash
cd ~/public_html/phemediaforms
git log --oneline  # View commit history
git checkout <commit-hash>  # Go back to previous version
touch tmp/restart.txt
```

## Viewing Logs

### Application Logs

```bash
# Passenger error log
tail -f ~/public_html/phemediaforms/tmp/passenger.*/error.log

# Passenger access log
tail -f ~/public_html/phemediaforms/tmp/passenger.*/access.log
```

### cPanel Logs

```bash
# Error log
tail -f ~/logs/error_log

# Access log
tail -f ~/logs/access_log
```

### View in cPanel

1. Go to **Logs** → **Error Log** or **Access Log**
2. Filter by domain
3. View in real-time or download

## Backup and Recovery

### Via cPanel

1. **Go to Backups**
2. **Download a Backup**
3. Select files and database to backup
4. Download to safe location

### Via SSH

```bash
# Backup application
tar -czf ~/phemediaa_forms_backup.tar.gz ~/public_html/phemediaforms

# Backup database
mysqldump -u user -p phemedaa_forms > ~/phemedaa_forms.sql

# Download to local machine
# Use FileZilla or SCP to download .tar.gz and .sql files
```

## Security Checklist

✓ Change default admin password  
✓ Enable HTTPS (via AutoSSL)  
✓ Set strong SECRET_KEY in `app.py`  
✓ Configure firewall (if available)  
✓ Enable two-factor authentication  
✓ Regular backups (weekly minimum)  
✓ Monitor error logs regularly  
✓ Update dependencies: `pip install --upgrade -r requirements.txt`

## Comparison: cPanel Python App vs Manual

| Feature | cPanel Python App | Manual Setup |
|---------|-----------------|--------------|
| Virtual Environment | Auto-created | Manual |
| Dependencies | pip install from UI | Manual via SSH |
| Starting/Stopping | Via UI | Manual |
| Auto-restart | ✓ Built-in | Need cron job |
| Monitoring | ✓ Real-time | Manual |
| Logs | ✓ Easy access | Terminal only |
| Easy Update | ✓ Yes | Complex |
| **Recommended** | ✓ YES | No |

## Quick Reference

```bash
# SSH to server
ssh username@yourdomain.com

# Activate virtual environment
source ~/public_html/phemediaforms/venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run setup scripts
python setup_mysql.py
python init_admins.py

# Restart app
touch ~/public_html/phemediaforms/tmp/restart.txt

# View logs
tail -f ~/public_html/phemediaforms/tmp/passenger.*/error.log

# Test database
python -c "from app import db; print('DB OK')"
```

## Support Resources

- **cPanel Docs**: https://docs.cpanel.net/
- **Passenger Docs**: https://www.phusionpassenger.com/docs/
- **Flask Docs**: https://flask.palletsprojects.com/
- **Your Application**: https://github.com/akinboye/phemediaforms

## Next Steps After Deployment

1. ✓ Test all forms
2. ✓ Verify email notifications
3. ✓ Test admin approval workflow
4. ✓ Check error logs
5. ✓ Set up monitoring
6. ✓ Configure backups
7. ✓ Change default passwords
8. ✓ Enable HTTPS

---

**Questions?** Contact info@phemediaa.com
