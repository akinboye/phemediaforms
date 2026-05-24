# 🚀 QUICK START - Read This First!

Your Flask Forms Portal is ready. Here's how to get started in 5 minutes:

## Step 1: Navigate to the Project Directory

Open PowerShell or Command Prompt and run:

```powershell
cd c:\Users\maila\Downloads\phemediaaforms\forms
```

## Step 2: Run the Setup Script (Recommended)

This will automatically set everything up for you:

```powershell
python setup.py
```

This script will:
- ✅ Check Python version
- ✅ Create virtual environment
- ✅ Install dependencies
- ✅ Verify Flask is working
- ✅ Guide email configuration

**Follow the prompts and answer 'y' when asked to start the app.**

---

## Alternative: Manual Setup

If you prefer to set up manually, follow these steps:

### 1. Create Virtual Environment

```powershell
python -m venv venv
venv\Scripts\activate
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure Email (Optional)

Open `app.py` with a text editor and find these lines (around line 15-20):

```python
ADMIN_EMAIL = "admin@example.com"
FROM_EMAIL = "noreply@example.com"
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USERNAME = "your-email@gmail.com"
MAIL_PASSWORD = "app-password"  # For Gmail, use App Password
```

Update with your email settings:
- **ADMIN_EMAIL**: Where you want admin notifications sent
- **FROM_EMAIL**: Sender email address
- **MAIL_SERVER**: Your SMTP server (smtp.gmail.com for Gmail)
- **MAIL_USERNAME**: Your email login
- **MAIL_PASSWORD**: Your email password or app password

**For Gmail Users:**
- Go to https://myaccount.google.com/apppasswords
- Select Mail and Windows Computer
- Use the 16-character password provided

### 4. Start the Application

```powershell
python app.py
```

### 5. Open in Browser

Navigate to: **http://localhost:5000**

You should see the PHEMEDAA landing page with 5 form links!

---

## Test the Application

1. Click on any form (e.g., "Background Checks")
2. Fill in some test data
3. Click "Submit Form"
4. Check your email for:
   - **Admin notification** with form data (sent to ADMIN_EMAIL)
   - **User confirmation** with submitted information (sent to form email field)

---

## Project Structure

```
forms/
├── app.py                           ← Main application (configure email here)
├── requirements.txt                 ← Dependencies (already set up)
├── templates/                       ← 7 HTML templates for forms
│   ├── base.html
│   ├── index.html
│   ├── backgroundchecks.html
│   ├── declarationbyemployee.html
│   ├── guarantorundertaking.html
│   ├── serviceagreement.html
│   └── trackingagreement.html
└── static/
    └── styles.css                   ← Responsive styling
```

---

## Email Configuration Examples

### Gmail Setup

```python
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USERNAME = "your-email@gmail.com"
MAIL_PASSWORD = "xxxx xxxx xxxx xxxx"  # 16-char app password from Google
```

### Outlook/Office 365

```python
MAIL_SERVER = "smtp.office365.com"
MAIL_PORT = 587
MAIL_USERNAME = "you@outlook.com"
MAIL_PASSWORD = "your-outlook-password"
```

### Corporate Email

Ask your IT department for SMTP settings, then configure accordingly.

---

## Stop the Application

Press **Ctrl+C** in the terminal to stop the Flask server.

---

## Need Help?

- **Setup issues?** See `README_FLASK.md`
- **Complete overview?** See `FLASK_MIGRATION_COMPLETE.md`
- **Forms not working?** Check Flask terminal output for errors
- **Email not sending?** Verify configuration in `app.py` and check spam folder

---

## What's New from PHP Version?

✅ **Same Functionality**
- 5 professional forms
- Email notifications
- Responsive design
- Form validation

✅ **Better Technology**
- Python instead of PHP
- Flask framework (modern & flexible)
- Easier to customize
- Better error handling

✅ **Same User Experience**
- Same forms and fields
- Same design and styling
- Same email features
- Same professional look

---

## Common Questions

**Q: Can I customize the forms?**  
A: Yes! Edit the templates in the `templates/` folder to add/remove fields.

**Q: Can I change colors/logo?**  
A: Yes! Edit `static/styles.css` for colors and `templates/base.html` for logo.

**Q: Can I host this online?**  
A: Yes! See deployment guide in `README_FLASK.md` for Heroku, Azure, or other platforms.

**Q: How do I modify form fields?**  
A: Edit the HTML in the form template files. New fields are automatically sent by email.

**Q: Is this production-ready?**  
A: For internal use, yes. For public use, add CSRF protection (see README_FLASK.md).

---

## Time to Launch

- ⏱️ **Setup:** 2-3 minutes (with setup.py)
- ⏱️ **Email config:** 2-3 minutes
- ⏱️ **Testing:** 1-2 minutes

**Total: About 5 minutes to have your forms portal running!**

---

## Let's Get Started!

### Run This Now:

```powershell
python setup.py
```

Then follow the prompts. Your forms portal will be running locally in minutes! 🚀

---

Happy form handling! If you have questions, see the detailed documentation in `README_FLASK.md`.
