# PHEMEDAA Admin Dashboard - Setup & Usage Guide

## Overview

The admin dashboard system has been fully implemented with role-based access control for managing form submissions, admin users, and email notifications.

## System Architecture

### User Roles

1. **Superadmin** (Root Administrator)
   - Full system access
   - Create, edit, and manage admin users
   - View all form submissions
   - Configure notification emails
   - Enable/disable admin accounts
   - Access: `/admin_login` → Superadmin Dashboard

2. **Admin** (Staff Administrator)
   - Limited access
   - View form submissions
   - View notification email settings
   - Access: `/admin_login` → Admin Dashboard

## Quick Start

### Step 1: Initialize Superadmin Account

**First time setup only:**

1. Open your browser and navigate to:
   ```
   http://localhost:5000/init-superadmin
   ```

2. You'll receive a response with default credentials:
   - **Username:** `admin`
   - **Password:** `admin123`
   - **Email:** `admin@phemediaa.com`

3. ⚠️ **IMPORTANT:** Change these credentials immediately after first login!

### Step 2: Login to Admin Dashboard

1. Navigate to: `http://localhost:5000/admin_login`
2. Enter your superadmin credentials:
   - **Username:** `admin` (or your updated username)
   - **Password:** `admin123` (or your updated password)
3. Click "Login"

### Step 3: Access Your Dashboard

After login, you'll be redirected to the appropriate dashboard:
- **Superadmin** → `/superadmin/dashboard`
- **Admin** → `/admin/dashboard`

---

## Superadmin Dashboard Features

### 👥 Manage Admins

#### Create New Admin User

1. Click "➕ Create New Admin" button
2. Fill in the form:
   - **First Name** (required)
   - **Last Name** (required)
   - **Email** (required, must be unique)
   - **Phone Number** (required)
   - **Username** (required, must be unique)
   - **Password** (required, minimum 6 characters)
   - **Confirm Password** (required, must match)
3. Click "Create Admin"
4. Share credentials securely with the admin user

**Generate Password Tip:**
- Click "🔐 Generate Password" button to create a secure random password
- The password will auto-populate both password fields

#### Edit Admin Account

1. Click on an admin's row in the table
2. Click "Edit" button
3. Update any fields (username cannot be changed)
4. To reset password, enter new password in "Password" field
5. Click "Update Admin"

#### Enable/Disable Admin

1. In the admin list table, click "Disable" to deactivate (prevents login)
2. Click "Enable" to reactivate the account
3. Changes take effect immediately

**Note:** Inactive admins cannot log in to the system

---

### 📋 Form Submissions

#### View Submissions by Form Type

1. Click on "📋 Form Submissions" in the sidebar
2. Select a form type:
   - 📋 Background Checks
   - 📝 Declarations
   - 🤝 Guarantor Undertaking
   - ✅ Service Agreements
   - 📍 Tracking Agreements
3. A table appears showing all submissions for that form

#### View Submission Details

1. In the submissions table, click "View Details" for a submission
2. You'll see:
   - Date & time submitted
   - Submitter's email
   - IP address used
   - All form field data
3. Actions available:
   - 📧 Email Submitter (opens email client)
   - 🖨️ Print Details or print using Ctrl+P

---

### 📧 Email Management

#### Add Notification Email

1. Click "📧 Email Settings" in the sidebar
2. Click "➕ Add Email" button
3. Fill in the form:
   - **Email Address** (required, must be valid)
   - **Receive Notifications For** (choose one):
     - 📋 All Forms (receives all submissions)
     - Or specific form type
4. Click "Add Email"

**Use Case Examples:**
- Add `info@phemediaa.com` for "All Forms" to receive every submission
- Add specific team member emails for specific form types
- Add support@phemediaa.com for Background Check only

#### Edit Notification Email

1. Click on an email row in the table
2. Click "Edit" button
3. Update email address or form type
4. Toggle "Active" to enable/disable temporarily
5. Click "Update Email"

#### Delete Notification Email

1. Click on an email row in the table
2. Click "Delete" (appears after editing)
3. Confirm deletion (cannot be undone)

#### Toggle Email On/Off

1. In the email list, click "Disable" to temporarily stop notifications
2. Click "Enable" to resume notifications
3. Useful for testing or maintenance without deleting

---

## Admin Dashboard Features (for Staff)

The staff admin dashboard provides:

- **View Form Submissions:** Access individual form submissions
- **View Details:** Click any submission to see full details
- **Print:** Print individual submission details
- **Email Submitter:** Contact submitters directly via email

Staff admins **cannot:**
- Create or manage other admins
- Add/remove/edit notification emails
- Access system administration features

---

## Database & Storage

### Form Submissions Storage

All submitted forms are now stored in SQLite database:
- **Location:** `phemedaa_forms.db` (in project root)
- **Form Data:** Stored as JSON for flexibility
- **Metadata:** IP address, user agent, submission time

### Database Models

```
SuperAdmin
├── id (Primary Key)
├── username (Unique)
├── password (hashed)
├── email
└── created_at

Admin
├── id (Primary Key)
├── first_name
├── last_name
├── email (Unique)
├── phone_number
├── username (Unique)
├── password (hashed)
├── is_active
├── created_at
└── created_by (FK to SuperAdmin)

NotificationEmail
├── id (Primary Key)
├── email
├── form_type ('all' or specific form)
├── is_active
├── added_by_admin (FK to Admin, nullable)
├── added_by_superadmin (FK to SuperAdmin, nullable)
└── created_at

FormSubmission
├── id (Primary Key)
├── form_type
├── submitted_data (JSON)
├── user_email
├── submitted_at
├── ip_address
└── user_agent
```

---

## Email Notification Flow

### Form Submission Process

1. User fills out and submits a form
2. Form data is validated
3. **Database:** Form submission is saved to `FormSubmission` table
4. **Emails:** All active notification emails for that form type receive an email
5. **User:** If email provided, user receives confirmation email
6. **Admin:** Form appears in submission viewing dashboard

### Email Recipients

Form submissions are sent to emails that match:
```
form_type = 'all' OR form_type = '[submitted_form_type]'
AND
is_active = TRUE
```

**Example Configuration:**
```
✓ info@phemediaa.com (all forms) → Receives ALL submissions
✓ bg-team@phemediaa.com (backgroundcheck) → Receives only background check submissions
✗ jane@example.com (all forms, inactive) → Does NOT receive anything
```

---

## Security Best Practices

### Password Management

1. ✅ All passwords are hashed using werkzeug.security
2. ✅ Minimum 6 characters enforced
3. ✅ Unique usernames required
4. ✅ Session-based authentication

### Access Control

1. ✅ Role-based route protection
2. ✅ Superadmin-only routes protected with `@require_superadmin`
3. ✅ Admin routes protected with `@require_admin_or_superadmin`
4. ✅ Session validation on every request
5. ✅ Inactive admins cannot access system

### Recommendations

1. **Change default password immediately:**
   - Login as `admin`
   - Edit your profile (future feature)
   - Change password to something secure

2. **Use strong passwords:**
   - Use the password generator (🔐 button)
   - Minimum 12 characters recommended
   - Include uppercase, lowercase, numbers, symbols

3. **Secure email configurations:**
   - Use SMTP app passwords (not regular Gmail passwords)
   - Keep `MAIL_PASSWORD` secure in production
   - Never commit credentials to version control

4. **Regular admin audits:**
   - Review admin list regularly
   - Disable unused accounts
   - Update contact information

5. **Monitor submissions:**
   - Regularly check form submissions
   - Verify email notifications are working
   - Watch for spam or suspicious entries

---

## Troubleshooting

### Issue: Cannot login

**Solution:**
1. Verify username is correct (case-sensitive)
2. Check if admin account is active
3. Reset password by editing admin account
4. Try `admin` / `admin123` if superadmin login

### Issue: Not receiving form submission emails

**Solution:**
1. Check notification email configuration
   - Navigate to Email Settings
   - Verify email address is in the list
   - Check if email is marked as "Active"
2. Verify form type matches
   - Email must be set to "All Forms" OR the specific form type
3. Check email configuration
   - `MAIL_USERNAME` and `MAIL_PASSWORD` in app.py
   - Verify SMTP settings (gmail uses app passwords)
4. Check email is correct
   - Typos in email address
   - Invalid email format

### Issue: Cannot access superadmin dashboard

**Solution:**
1. Verify you're logged in as superadmin
2. Check session by looking at login page
3. Try logging out (`/admin_logout`) and back in
4. Clear browser cookies for localhost

### Issue: Database errors

**Solution:**
1. Delete `phemedaa_forms.db` to reset
2. Server will recreate it on next run
3. Run `/init-superadmin` again
4. All previous data will be lost

---

## Routes Reference

### Public Routes
- `GET /` — Landing page
- `GET /[form_name]` — Individual form pages
- `POST /submit-form` — Form submission handling
- `GET /confirmation` — Submission confirmation page

### Authentication Routes
- `GET /admin_login` — Admin login page
- `POST /admin_login` — Process login
- `GET /admin_logout` — Logout
- `GET /init-superadmin` — Initialize first superadmin (one-time setup)

### Superadmin Routes
- `GET /superadmin/dashboard` — Superadmin main dashboard
- `GET /superadmin/admin/create` — Create admin form
- `POST /superadmin/admin/create` — Process admin creation
- `GET /superadmin/admin/<id>/edit` — Edit admin form
- `POST /superadmin/admin/<id>/update` — Update admin
- `POST /superadmin/admin/<id>/toggle` — Enable/disable admin
- `GET /superadmin/submissions/<form_type>` — Get submissions JSON
- `GET /superadmin/submission/<id>` — View submission details
- `GET /superadmin/email/create` — Add email form
- `POST /superadmin/email/create` — Save email
- `GET /superadmin/email/<id>/edit` — Edit email form
- `POST /superadmin/email/<id>/update` — Update email
- `POST /superadmin/email/<id>/toggle` — Enable/disable email
- `POST /superadmin/email/<id>/delete` — Delete email

### Admin Routes
- `GET /admin/dashboard` — Admin staff dashboard
- Access to same submission and email viewing as superadmin

---

## Next Steps

1. ✅ **Run the server:** Start Flask development server
2. ✅ **Initialize superadmin:** Visit `/init-superadmin`
3. ✅ **Login:** Use `admin` / `admin123`
4. ✅ **Change password:** Edit your admin account
5. ✅ **Create staff admins:** Add team members
6. ✅ **Configure notifications:** Set up email routing
7. ✅ **Test submission:** Submit a form and verify flow

---

## Files Added/Modified

### New Files Created
- `models.py` — SQLAlchemy database models
- `auth.py` — Authentication helpers and decorators
- `templates/admin_login.html` — Admin login page
- `templates/superadmin_dashboard.html` — Superadmin dashboard
- `templates/admin_dashboard.html` — Staff admin dashboard
- `templates/admin_form.html` — Create/edit admin form
- `templates/email_form.html` — Manage notification emails
- `templates/submission_details.html` — View submission details
- `phemedaa_forms.db` — SQLite database (created on first run)

### Modified Files
- `app.py` — Added SQLAlchemy initialization, admin routes, form submission storage
- `requirements.txt` — Added Flask-SQLAlchemy and SQLAlchemy dependencies

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the code comments in models.py and auth.py
3. Check app.py for route implementations
4. Verify Flask and SQLAlchemy are properly installed

---

*Admin Dashboard Implementation Complete - 2026 PHEMEDAA*
