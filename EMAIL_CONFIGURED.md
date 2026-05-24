# ✅ Email Configuration Updated

## Current Email Settings

Your PHEMEDAA Forms Portal has been configured with the following contact emails:

### Email Configuration
- **Admin Email (receives form submissions)**: info@phemediaa.com
- **Sender Email (from address)**: femioluwole1@gmail.com
- **Support Email (displayed on site)**: info@phemediaa.com
- **SMTP Server**: smtp.gmail.com (Gmail)
- **SMTP Port**: 587
- **TLS Enabled**: Yes

## Next Step: Set Gmail App Password

For the email system to work, you need to generate an **App Password** from your Google Account:

1. Go to: https://myaccount.google.com/apppasswords
2. Sign in with: `femioluwole1@gmail.com`
3. Select "Mail" and "Windows Computer"
4. Google will generate a **16-character password**
5. Copy this password
6. Open `app.py` and update line 30:
   ```python
   MAIL_PASSWORD = 'xxxx xxxx xxxx xxxx'  # Paste your 16-char password here
   ```

## Email Flow

When a user submits a form from your website:

1. **User fills in form** → Click Submit
2. **Admin Notification Email** sent to: `info@phemediaa.com`
   - Contains: All form data in HTML format
   - From: `femioluwole1@gmail.com`
3. **User Confirmation Email** sent to: User's email from form
   - Contains: Confirmation message
   - From: `femioluwole1@gmail.com`

## Testing

Once you set the app password:

1. Start the Flask app: `python app.py`
2. Open: http://localhost:5000
3. Fill out and submit a test form
4. Check inbox for emails:
   - Admin notification at `info@phemediaa.com`
   - User confirmation at your test email

## Important Notes

⚠️ **Security**:
- Keep the App Password secure - don't share it
- Don't commit it to version control
- This is NOT your regular Gmail password

ℹ️ **Gmail 2FA Requirement**:
- App Passwords only work if you have 2-Factor Authentication enabled
- If you need help, see Gmail Security Settings: https://support.google.com/accounts/answer/185833

✅ **Email Forwarding**:
- Admins can optionally set up email forwarding from `info@phemediaa.com` to personal emails
- This ensures you don't miss form submissions

## Current File Locations

- **Configuration File**: `app.py` (line 19-30)
- **Email Templates**: Inside `app.py` (functions `generate_admin_email()` and `generate_user_email()`)
- **Form Templates**: `templates/` folder

## Files Updated

Updated `app.py` with:
- ✅ ADMIN_EMAIL = 'info@phemediaa.com'
- ✅ FROM_EMAIL = 'femioluwole1@gmail.com'
- ✅ SUPPORT_EMAIL = 'info@phemediaa.com'
- ✅ MAIL_SERVER = 'smtp.gmail.com'
- ✅ MAIL_PORT = 587
- ✅ TLS enabled

---

## Ready to Launch?

1. **Set App Password** in `app.py` line 30
2. **Start Flask**: `python app.py`
3. **Open browser**: http://localhost:5000
4. **Test a form**: Fill and submit test data
5. **Verify emails**: Check Gmail inbox

**Questions?** See `README_FLASK.md` for detailed email setup guide.
