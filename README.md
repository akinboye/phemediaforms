# PHEMEDAA Forms Portal

A secure Flask web application for managing and processing multiple forms with admin approval workflow, PDF generation, and email notifications.

## Features

- **Multiple Form Types**: Background Check, Client Engagement, Employee Declaration, Guarantor Undertaking, Service Agreement, Tracking Agreement, Oil & Gas Service Request
- **Form Submission**: Users can submit forms online with validation
- **Admin Dashboard**: SuperAdmin and Admin interfaces for managing submissions
- **Approval Workflow**: Review, approve, or reject submissions with comments
- **PDF Generation**: Automatic PDF generation for forms and approvals
- **Digital Signatures**: Support for approval stamps and signatures
- **Email Notifications**: Automated email confirmations and notifications
- **Security**: User authentication, CSRF protection, input validation, security headers

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: MySQL
- **Email**: SMTP via mail.phemediaa.com
- **PDF Generation**: FPDF2
- **Frontend**: HTML, CSS, JavaScript

## Prerequisites

- Python 3.7+
- MySQL Server
- Git

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/akinboye/phemediaforms.git
cd phemediaforms
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. MySQL Configuration

Ensure MySQL is running with the following credentials:
- **Host**: localhost
- **Port**: 3306
- **Username**: root
- **Password**: $Albert2022#

### 4. Initialize Database
```bash
python setup_mysql.py
```

### 5. Create Admin Users
```bash
python init_admins.py
```

This creates:
- **SuperAdmin**: username=`admin`, password=`admin123`
- **Admin**: username=`user`, password=`user123`

## Running the Application

### Development
```bash
python app.py
```

The application will start on `http://localhost:5000`

### Production
Use a production WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn app:app
```

## Folder Structure

```
phemediaforms/
├── app.py                    # Main Flask application
├── models.py                 # Database models
├── auth.py                   # Authentication helpers
├── setup_mysql.py           # Database initialization
├── init_admins.py           # Admin user initialization
├── requirements.txt         # Python dependencies
├── static/                  # Static files (CSS, images)
├── templates/               # HTML templates
├── uploads/                 # User uploads (PDFs, stamps)
└── instance/               # Instance-specific files
```

## Email Configuration

The application is configured to use:
- **Server**: mail.phemediaa.com
- **Port**: 465 (SSL)
- **Username**: admin@phemediaa.com
- **Password**: @phemediaadmin123456_

To test email configuration:
```bash
python test_email_config.py
```

## Database Models

- **SuperAdmin**: System administrator
- **Admin**: Form approval administrators
- **FormSubmission**: Submitted form data
- **NotificationEmail**: Email notification settings
- **CompanyAddress**: Company address information
- **ApprovalStamp**: Digital approval stamps

## API Routes

### Public Routes
- `GET /` - Home page
- `POST /submit-form` - Submit form
- `GET /{form_type}` - Form pages (backgroundcheck, clientengagement, etc.)

### Admin Routes
- `GET/POST /admin_login` - Admin login
- `GET /admin/dashboard` - Admin dashboard
- `GET /superadmin/dashboard` - SuperAdmin dashboard

## Security Features

- CSRF Protection via Flask-WTF
- Password hashing using Werkzeug
- Session-based authentication
- Input validation and sanitization
- Security headers (X-Frame-Options, X-XSS-Protection, etc.)
- Content Security Policy

## License

Copyright © 2026 PHEMEDAA. All rights reserved.

## Support

For support, contact: info@phemediaa.com
