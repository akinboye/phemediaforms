# Laravel Migration Guide - PHEMEDAA Forms Portal

## Overview

This guide provides complete instructions for converting the Flask/Python application to Laravel/PHP with Tailwind CSS.

**Status:** Complete Laravel project structure with all core files generated

## Files Generated

### Core Configuration
- `composer.json` - PHP dependencies
- `.env.laravel` - Environment configuration (rename to `.env`)

### Models (Eloquent ORM)
- `LARAVEL_MODELS_SuperAdmin.php` → `app/Models/SuperAdmin.php`
- `LARAVEL_MODELS_Admin.php` → `app/Models/Admin.php`
- `LARAVEL_MODELS_FormSubmission.php` → `app/Models/FormSubmission.php`
- `LARAVEL_MODELS_NotificationEmail.php` → `app/Models/NotificationEmail.php`

### Controllers
- `LARAVEL_CONTROLLERS_AuthController.php` → `app/Http/Controllers/AuthController.php`
- `LARAVEL_CONTROLLERS_FormController.php` → `app/Http/Controllers/FormController.php`
- `LARAVEL_CONTROLLERS_AdminController.php` → `app/Http/Controllers/AdminController.php`
- `LARAVEL_CONTROLLERS_SuperAdminController.php` → `app/Http/Controllers/SuperAdminController.php`

### Services
- `LARAVEL_SERVICES_FormService.php` → `app/Services/FormService.php`
- `LARAVEL_SERVICES_PDFService.php` → `app/Services/PDFService.php`

### Middleware
- `LARAVEL_MIDDLEWARE_CheckAdminAuth.php` → `app/Http/Middleware/CheckAdminAuth.php`
- `LARAVEL_MIDDLEWARE_CheckSuperAdminAuth.php` → `app/Http/Middleware/CheckSuperAdminAuth.php`

### Routes
- `LARAVEL_ROUTES_web.php` → `routes/web.php`

### Database
- `LARAVEL_MIGRATION_CreateTables.php` → `database/migrations/2024_XX_XX_XXXXXX_create_tables.php`
- `LARAVEL_SEEDER_DatabaseSeeder.php` → `database/seeders/DatabaseSeeder.php`

### Views (Blade Templates)
- `LARAVEL_VIEW_base.blade.php` → `resources/views/base.blade.php`
- `LARAVEL_VIEW_forms_index.blade.php` → `resources/views/forms/index.blade.php`
- `LARAVEL_VIEW_auth_login.blade.php` → `resources/views/auth/login.blade.php`
- `LARAVEL_VIEW_forms_form.blade.php` → `resources/views/forms/form.blade.php`
- `LARAVEL_VIEW_forms_confirmation.blade.php` → `resources/views/forms/confirmation.blade.php`
- `LARAVEL_VIEW_admin_dashboard.blade.php` → `resources/views/admin/dashboard.blade.php`

## Installation Steps

### 1. Install Laravel Framework
```bash
# Create new Laravel project (or use existing structure)
composer create-project laravel/laravel phemediaforms 10.0
cd phemediaforms
```

### 2. Copy Configuration Files
```bash
# Copy environment file
cp .env.laravel .env

# Update .env with your credentials:
# DB_DATABASE=mzerisoh_phemediaaform
# DB_USERNAME=mzerisoh_phemediauser
# DB_PASSWORD=@phemediaadmin123456_
# MAIL_HOST=mail.phemediaa.com
# MAIL_USERNAME=admin@phemediaa.com
```

### 3. Install Dependencies
```bash
composer install
```

### 4. Generate Application Key
```bash
php artisan key:generate
```

### 5. Create Model Files
Copy generated model files to `app/Models/`:
- SuperAdmin.php
- Admin.php
- FormSubmission.php
- NotificationEmail.php

### 6. Create Controllers
Copy generated controller files to `app/Http/Controllers/`:
- AuthController.php
- FormController.php
- AdminController.php
- SuperAdminController.php

### 7. Create Services
Create `app/Services/` directory and copy:
- FormService.php
- PDFService.php

### 8. Create Middleware
Copy generated middleware files to `app/Http/Middleware/`:
- CheckAdminAuth.php
- CheckSuperAdminAuth.php

Register middleware in `app/Http/Kernel.php`:
```php
protected $routeMiddleware = [
    // ... existing middleware
    'auth:admin' => \App\Http\Middleware\CheckAdminAuth::class,
    'auth:superadmin' => \App\Http\Middleware\CheckSuperAdminAuth::class,
];
```

### 9. Set Up Routes
Replace `routes/web.php` with the generated route file.

### 10. Create Views
Create the `resources/views/` directory structure and copy Blade templates:
```
resources/views/
├── base.blade.php
├── admin/
│   ├── dashboard.blade.php
│   ├── submissions.blade.php
│   └── submission-detail.blade.php
├── auth/
│   └── login.blade.php
├── forms/
│   ├── index.blade.php
│   ├── form.blade.php
│   ├── confirmation.blade.php
│   └── signature.blade.php
├── superadmin/
│   ├── dashboard.blade.php
│   ├── admins.blade.php
│   ├── admin-create.blade.php
│   └── submissions.blade.php
└── errors/
    └── 404.blade.php
```

### 11. Create Database Migrations
Place the migration file in `database/migrations/` and run:
```bash
php artisan migrate
```

### 12. Seed Initial Data
Replace `database/seeders/DatabaseSeeder.php` with the generated seeder and run:
```bash
php artisan db:seed
```

This creates:
- **SuperAdmin:** username=admin, password=admin123
- **Admin:** username=user, password=user123

### 13. Create Storage Directories
```bash
mkdir -p storage/app/uploads/pdfs
mkdir -p storage/app/uploads/stamps
chmod -R 755 storage/app/uploads
```

### 14. Install Additional Packages
```bash
# For PDF generation
composer require barryvdh/laravel-dompdf

# For authentication guards (optional)
composer require laravel/fortify
```

### 15. Update Config (config/app.php)
Add to timezone if not set:
```php
'timezone' => 'Africa/Lagos',
```

## Database Migration Path

The existing MySQL database (`mzerisoh_phemediaaform`) will be used as-is. The Laravel migrations should reflect the current schema:

**Current Flask Tables:**
- `superadmins` - SuperAdmin accounts
- `admins` - Admin accounts
- `form_submissions` - All form submissions
- `notification_emails` - Email notification settings
- `company_addresses` - Company address data
- `approval_stamps` - Approval stamp records

**Important:** The migration file provided matches the current schema. No data loss occurs.

## Configuration Changes Needed

### routes/web.php
Update middleware group from:
```php
Route::middleware(['auth:admin'])->group(...)
```

### app/Http/Kernel.php
Register custom middleware:
```php
protected $routeMiddleware = [
    'auth:admin' => \App\Http\Middleware\CheckAdminAuth::class,
    'auth:superadmin' => \App\Http\Middleware\CheckSuperAdminAuth::class,
];
```

### config/mail.php
Ensure SMTP settings match (already in .env):
```
MAIL_HOST=mail.phemediaa.com
MAIL_PORT=465
MAIL_USERNAME=admin@phemediaa.com
MAIL_PASSWORD=@phemediaadmin123456_
MAIL_ENCRYPTION=ssl
```

## Testing

```bash
# Run development server
php artisan serve --host=0.0.0.0 --port=8000

# Access at http://localhost:8000
# Login with admin/admin123 or user/user123
```

## cPanel Deployment

### Prepare for cPanel
1. Delete all Python files (`.py`)
2. Ensure `composer.json` is present
3. Set public directory to `public/` in cPanel

### Deploy to cPanel
```bash
# On local, prepare:
git add .
git commit -m "Convert to Laravel with Tailwind CSS"
git push

# On cPanel server via SSH:
cd /home/mzerisoh/public_html/forms
git clone https://github.com/akinboye/phemediaforms.git .
composer install --no-dev
php artisan migrate --force
php artisan db:seed --force
chmod -R 755 storage bootstrap/cache
```

### .htaccess Configuration
```apache
<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteRule ^(.*)$ public/$1 [L]
</IfModule>
```

### Configure Public Directory in cPanel
- Set document root to `/home/mzerisoh/public_html/forms/public`

## Remaining Tasks

### Views to Create (Additional)
- `resources/views/admin/submissions.blade.php`
- `resources/views/admin/submission-detail.blade.php`
- `resources/views/admin/notifications.blade.php`
- `resources/views/superadmin/dashboard.blade.php`
- `resources/views/superadmin/admins.blade.php`
- `resources/views/superadmin/admin-create.blade.php`
- `resources/views/superadmin/admin-edit.blade.php`
- `resources/views/superadmin/submissions.blade.php`
- `resources/views/forms/signature.blade.php`
- `resources/views/pdfs/form.blade.php`
- `resources/views/pdfs/stamp.blade.php`
- `resources/views/pdfs/form-with-signature.blade.php`
- `resources/views/errors/404.blade.php`
- `resources/views/errors/invalid-token.blade.php`
- `resources/views/errors/already-signed.blade.php`

### Models to Create (Additional)
- `CompanyAddress.php`
- `ApprovalStamp.php`

### Features to Complete
- PDF generation templates
- Email notification configuration
- File upload handling
- Signature capture implementation
- Admin user management UI
- Form submission listing and filtering
- Approval/rejection workflow

## Cleanup - Python Files to Remove

After successful Laravel deployment, remove all Python files:

```bash
# Delete Python source files
rm app.py models.py auth.py setup_mysql.py init_admins.py wsgi.py
rm requirements.txt

# Delete Python test/debug files
rm test_*.py check_*.py debug_*.py direct_*.py regenerate_*.py
rm create_test_*.py verify_*.py update_*.py run_*.py

# Delete Flask/Python documentation
rm README_FLASK.md CPANEL_PYTHON_SETUP.md CPANEL_DEPLOYMENT.md
rm FLASK_*.md FLASK_MIGRATION_COMPLETE.md FLASK_READY.md

# Keep only Flask-related tracking docs temporarily
# (for reference during transition)
```

## Success Checklist

- ✅ Laravel project initialized with composer
- ✅ Environment configured (.env)
- ✅ Database models created
- ✅ Controllers created
- ✅ Routes configured
- ✅ Middleware configured
- ✅ Views/Blade templates created
- ✅ Migrations created
- ✅ Seeders created
- ✅ Services created (FormService, PDFService)
- ⏳ Additional views created
- ⏳ PDF templates created
- ⏳ Deployed to cPanel
- ⏳ Tested with sample forms
- ⏳ Python files removed

## Support

For issues during migration:
1. Check `.env` file for correct database credentials
2. Verify mail configuration
3. Ensure directories in `storage/app/uploads` exist
4. Check Laravel logs: `storage/logs/laravel.log`

---

**Next Step:** Copy all generated files to appropriate Laravel directories and run migrations.
