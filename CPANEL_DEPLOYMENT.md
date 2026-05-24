# Deploying PHEMEDAA Forms Portal on cPanel

Complete guide for deploying the Flask application on cPanel hosting.

## Prerequisites

- cPanel hosting account with SSH access
- Python 3.7+ support on your hosting
- MySQL database access (usually included)
- Domain name pointing to your hosting

## Step 1: Connect via SSH

1. Open Terminal/PuTTY
2. Connect to your server:
```bash
ssh username@yourdomain.com
```

Replace `username` with your cPanel username and `yourdomain.com` with your actual domain.

## Step 2: Clone the Repository

Navigate to the public_html or desired directory:

```bash
cd ~/public_html
# OR for a subdomain
cd ~/public_html/subdomain_folder
```

Clone the repository:
```bash
git clone https://github.com/akinboye/phemediaforms.git
cd phemediaforms
```

## Step 3: Set Up Python Virtual Environment

Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 4: Configure MySQL Database

### Option A: Use cPanel MySQL

1. Log into cPanel
2. Go to **MySQL Databases**
3. Create a new database named `phemedaa_forms`
4. Create a MySQL user with full privileges
5. Update the database URI in `app.py`

### Option B: Remote MySQL

If using remote MySQL (like your local machine), ensure the connection string in `app.py` is correct:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:$Albert2022%23@localhost:3306/phemedaa_forms'
```

### Initialize the Database

Via SSH (while in the project directory with venv activated):

```bash
python setup_mysql.py
python init_admins.py
```

## Step 5: Create WSGI Application File

Create a file named `wsgi.py` in your project root:

```python
"""
WSGI entry point for cPanel/Passenger
"""
import sys
import os

# Add project directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Activate virtual environment
activate_this = os.path.join(os.path.dirname(__file__), 'venv', 'bin', 'activate_this.py')
exec(open(activate_this).read(), {'__file__': activate_this})

# Import the Flask app
from app import app as application
```

## Step 6: Configure cPanel App Manager (Passenger)

1. Log into cPanel
2. Go to **Setup Node.js App** or **Setup Python App** (depends on your cPanel version)
3. Click **Create Application**
4. Fill in the details:
   - **Node.js/Python Version**: Select your Python version (3.7+)
   - **Application root**: Point to your project directory (`/home/username/public_html/phemediaforms`)
   - **Application startup file**: `wsgi.py`
   - **Application Environment**: Set to `production`
   - **Application URL**: Your domain name

5. Click **Create**

cPanel will automatically:
- Set up Passenger
- Configure the web server
- Create necessary config files
- Restart the application

## Step 7: Configure Environment Variables (Optional)

Create a `.env` file in your project root:

```bash
SECRET_KEY=your-secure-secret-key-here
FLASK_ENV=production
```

Update your `app.py` to load from `.env`:
```python
from dotenv import load_dotenv
load_dotenv()
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'phemedaa-forms-secret-key-2026')
```

## Step 8: Set Up SSL Certificate

### Using AutoSSL (Recommended)

1. In cPanel, go to **AutoSSL**
2. Click **Check for new certificates**
3. Once issued, your domain will be HTTPS-enabled

### Manual SSL

1. Go to **SSL/TLS Manager** in cPanel
2. Upload your SSL certificate
3. Install it on your domain

## Step 9: Configure Firewall Rules (if applicable)

Ensure port 3306 (MySQL) is open if using remote MySQL:

```bash
sudo ufw allow 3306
```

## Step 10: File Permissions

Ensure proper permissions:

```bash
cd ~/public_html/phemediaforms
chmod 755 .
chmod 755 venv
chmod 644 app.py models.py auth.py requirements.txt
chmod 755 uploads uploads/agreements uploads/stamps
```

## Step 11: Test the Application

Visit your domain in a browser:
- **Home**: `https://yourdomain.com`
- **Admin Login**: `https://yourdomain.com/admin_login`

Test with credentials:
- **SuperAdmin**: username=`admin`, password=`admin123`
- **Admin**: username=`user`, password=`user123`

## Step 12: Configure Email (Important)

Update the email settings in `app.py` to use your cPanel email:

```python
MAIL_SERVER = 'mail.phemediaa.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'admin@phemediaa.com'
MAIL_PASSWORD = '@phemediaadmin123456_'
```

Or use cPanel's local mail server:
```python
MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_USE_TLS = False
MAIL_USERNAME = 'your-email@yourdomain.com'
MAIL_PASSWORD = 'your-email-password'
```

## Step 13: Enable Error Logging

Create a logs directory:
```bash
mkdir -p ~/public_html/phemediaforms/logs
chmod 755 logs
```

Update `app.py` to log errors:
```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/phemediaa_forms.log', maxBytes=10240000, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

## Step 14: Set Up Auto-Restart (Optional)

Create a cron job to restart the app if it crashes:

1. In cPanel, go to **Cron Jobs**
2. Add this entry:
```bash
* * * * * /home/username/public_html/phemediaforms/venv/bin/python /home/username/public_html/phemediaforms/app.py
```

Or use Passenger's auto-restart:
- Create a file: `tmp/restart.txt`
- Touch this file whenever you need to restart

## Troubleshooting

### 500 Internal Server Error
- Check error logs: `tail -f logs/phemediaa_forms.log`
- Verify database connection
- Check file permissions

### Database Connection Issues
- Verify MySQL credentials in `app.py`
- Ensure MySQL service is running
- Check firewall rules

### Module Import Errors
- Verify virtual environment is activated
- Re-run `pip install -r requirements.txt`
- Check Python version compatibility

### Permission Denied Errors
- Run `chmod 755` on required directories
- Ensure www-data/nobody user owns files

### Email Not Sending
- Test with `python test_email_config.py`
- Verify mail server credentials
- Check firewall rules for SMTP ports

## Accessing cPanel Features

| Feature | URL | Purpose |
|---------|-----|---------|
| File Manager | cPanel → File Manager | Manage files |
| MySQL | cPanel → MySQL Databases | Manage databases |
| SSH | cPanel → Terminal | SSH access |
| Logs | cPanel → Raw Access Logs | View server logs |
| Backups | cPanel → Backups | Backup your app |
| SSL | cPanel → SSL/TLS Manager | Install SSL cert |

## Security Recommendations

1. **Change default admin credentials**:
   ```bash
   python init_admins.py
   ```

2. **Use strong SECRET_KEY**:
   ```python
   app.config['SECRET_KEY'] = 'your-very-secure-random-key'
   ```

3. **Enable HTTPS** (AutoSSL recommended)

4. **Set up regular backups** in cPanel

5. **Monitor error logs** regularly

6. **Keep dependencies updated**:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

## Updating the Application

To update your application on cPanel:

```bash
cd ~/public_html/phemediaforms
source venv/bin/activate
git pull origin master
pip install --upgrade -r requirements.txt
touch tmp/restart.txt  # Restart Passenger
```

## Database Backups

### Manual Backup
```bash
mysqldump -u username -p database_name > backup.sql
```

### Via cPanel
1. Go to **Backups**
2. Click **Download a backup**
3. Select the database and files to backup

## Performance Tips

1. **Enable Gzip Compression** in cPanel
2. **Use caching** for static files
3. **Enable CloudFlare** (if available)
4. **Monitor resource usage** in cPanel
5. **Optimize database queries**

## Support & Documentation

- **cPanel Docs**: https://docs.cpanel.net/
- **Flask Docs**: https://flask.palletsprojects.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **Passenger Docs**: https://www.phusionpassenger.com/docs/

## Next Steps

After deployment:
1. ✓ Test all form submissions
2. ✓ Verify email notifications
3. ✓ Test admin approval workflow
4. ✓ Set up monitoring/alerts
5. ✓ Configure regular backups
6. ✓ Document any custom configurations

---

For questions or issues, contact: info@phemediaa.com
