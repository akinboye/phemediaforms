#!/usr/bin/env python
"""
PHEMEDAA Forms Portal - Flask Version
Quick Setup and Test Script

This script helps you set up the Flask application and verify everything is working correctly.
"""

import os
import sys
import subprocess
import platform

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def print_step(step_num, text):
    """Print a numbered step"""
    print(f"\n[Step {step_num}] {text}")
    print("-" * 50)

def check_python():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"❌ Python 3.7+ required. You have Python {version.major}.{version.minor}")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def create_venv():
    """Create virtual environment"""
    venv_dir = "venv"
    if os.path.exists(venv_dir):
        print(f"✓ Virtual environment already exists at {venv_dir}")
        return True
    
    print(f"Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
        print(f"✓ Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def get_pip_command():
    """Get the correct pip command for the current platform"""
    if platform.system() == "Windows":
        return "venv\\Scripts\\pip"
    else:
        return "venv/bin/pip"

def get_python_command():
    """Get the correct python command for the current platform"""
    if platform.system() == "Windows":
        return "venv\\Scripts\\python"
    else:
        return "venv/bin/python"

def install_requirements():
    """Install Python dependencies"""
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found!")
        return False
    
    pip_cmd = get_pip_command()
    print("Installing dependencies from requirements.txt...")
    try:
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_flask():
    """Check if Flask is properly installed"""
    python_cmd = get_python_command()
    try:
        result = subprocess.run([python_cmd, "-c", "import flask; print(flask.__version__)"], 
                              capture_output=True, text=True, check=True)
        flask_version = result.stdout.strip()
        print(f"✓ Flask {flask_version} is installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Flask is not properly installed. Please run: pip install -r requirements.txt")
        return False

def test_app():
    """Test if the Flask app can start"""
    python_cmd = get_python_command()
    print("Testing Flask application...")
    
    test_code = """
import sys
sys.path.insert(0, '.')
from app import app
with app.app_context():
    print("✓ Flask app initialized successfully")
    print("✓ All routes are configured")
"""
    
    try:
        subprocess.run([python_cmd, "-c", test_code], check=True, timeout=5)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error testing Flask app: {e}")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Flask app test timed out")
        return False

def configure_email():
    """Guide user through email configuration"""
    print_step(5, "Email Configuration")
    print("""
To enable email functionality, you need to configure SMTP settings:

1. Open app.py in your text editor
2. Find the email configuration section (around lines 15-20):

    ADMIN_EMAIL = "admin@example.com"
    FROM_EMAIL = "noreply@example.com"
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USERNAME = "your-email@gmail.com"
    MAIL_PASSWORD = "your-app-password"

3. Replace with your actual email settings:

   For Gmail:
   - MAIL_SERVER = "smtp.gmail.com"
   - MAIL_PORT = 587
   - MAIL_USERNAME = your Gmail address
   - MAIL_PASSWORD = Create an App Password (https://myaccount.google.com/apppasswords)

   For Outlook:
   - MAIL_SERVER = "smtp.office365.com"
   - MAIL_PORT = 587
   - MAIL_USERNAME = your Outlook email
   - MAIL_PASSWORD = your Outlook password

4. Save the file

⚠️  Important: Never commit MAIL_PASSWORD to version control!
""")

def show_startup_info():
    """Show startup information"""
    platform_name = "Windows" if platform.system() == "Windows" else "macOS/Linux"
    
    print_step(6, "Starting the Application")
    print(f"""
Your Flask application is now ready to use!

To start the application, run:

  {get_python_command()} app.py

Or if you prefer:

  flask run

The application will start at: http://localhost:5000

Once started:
1. Open your browser to http://localhost:5000
2. Click on any form to test
3. Fill in the fields and submit
4. Check your email for test submissions

✓ To stop the application, press Ctrl+C

📝 For more information, see README_FLASK.md
""")

def main():
    """Main setup routine"""
    print_header("PHEMEDAA Forms Portal - Flask Setup")
    
    print("Welcome! This script will help you set up the Flask Forms Portal.")
    print("Let's make sure everything is configured correctly...\n")
    
    # Step 1: Check Python
    print_step(1, "Checking Python Version")
    if not check_python():
        print("❌ Setup failed. Please install Python 3.7 or higher.")
        sys.exit(1)
    
    # Step 2: Create virtual environment
    print_step(2, "Setting Up Virtual Environment")
    if not create_venv():
        print("❌ Setup failed. Could not create virtual environment.")
        sys.exit(1)
    
    # Step 3: Install dependencies
    print_step(3, "Installing Dependencies")
    if not install_requirements():
        print("❌ Setup failed. Could not install dependencies.")
        sys.exit(1)
    
    # Step 4: Check Flask
    print_step(4, "Verifying Flask Installation")
    if not check_flask():
        print("❌ Setup failed. Flask not properly installed.")
        sys.exit(1)
    
    # Step 5: Email configuration info
    configure_email()
    
    # Step 6: Show startup info
    show_startup_info()
    
    print_header("Setup Complete!")
    print("✅ All checks passed! Your Flask application is ready.")
    print("\nNext steps:")
    print("1. Configure email settings in app.py")
    print("2. Run: " + get_python_command() + " app.py")
    print("3. Open http://localhost:5000 in your browser")
    
    response = input("\nWould you like to start the application now? (y/n): ").lower().strip()
    if response == 'y':
        print("\nStarting Flask application...")
        python_cmd = get_python_command()
        os.system(f"{python_cmd} app.py")

if __name__ == "__main__":
    main()
