"""
Email Configuration Test
Test the PHEMEDAA email settings
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_email_configuration():
    """Test email sending with the configured settings"""
    
    email_config = {
        'server': 'mail.phemediaa.com',
        'port': 465,
        'username': 'admin@phemediaa.com',
        'password': '@phemediaadmin123456_',
        'use_ssl': True
    }
    
    print("Testing Email Configuration")
    print("=" * 50)
    print(f"Server: {email_config['server']}")
    print(f"Port: {email_config['port']}")
    print(f"Username: {email_config['username']}")
    print(f"SSL: {email_config['use_ssl']}")
    print("=" * 50)
    
    try:
        if email_config['use_ssl']:
            # Use SSL/TLS connection (port 465)
            server = smtplib.SMTP_SSL(email_config['server'], email_config['port'], timeout=10)
        else:
            # Use STARTTLS connection (port 587)
            server = smtplib.SMTP(email_config['server'], email_config['port'], timeout=10)
            server.starttls()
        
        print("✓ Connected to mail server")
        
        # Login
        server.login(email_config['username'], email_config['password'])
        print("✓ Authentication successful")
        
        # Create test email
        msg = MIMEMultipart()
        msg['From'] = email_config['username']
        msg['To'] = email_config['username']
        msg['Subject'] = 'PHEMEDAA Forms - Configuration Test'
        
        body = """
This is a test email to verify the email configuration for PHEMEDAA Forms Portal.

If you received this email, the email settings are working correctly!

Email Details:
- Server: mail.phemediaa.com
- Port: 465
- Account: admin@phemediaa.com

Best regards,
PHEMEDAA Forms Portal
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server.send_message(msg)
        print("✓ Test email sent successfully")
        
        server.quit()
        print("\n✓ Email configuration is working correctly!")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"\n✗ Authentication Failed: {e}")
        print("Please check your username and password")
        return False
    except smtplib.SMTPException as e:
        print(f"\n✗ SMTP Error: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Connection Error: {e}")
        print("Please ensure:")
        print("1. mail.phemediaa.com is accessible")
        print("2. Port 465 is open")
        print("3. Your internet connection is working")
        return False

if __name__ == '__main__':
    test_email_configuration()
