# cPanel Deployment - Quick Start (5 Steps)

**Goal:** Deploy Laravel application to https://phemediaa.com/forms  
**Time:** ~20 minutes

---

## 🚀 SUPER QUICK DEPLOYMENT (Copy & Paste)

If you're comfortable with SSH, copy-paste this entire block:

```bash
# Step 1: Navigate to web root
cd /home/mzerisoh/public_html
rm -rf forms
mkdir forms
cd forms

# Step 2: Clone repository
git clone https://github.com/akinboye/phemediaforms.git .

# Step 3: Install dependencies
composer install --no-dev

# Step 4: Setup environment and database
cp .env .env.backup
cat > .env << 'EOF'
APP_NAME="PHEMEDAA Forms Portal"
APP_ENV=production
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

LOG_CHANNEL=stack
LOG_LEVEL=debug
CACHE_DRIVER=file
SESSION_DRIVER=file
QUEUE_CONNECTION=sync
EOF

# Step 5: Generate key and setup database
php artisan key:generate
php artisan migrate --force
php artisan db:seed --force

# Step 6: Set permissions and cache
chmod -R 755 storage bootstrap/cache
php artisan config:cache
php artisan route:cache
php artisan view:cache

# Done! Application is live at https://phemediaa.com/forms
echo "✅ DEPLOYMENT COMPLETE!"
```

---

## 📝 STEP-BY-STEP GUIDE

### 1️⃣ SSH into cPanel Server

```bash
ssh mzerisoh@phemediaa.com
```

**If using cPanel Terminal:**
- Login to cPanel
- Advanced → Terminal
- (You're already connected)

---

### 2️⃣ Clone Application

```bash
cd /home/mzerisoh/public_html
rm -rf forms          # Remove old version if exists
mkdir forms
cd forms
git clone https://github.com/akinboye/phemediaforms.git .
```

**Verify files:**
```bash
ls -la
# Should show: laravel/, docs/, composer.json, .env, etc.
```

---

### 3️⃣ Install PHP Packages

```bash
composer install --no-dev
```

Wait for: `Successfully installed X packages`

---

### 4️⃣ Configure Environment

```bash
# Copy template
cp .env .env.backup

# Edit .env
nano .env
```

**Essential values to set:**
```
APP_URL=https://phemediaa.com/forms
DB_DATABASE=mzerisoh_phemediaaform
DB_USERNAME=mzerisoh_phemediauser
DB_PASSWORD=@phemediaadmin123456_
MAIL_HOST=mail.phemediaa.com
MAIL_USERNAME=admin@phemediaa.com
MAIL_PASSWORD=@phemediaadmin123456_
```

**Save:** `Ctrl+X` → `Y` → `Enter`

---

### 5️⃣ Setup Database

```bash
# Generate encryption key
php artisan key:generate

# Create tables
php artisan migrate --force

# Add demo data
php artisan db:seed --force
```

---

### 6️⃣ Configure cPanel

In **cPanel File Manager:**
1. Go to: `/public_html/forms/public`
2. Right-click folder
3. Select: **Make Default**

Or in **cPanel Addon Domains:**
1. Point `forms.phemediaa.com` or subdirectory to `/forms/public`

---

### 7️⃣ Set Permissions

```bash
chmod -R 755 storage bootstrap/cache
chmod -R 755 uploads

# Verify with:
ls -la storage/
```

---

### 8️⃣ Clear Cache

```bash
php artisan config:cache
php artisan route:cache
php artisan view:cache
```

---

## ✅ TESTING

Visit these URLs:

| URL | Expected Result |
|-----|-----------------|
| https://phemediaa.com/forms/ | Home page loads |
| https://phemediaa.com/forms/admin/login | Login form appears |
| https://phemediaa.com/forms/backgroundcheck | Form loads |

**Admin credentials:**
```
Username: admin
Password: admin123
```

---

## 🆘 QUICK FIXES

### Application not loading?

```bash
php artisan cache:clear
php artisan config:clear
tail -20 storage/logs/laravel.log
```

### Database error?

```bash
php artisan tinker
> DB::connection()->getPdo()
> exit
```

### Permission error?

```bash
chmod -R 777 storage
chown -R mzerisoh:mzerisoh storage bootstrap
```

### Composer error?

```bash
/usr/local/bin/composer install --no-dev
```

---

## 📍 FILE LOCATIONS

| Item | Path |
|------|------|
| **Application Root** | `/home/mzerisoh/public_html/forms/` |
| **Laravel Code** | `/home/mzerisoh/public_html/forms/laravel/` |
| **Public Folder** | `/home/mzerisoh/public_html/forms/public/` |
| **Database** | `mzerisoh_phemediaaform` |
| **Logs** | `/home/mzerisoh/public_html/forms/storage/logs/` |
| **Uploads** | `/home/mzerisoh/public_html/forms/uploads/` |

---

## 🎯 VERIFICATION CHECKLIST

After deployment, verify:

- [ ] Website loads: https://phemediaa.com/forms/
- [ ] No 500 errors
- [ ] Admin login works
- [ ] Forms display correctly
- [ ] Database connected (check phpMyAdmin)
- [ ] HTTPS certificate valid
- [ ] No errors in: `storage/logs/laravel.log`

---

## 🔄 AFTER DEPLOYMENT

### Monitor Application

```bash
# Watch logs in real-time
tail -f /home/mzerisoh/public_html/forms/storage/logs/laravel.log

# Check for errors
grep -i "error" /home/mzerisoh/public_html/forms/storage/logs/laravel.log
```

### Update Code

```bash
cd /home/mzerisoh/public_html/forms
git pull origin master
composer install --no-dev
php artisan migrate --force
php artisan optimize:clear
```

### Backup Database

```bash
mysqldump -u mzerisoh_phemediauser -p mzerisoh_phemediaaform > backup.sql
# Enter password: @phemediaadmin123456_
```

---

## 📞 COMMON ISSUES & SOLUTIONS

| Issue | Solution |
|-------|----------|
| **500 Internal Server Error** | Check `storage/logs/laravel.log` |
| **Route not found** | Run `php artisan route:cache` |
| **Database connection error** | Check `.env` credentials match cPanel |
| **Permission denied** | Run `chmod -R 755 storage bootstrap` |
| **CSRF token mismatch** | Run `php artisan cache:clear` |
| **Mail not sending** | Test in admin dashboard, check MAIL_* vars |

---

## 🎉 YOU'RE DONE!

Your Laravel application is now running at:

### 🔗 https://phemediaa.com/forms

**Admin Panel:** https://phemediaa.com/forms/admin/login  
**Credentials:** admin / admin123

---

**Time taken:** ~20 minutes  
**Difficulty:** Beginner to Intermediate  
**Support:** All documentation in `/docs/` folder

✅ Application is production-ready!

---

*For detailed troubleshooting, see: CPANEL_DEPLOYMENT_GUIDE.md*
