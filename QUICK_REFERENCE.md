# PHEMEDAA Admin Dashboard - Quick Reference Card

## 🚀 Quick Start (5 minutes)

### 1. Start Server
```bash
python app.py
```

### 2. Initialize Superadmin
Open: `http://localhost:5000/init-superadmin`
Save credentials: admin / admin123

### 3. Login
Go to: `http://localhost:5000/admin_login`
Use: admin / admin123

### 4. Done! 🎉
You're now in the superadmin dashboard

---

## 📍 Key URLs

| Feature | URL | Access |
|---------|-----|--------|
| **Forms** | http://localhost:5000/ | Public |
| **Admin Login** | http://localhost:5000/admin_login | Anyone |
| **Superadmin Dashboard** | http://localhost:5000/superadmin/dashboard | Superadmin only |
| **Staff Admin Dashboard** | http://localhost:5000/admin/dashboard | Staff admin only |
| **Init Superadmin** | http://localhost:5000/init-superadmin | First time only |
| **Logout** | http://localhost:5000/admin_logout | All authenticated |

---

## 🎯 Common Tasks

### Create a New Admin
1. Login as Superadmin
2. Click "👥 Manage Admins"
3. Click "➕ Create New Admin"
4. Fill form (name, email, phone, username, password)
5. Click "Create Admin"
6. Share username & password with admin

### Add Email Notification
1. Click "📧 Email Settings"
2. Click "➕ Add Email"
3. Enter email address
4. Choose form type (All Forms or specific)
5. Click "Add Email"

### View Form Submission
1. Click "📋 Form Submissions"
2. Select form type
3. Click "View Details" on a submission
4. See all submitted data

### Disable Admin User
1. Click "👥 Manage Admins"
2. Find admin in table
3. Click "Disable" button
4. Admin cannot login (click "Enable" to restore)

### Print Submission
1. View submission details
2. Click "🖨️ Print" OR use Ctrl+P
3. Print or save as PDF

---

## 💡 Tips & Tricks

### Generate Password
- When creating admin, click "🔐 Generate Password"
- Creates secure 12-character password
- Saves time and ensures strong passwords

### Email Routing
- "All Forms" emailreceives every submission
- Specific form emails receive only that form
- Can have both (all + specific)

### Form Types
1. `backgroundchecks` - Background Checks
2. `declarationbyemployee` - Declarations
3. `guarantorundertaking` - Guarantor
4. `serviceagreement` - Service Agreements
5. `trackingagreement` - Tracking Agreements

### Print Friendly
- All pages are print-optimized
- Buttons and navigation hidden in print
- Looks professional when printed to PDF

---

## ⚙️ Navigation Menu (Superadmin)

```
📊 Navigation
├── 👥 Manage Admins
│   └── Create, Edit, Enable/Disable admins
├── 📋 Form Submissions
│   └── View by form type, see details
└── 📧 Email Settings
    └── Add, Edit, Enable/Disable emails
```

---

## 👤 User Roles

### Superadmin
- Full system access
- Create/manage admins
- Configure emails
- View all submissions
- Who to use for: System administrator setup

### Admin (Staff)
- Limited to viewing submissions
- Can email submitters
- Cannot manage system
- Who to use for: Help desk, support staff

### User
- Can submit forms
- Receive confirmation emails
- Cannot see admin features
- Who to use for: Regular form submitters

---

## 🔐 Passwords & Security

### Password Rules
- Minimum 6 characters
- Can contain letters, numbers, symbols
- All passwords hashed (cannot be recovered)
- Must be changed by user if forgotten

### Reset Password
1. Login as Superadmin
2. Go to "Manage Admins"
3. Click "Edit" on admin
4. Enter new password
5. Click "Update Admin"

### Best Practices
- ✅ Use unique usernames
- ✅ Use strong passwords
- ✅ Change default admin password
- ✅ Disable unused admin accounts
- ✅ Keep email config updated

---

## 📧 Email Configuration

### What Gets Emailed

**When form submitted:**
1. ✉️ Admin receives form data (to notification emails)
2. ✉️ Submitter receives confirmation (if email provided)

**Who receives emails:**
- All emails marked as "Active"
- Matching form type (or "All Forms")

### Email Setup Example

```
Email 1: info@phemediaa.com
Type: All Forms ✓ Active
→ Receives ALL form submissions

Email 2: bg-team@example.com
Type: Background Checks ✓ Active
→ Receives only background checks

Email 3: old@example.com
Type: All Forms (but INACTIVE)
→ Does NOT receive anything
```

---

## 🐛 Quick Troubleshoot

| Problem | Solution |
|---------|----------|
| Can't login | Try admin/admin123, check if admin is active |
| Not receiving emails | Check notification email is active, correct form type |
| Can't see superadmin dashboard | Make sure you're logged in as superadmin |
| Database error | Delete phemedaa_forms.db, restart server, run /init-superadmin |
| Forgot password | Edit admin account, set new password |
| Admin can't login | Check if admin is active (enable if disabled) |

---

## 📊 Dashboard Layout

```
┌─ Superadmin Dashboard ─────────────────────┐
│                                            │
│  [Logout]                                 │
│                                            │
│  ┌─ Sidebar ─┐  ┌─ Main Content ────────┐ │
│  │ Navigation│  │                       │ │
│  │ ─────     │  │ Welcome Box           │ │
│  │ Admins   │  │ ─────────────────────│ │
│  │ Forms    │  │ Manage Admins Panel   │ │
│  │ Emails   │  │ [Create Admin]        │ │
│  │          │  │ [Admin Table]         │ │
│  └──────────┘  └─────────────────────────┘ │
└────────────────────────────────────────────┘
```

---

## 📁 Database Location

```
phemedaa_forms.db
├── superadmin table
├── admin table
├── notification_email table
└── form_submission table
```

**Location:** Project root directory (same folder as app.py)

**To reset:** Delete phemedaa_forms.db and restart server

---

## 🔑 Routes by Permission

### Public (No Login)
- GET / → Home page
- GET /[form_name] → Form pages
- POST /submit-form → Submit forms

### Authenticated (Any Admin)
- GET /admin_logout → Logout
- GET /admin/dashboard → View submissions (if staff)
- GET /superadmin/dashboard → Full dashboard (if superadmin)

### Superadmin Only
- POST /superadmin/admin/create → Create admin
- POST /superadmin/admin/[id]/update → Edit admin
- POST /superadmin/admin/[id]/toggle → Enable/disable admin
- POST /superadmin/email/create → Add email
- POST /superadmin/email/[id]/update → Edit email
- POST /superadmin/email/[id]/delete → Delete email

---

## 🎯 Daily Workflow

### Morning
✅ Check form submissions
✅ Review newly submitted data
✅ Email submitters if needed

### Weekly
✅ Review admin access
✅ Verify email notifications working
✅ Disable unused admin accounts

### Monthly
✅ Archive old submissions (if needed)
✅ Update admin passwords
✅ Review email configuration
✅ Check system logs

---

## 📞 Support

For detailed help, see:
- **ADMIN_GUIDE.md** - Full user guide
- **IMPLEMENTATION_SUMMARY.md** - Technical details
- Code comments in models.py, auth.py, app.py

---

## ✅ Checklist Before Go-Live

- [ ] Change default admin password
- [ ] Create staff admin accounts
- [ ] Configure Gmail app password
- [ ] Add notification emails
- [ ] Test form submission end-to-end
- [ ] Verify emails being sent
- [ ] Train staff on dashboard usage
- [ ] Set up email forwarding if needed
- [ ] Configure backups
- [ ] Document admin procedures

---

**Admin Dashboard Ready! 🚀**

*Last Updated: 2026*
*PHEMEDAA Forms Portal*
