# PHEMEDAA Forms Portal - Flask Version

A professional form management system built with Python Flask that provides a landing page with links to five distinct forms. The system automatically collects form data and sends it to specified email addresses.

## Features

✅ **5 Professional Forms**
- Background Checks Form
- Declaration by Employee Form  
- Guarantor Undertaking Form
- Service Agreement Form
- Tracking Agreement Form

✅ **Email Integration**
- Automatic admin notifications with complete form data
- User confirmation emails with submitted information
- HTML formatted emails for professional appearance

✅ **User Experience**
- Responsive design works on desktop, tablet, and mobile
- Form validation (client and server-side)
- Real-time error feedback
- Smooth form submission via AJAX

✅ **Security**
- Input sanitization to prevent XSS attacks
- Email address validation
- CSRF protection ready (can be added)
- Error handling with user-friendly messages

## Quick Start

### 1. Prerequisites

- Python 3.7 or higher
- Basic text editor or IDE
- Email account with SMTP access

### 2. Installation

1. Navigate to the project directory:
```bash
cd c:\Users\maila\Downloads\phemediaaforms\forms
```

2. Create a Python virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Configuration

1. Open `app.py` and modify the email configuration (lines 15-20):

```python
ADMIN_EMAIL = "your-admin@example.com"      # Where admin notifications are sent
FROM_EMAIL = "noreply@example.com"           # Email address that sends the emails
MAIL_SERVER = "smtp.gmail.com"               # Your SMTP server
MAIL_PORT = 587                              # SMTP port
MAIL_USERNAME = "your-email@example.com"     # Your email address
MAIL_PASSWORD = "your-app-password"          # Your email password or app password
```

**For Gmail users:**
- Enable "Less secure app access" OR
- Create an "App Password" at https://myaccount.google.com/apppasswords

**For other email providers:**
- Find their SMTP settings (usually documented on their support site)
- Gmail: smtp.gmail.com:587
- Outlook: smtp.office365.com:587
- Yahoo: smtp.mail.yahoo.com:465

### 4. Running the Application

1. Start the Flask development server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. You should see the PHEMEDAA landing page with 5 form links

### 5. Testing the Forms

1. Click on any form link (e.g., "Background Checks")
2. Fill in the form fields (marked with * are required)
3. Click "Submit Form" button
4. You should see a success message
5. Check your email inbox (and spam folder) for:
   - Admin notification with all form data
   - User confirmation email

## File Structure

```
forms/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── templates/
│   ├── base.html                   # Base template (header/footer)
│   ├── index.html                  # Landing page
│   ├── backgroundchecks.html       # Background checks form
│   ├── declarationbyemployee.html  # Employee declaration form
│   ├── guarantorundertaking.html   # Guarantor undertaking form
│   ├── serviceagreement.html       # Service agreement form
│   └── trackingagreement.html      # Tracking agreement form
└── static/
    └── styles.css                  # Responsive CSS styling
```

## Email Configuration Guide

### Gmail Setup

1. Enable 2-factor authentication on your Google Account
2. Go to https://myaccount.google.com/apppasswords
3. Select "Mail" and "Windows Computer" (or your device)
4. Google will generate a 16-character password
5. Use this password in `MAIL_PASSWORD` in app.py
6. Keep MAIL_SERVER as "smtp.gmail.com" and MAIL_PORT as 587

### Outlook/Microsoft 365

```python
MAIL_SERVER = "smtp.office365.com"
MAIL_PORT = 587
MAIL_USERNAME = "your-email@outlook.com"
MAIL_PASSWORD = "your-password"
```

### Corporate Email Servers

Contact your IT department for:
- SMTP server address
- SMTP port (usually 25, 465, or 587)
- Username and password
- Whether authentication is required

## Customization Guide

### Adding Your Company Logo

1. Place your logo image in `static/` directory
2. Edit `templates/base.html` to add the logo:
```html
<img src="{{ url_for('static', filename='logo.png') }}" alt="Company Logo" class="logo">
```

### Changing Colors

Edit `static/styles.css` to modify CSS variables (lines 1-10):
```css
--primary-color: #3498db;      /* Main color */
--accent-color: #2c3e50;       /* Accent color */
--success-color: #27ae60;      /* Success messages */
--error-color: #e74c3c;        /* Error messages */
```

### Modifying Form Fields

1. Open the desired form template (e.g., `backgroundchecks.html`)
2. Add/remove form fields as needed
3. Update the field names to match what you want to track
4. The `submitForm()` JavaScript function will automatically collect all form data

Example adding a new field:
```html
<div class="form-group">
    <label for="new_field" class="required">New Field Label</label>
    <input type="text" id="new_field" name="new_field" required>
</div>
```

### Changing Email Recipients

Modify `app.py` lines 117-119 in `process_form_submission()`:
```python
recipients = [
    ADMIN_EMAIL,           # Admin notification
    form_data.get('email') # User confirmation (using email from form)
]
```

## Troubleshooting

### "Email failed to send" Error

1. Check email configuration in app.py
2. Verify MAIL_SERVER and MAIL_PORT are correct
3. Make sure your email credentials are accurate
4. Check if 2FA is enabled (use App Password for Gmail)
5. Some ISPs block port 587 - try port 465 instead

### Forms not loading

1. Make sure you're running `python app.py`
2. Check that http://localhost:5000 is accessible
3. Look for error messages in the terminal
4. Verify all template files are in the `templates/` directory

### CSS not loading

1. Make sure `styles.css` is in the `static/` directory
2. Check that URL in `base.html` is correct: `{{ url_for('static', filename='styles.css') }}`
3. Clear browser cache (Ctrl+Shift+Delete or Cmd+Shift+Delete)
4. Restart Flask server

### Form data not collecting

1. Check browser console for JavaScript errors (F12 → Console)
2. Verify form names match between HTML form and submitForm() function
3. Check that `/submit-form` route is accessible
4. Look at Flask terminal output for error messages

## Advanced Configuration

### HTTPS (SSL/TLS)

For production, use HTTPS. Install `pyopenssl`:
```bash
pip install pyopenssl
python app.py --ssl-context=adhoc
```

### Database Storage

To store form submissions, modify `process_form_submission()` in app.py to save to a database (SQLAlchemy recommended).

### Background Jobs

For sending emails without blocking the form submission, use Celery with Redis.

## Production Deployment

### Heroku Deployment

1. Install Heroku CLI
2. Create `Procfile`:
```
web: gunicorn app:app
```

3. Install gunicorn:
```bash
pip install gunicorn
pip freeze > requirements.txt
```

4. Deploy:
```bash
heroku login
heroku create your-app-name
git push heroku main
```

### Azure Deployment

1. Install Azure CLI
2. Follow Azure App Service documentation
3. Set environment variables for email configuration

## Support & Documentation

For issues or questions:
- Flask Documentation: https://flask.palletsprojects.com/
- Jinja2 Templates: https://jinja.palletsprojects.com/
- Python Email: https://docs.python.org/3/library/email.html

## License

This application is provided as-is for the PHEMEDAA organization.

## Version Information

- **Flask Version**: 3.0.0
- **Python**: 3.7+
- **Created**: 2024
- **Last Updated**: 2024
