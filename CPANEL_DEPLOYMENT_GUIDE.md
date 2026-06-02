# cPanel Deployment Guide - Laravel Forms Application

**Target URL:** https://phemediaa.com/forms  
**cPanel User:** mzerisoh  
**Database:** mzerisoh_phemediaaform  
**Server Location:** /home/mzerisoh/public_html/forms  

---

## ✅ PRE-DEPLOYMENT CHECKLIST

Before starting, ensure you have:
- [ ] cPanel access with root/SSH permissions
- [ ] SSH client (or use cPanel Terminal)
- [ ] Git installed on server
- [ ] Composer installed on server
- [ ] PHP 8.1+ installed
- [ ] MySQL database created
- [ ] Domain pointing to correct server

---

## 🚀 COMPLETE DEPLOYMENT STEPS

### Step 1: SSH into Your Server

```bash
# Using Terminal/Command Prompt (Windows/Mac/Linux)
ssh mzerisoh@phemediaa.com

# Or if using cPanel Terminal (Terminal > Terminal):
# (Already logged in as your user)
```

---

### Step 2: Navigate to Web Root

```bash
cd /home/mzerisoh/public_html

# If forms directory exists, remove it first:
rm -rf forms

# Create fresh forms directory
mkdir -p forms
cd forms
```

---

### Step 3: Clone the GitHub Repository

```bash
# Clone your Laravel application
git clone https://github.com/akinboye/phemediaforms.git .

# Verify files were cloned
ls -la

# Should show: laravel/, docs/, uploads/, .env, composer.json, etc.
```

---

### Step 4: Install PHP Dependencies

```bash
# Install composer packages
composer install --no-dev

# This installs all Laravel dependencies (~30-60 seconds)
# Wait for completion message: "Successfully installed X packages"
```

---

### Step 5: Set Up Environment File

```bash
# Copy the environment template
cp .env .env.production

# Edit the .env file with your actual credentials
nano .env
```

**Update the following values in .env:**

```env
APP_NAME="PHEMEDAA Forms Portal"
APP_ENV=production
APP_KEY=base64:YOUR_KEY_HERE    # Will be auto-generated
APP_DEBUG=false
APP_URL=https://phemediaa.com/forms

DB_CONNECTION=mysql
DB_HOST=localhost
DB_PORT=3306
DB_DATABASE=mzerisoh_phemediaaform
DB_USERNAME=mzerisoh_phemediauser
DB_PASSWORD=@phemediaadmin123456_

MAIL_MAILER=smtp
MAIL_HOST=mail.phemediaa.com
MAIL_PORT=465
MAIL_USERNAME=admin@phemediaa.com
MAIL_PASSWORD=@phemediaadmin123456_
MAIL_ENCRYPTION=ssl
MAIL_FROM_ADDRESS="admin@phemediaa.com"
MAIL_FROM_NAME="PHEMEDAA Forms Portal"
```

**Save and exit nano:**
- Press: `Ctrl + X`
- Press: `Y` (confirm)
- Press: `Enter` (save)

---

### Step 6: Generate Application Key

```bash
# Generate a unique application encryption key
php artisan key:generate

# You should see:
# ✅ Application key set successfully.
```

---

### Step 7: Set Up Database

```bash
# Run migrations to create database tables
php artisan migrate --force

# Expected output shows tables created:
# ✅ Migration created successfully
```

**Verify database was created:**
```bash
# Check if tables exist
php artisan migrate:status

# Should show all migrations as "Ran"
```

---

### Step 8: Seed Demo Data (Optional)

```bash
# This creates demo admin accounts
php artisan db:seed --force

# Demo Credentials Created:
# SuperAdmin: admin / admin123
# Admin: user / user123
```

---

### Step 9: Set File Permissions

```bash
# Set proper Laravel permissions
chmod -R 755 storage bootstrap/cache
chmod -R 755 storage/logs
chmod -R 755 bootstrap/cache

# Also ensure laravel directory is readable
chmod -R 755 laravel
```

---

### Step 10: Create .htaccess File

In cPanel, navigate to `/home/mzerisoh/public_html/forms/` and create `.htaccess`:

```bash
# Create the file
nano .htaccess
```

**Add this content:**

```apache
<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteBase /forms/
    
    # Redirect all requests to public folder
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_FILENAME} !-d
    RewriteCond %{REQUEST_FILENAME} !-l
    RewriteRule ^(.*)$ public/$1 [L]
</IfModule>
```

**Save (Ctrl+X, Y, Enter)**

---

### Step 11: Configure Public Directory in cPanel

**Via cPanel File Manager:**

1. Go to: **cPanel → File Manager**
2. Navigate to: `/public_html/forms/public`
3. Right-click the `public` folder → **Make Default**
4. Or use: **File Manager → Settings → Document Root → Set to `/forms/public`**

**Via SSH (if Make Default doesn't work):**

This is handled automatically if Laravel is correctly set up.

---

### Step 12: Create Uploads Directory (If Needed)

```bash
# Ensure uploads directory exists and is writable
mkdir -p /home/mzerisoh/public_html/forms/uploads/agreements
mkdir -p /home/mzerisoh/public_html/forms/uploads/stamps

chmod -R 777 /home/mzerisoh/public_html/forms/uploads
```

---

### Step 13: Clear Cache

```bash
# Clear application cache
php artisan config:cache
php artisan route:cache
php artisan view:cache

# If you make changes later:
php artisan cache:clear
```

---

### Step 14: Verify Installation

```bash
# Check Laravel is working
php artisan about

# Should show:
# ✅ Environment: production
# ✅ Debug Mode: false
# ✅ Database: OK
```

---

## ✅ TESTING THE APPLICATION

### Test 1: Check URL Access

```
https://phemediaa.com/forms/
```

**Expected:** You should see the PHEMEDAA Forms Portal home page

### Test 2: Test Admin Login

```
URL: https://phemediaa.com/forms/admin/login
Username: admin
Password: admin123
```

**Expected:** You're logged into admin dashboard

### Test 3: Test Form Submission

```
URL: https://phemediaa.com/forms/backgroundcheck
```

**Expected:** Form loads with all fields

---

## 🚨 TROUBLESHOOTING

### Error: "500 Internal Server Error"

**Solution:**

```bash
# Check Laravel logs
tail -50 storage/logs/laravel.log

# Clear cache
php artisan cache:clear
php artisan config:clear

# Re-run migrations
php artisan migrate --force
```

---

### Error: "Class not found" or "Route not found"

**Solution:**

```bash
# Regenerate autoloader
composer dump-autoload -o

# Clear everything
php artisan optimize:clear
php artisan cache:clear
```

---

### Error: "CSRF token mismatch"

**Solution:** Session directory permissions issue

```bash
chmod -R 777 storage/framework/sessions
chmod -R 777 bootstrap/cache
```

---

### Error: "Cannot write to storage"

**Solution:**

```bash
# Fix storage permissions
chmod -R 755 storage
chmod -R 755 bootstrap/cache
chown -R mzerisoh:mzerisoh storage bootstrap

# Test write permissions
touch storage/test.txt
rm storage/test.txt
```

---

### Error: "Database connection refused"

**Solution:** Check database credentials

```bash
# Verify credentials in .env match cPanel database
# Test connection:
php artisan tinker
> DB::connection()->getPdo()
# Should return connection info
> exit

# Verify database exists
mysql -h localhost -u mzerisoh_phemediauser -p mzerisoh_phemediaaform
# Enter password: @phemediaadmin123456_
```

---

### Error: "Composer not found"

**Solution:** Use PHP's built-in Composer

```bash
# cPanel usually has composer at:
/usr/local/bin/composer install --no-dev

# Or use PHP directly:
php -d memory_limit=-1 /usr/local/bin/composer install --no-dev
```

---

## 📋 FINAL VERIFICATION CHECKLIST

After deployment, verify everything works:

- [ ] Website loads: https://phemediaa.com/forms/
- [ ] Admin login works: https://phemediaa.com/forms/admin/login
- [ ] Form submission works: https://phemediaa.com/forms/backgroundcheck
- [ ] Database populated: Check with phpMyAdmin
- [ ] Emails sending: Test from admin dashboard
- [ ] No errors in logs: Check `storage/logs/laravel.log`
- [ ] HTTPS working: SSL certificate active
- [ ] Performance acceptable: Page loads in < 2 seconds

---

## 🔧 POST-DEPLOYMENT

### Backup Strategy

```bash
# Create daily backups
cd /home/mzerisoh/public_html/forms

# Backup database
mysqldump -u mzerisoh_phemediauser -p mzerisoh_phemediaaform > backup_$(date +%Y%m%d).sql

# Backup files (excluding node_modules/vendor)
tar --exclude='vendor' --exclude='node_modules' -czf backup_$(date +%Y%m%d).tar.gz .
```

---

### Monitor Logs

```bash
# Watch for errors
tail -f storage/logs/laravel.log

# Check last 100 lines
tail -100 storage/logs/laravel.log
```

---

### Update Application

```bash
cd /home/mzerisoh/public_html/forms

# Pull latest changes
git pull origin master

# Update dependencies
composer install --no-dev

# Clear cache
php artisan optimize:clear
```

---

## 🎯 QUICK REFERENCE

| Action | Command |
|--------|---------|
| **SSH Login** | `ssh mzerisoh@phemediaa.com` |
| **Navigate** | `cd /home/mzerisoh/public_html/forms` |
| **Clone** | `git clone https://github.com/akinboye/phemediaforms.git .` |
| **Install** | `composer install --no-dev` |
| **Setup** | `php artisan migrate --force` |
| **Seed** | `php artisan db:seed --force` |
| **Cache** | `php artisan config:cache` |
| **Logs** | `tail -f storage/logs/laravel.log` |
| **Permissions** | `chmod -R 755 storage bootstrap` |
| **Test** | `php artisan tinker` |

---

## 📞 SUPPORT

If you encounter issues:

1. **Check logs:** `storage/logs/laravel.log`
2. **Verify permissions:** `ls -la storage/`
3. **Test database:** `php artisan tinker` → `DB::connection()->getPdo()`
4. **Test email:** Admin dashboard → Test email
5. **Check cPanel:** File Manager, Database, Addon Domains

---

## ✅ SUCCESS INDICATORS

Your application is running successfully when:

✅ HTTPS loads with no errors  
✅ Admin login works with provided credentials  
✅ Forms display and submit  
✅ PDF generation works  
✅ Emails send from admin@phemediaa.com  
✅ No 500 errors in logs  
✅ Database contains form submissions  

---

**Status:** ✅ DEPLOYMENT GUIDE COMPLETE

**Expected Time:** 15-20 minutes total  
**Difficulty:** Intermediate (requires SSH access)  
**Support:** All documentation available in `/docs/`

🚀 **Your application will be live at https://phemediaa.com/forms/**
