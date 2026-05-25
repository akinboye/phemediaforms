"""
PHEMEDAA Forms Portal - Flask Application
Main application file with all routes and logic
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, send_file
from flask_wtf.csrf import CSRFProtect
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import base64
import re
import os
import time
import uuid
from functools import wraps
from werkzeug.utils import secure_filename
from models import db, SuperAdmin, Admin, NotificationEmail, FormSubmission, CompanyAddress, ApprovalStamp
from auth import hash_password, verify_password, is_superadmin_logged_in, is_admin_logged_in, get_current_superadmin, get_current_admin, require_superadmin, require_admin_or_superadmin

# Try to import PDF generation libraries
try:
    from fpdf import FPDF
    HAS_PDF_SUPPORT = True
except ImportError:
    HAS_PDF_SUPPORT = False

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'phemedaa-forms-secret-key-2026')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://mzerisoh_phemediauser:%40phemediaadmin123456_@localhost:3306/mzerisoh_phemediaaform'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Security Configuration
csrf = CSRFProtect(app)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_DURATION'] = timedelta(hours=24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['WTF_CSRF_TIME_LIMIT'] = None  # No time limit for CSRF tokens

# File upload configuration
UPLOADS_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
STAMPS_FOLDER = os.path.join(UPLOADS_FOLDER, 'stamps')
PDFS_FOLDER = os.path.join(UPLOADS_FOLDER, 'agreements')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Create upload directories
for folder in [UPLOADS_FOLDER, STAMPS_FOLDER, PDFS_FOLDER]:
    os.makedirs(folder, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOADS_FOLDER
app.config['STAMPS_FOLDER'] = STAMPS_FOLDER
app.config['PDFS_FOLDER'] = PDFS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size

# Initialize SQLAlchemy
db.init_app(app)

# Create database tables on startup
with app.app_context():
    db.create_all()

# Configuration
ADMIN_EMAIL = 'info@phemediaa.com'
FROM_EMAIL = 'femioluwole1@gmail.com'
COMPANY_NAME = 'PHEMEDAA'
SUPPORT_EMAIL = 'info@phemediaa.com'
SUPPORT_PHONE = '+234 803 231 7546'

# Email Server Configuration
MAIL_SERVER = 'mail.phemediaa.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'admin@phemediaa.com'
MAIL_PASSWORD = '@phemediaadmin123456_'

# Form metadata
FORM_TYPES = {
    'backgroundcheck': {
        'title': 'Background Check Form',
        'icon': '📋',
        'description': 'Complete your background check submission form.',
    },
    'clientengagement': {
        'title': 'Client Engagement Form & Agreement',
        'icon': '🏢',
        'description': 'Submit your client engagement agreement for security services.',
    },
    'declarationbyemployee': {
        'title': 'Declaration by Employee Form',
        'icon': '📝',
        'description': 'Submit your employee declaration form.',
    },
    'guarantorundertaking': {
        'title': 'Guarantor Undertaking',
        'icon': '🤝',
        'description': 'Submit your guarantor undertaking agreement.',
    },
    'serviceagreement': {
        'title': 'Service Agreement',
        'icon': '✅',
        'description': 'Review and sign our service agreement.',
    },
    'trackingagreement': {
        'title': 'Tracking Agreement',
        'icon': '📍',
        'description': 'Submit your tracking agreement form.',
    },
    'oilgasservicerequest': {
        'title': 'Oil & Gas Service Request',
        'icon': '⛽',
        'description': 'Submit your service request for oil & gas sector operations.',
    }
}


# Security Headers Middleware
@app.after_request
def set_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    # Content Security Policy - allows styles and scripts from same origin
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://unpkg.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; img-src 'self' data:; font-src 'self' https://fonts.gstatic.com; connect-src 'self' https://unpkg.com"
    return response


def sanitize_input(user_input):
    """Sanitize user input - remove potentially dangerous characters"""
    if isinstance(user_input, str):
        # Strip whitespace
        user_input = user_input.strip()
        # Remove null bytes
        user_input = user_input.replace('\x00', '')
        return user_input
    return user_input


def validate_email(email):
    """Validate email format"""
    if not email or not isinstance(email, str):
        return False
    email = sanitize_input(email).lower()
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None and len(email) <= 255


def validate_phone(phone):
    """Validate phone number format"""
    if not phone or not isinstance(phone, str):
        return False
    phone = sanitize_input(phone)
    # Allow digits, +, -, spaces, parentheses
    pattern = r'^[\d\s+\-()]{7,20}$'
    return bool(re.match(pattern, phone))


def validate_form_type(form_type):
    """Validate form type is in allowed list"""
    return form_type in FORM_TYPES


def escape_html(text):
    """Escape HTML special characters"""
    if not isinstance(text, str):
        text = str(text)
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&#x27;"))


def send_email(recipient, subject, html_content):
    """Send email to recipient"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = FROM_EMAIL
        msg['To'] = recipient

        msg.attach(MIMEText(html_content, 'html'))

        # Try sending with local mail server
        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            if MAIL_USE_TLS:
                server.starttls()
            if MAIL_USERNAME and MAIL_PASSWORD:
                server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False


def generate_admin_email(form_type, form_data):
    """Generate HTML email for admin"""
    form_title = FORM_TYPES.get(form_type, {}).get('title', form_type)
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Poppins', 'Segoe UI', sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .form-section {{ margin-bottom: 20px; border-bottom: 1px solid #ddd; padding-bottom: 15px; }}
        .form-group {{ margin-bottom: 15px; }}
        .label {{ font-weight: bold; color: #2c3e50; }}
        .value {{ margin-top: 5px; padding: 8px; background-color: #ecf0f1; border-radius: 4px; }}
        .footer {{ background-color: #f5f5f5; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class='header'>
        <h2>PHEMEDAA Form Submission</h2>
    </div>
    <div class='content'>
        <p>A new form has been submitted. Please find the details below:</p>
        <div class='form-section'>
            <div class='form-group'>
                <div class='label'>Form Type:</div>
                <div class='value'>{form_title}</div>
            </div>
            <div class='form-group'>
                <div class='label'>Submission Date:</div>
                <div class='value'>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
            </div>
        </div>
        <div class='form-section'><h3>Form Details:</h3>
"""
    
    for key, value in form_data.items():
        if value:
            display_key = key.replace('_', ' ').title()
            if isinstance(value, list):
                value = ', '.join(value)
            html += f"""
            <div class='form-group'>
                <div class='label'>{display_key}:</div>
                <div class='value'>{value}</div>
            </div>"""
    
    html += """
        </div>
    </div>
    <div class='footer'>
        <p>&copy; 2026 PHEMEDAA. All rights reserved.</p>
        <p>This is an automated message. Please do not reply to this email.</p>
    </div>
</body>
</html>"""
    
    return html


def generate_user_email(form_type):
    """Generate confirmation email for user"""
    form_title = FORM_TYPES.get(form_type, {}).get('title', form_type)
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Poppins', 'Segoe UI', sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background-color: #27ae60; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .footer {{ background-color: #f5f5f5; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class='header'>
        <h2>Form Submission Confirmation</h2>
    </div>
    <div class='content'>
        <p>Thank you for submitting your form!</p>
        <p>We have received your <strong>{form_title}</strong> submission on <strong>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</strong>.</p>
        <p>Our team will review your submission and contact you shortly if we need any additional information.</p>
        <p>Best regards,<br>{COMPANY_NAME} Team</p>
    </div>
    <div class='footer'>
        <p>&copy; 2026 PHEMEDAA. All rights reserved.</p>
    </div>
</body>
</html>"""
    
    return html


def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def send_email_with_attachment(recipient, subject, html_content, attachment_path=None, attachment_filename=None):
    """Send email to recipient with optional attachment"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = FROM_EMAIL
        msg['To'] = recipient

        msg.attach(MIMEText(html_content, 'html'))

        # Attach file if provided
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename= {attachment_filename or os.path.basename(attachment_path)}')
                msg.attach(part)

        # Try sending with local mail server
        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            if MAIL_USE_TLS:
                server.starttls()
            if MAIL_USERNAME and MAIL_PASSWORD:
                server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"Error sending email with attachment: {str(e)}")
        return False


def add_pdf_header(pdf, title, subtitle="Approved & Certified Document"):
    """Add consistent header to PDF with logo and centered title"""
    try:
        # Add logo on top left (if it exists)
        logo_path = os.path.join(os.path.dirname(__file__), 'static', 'logo.png')
        if os.path.exists(logo_path):
            pdf.image(logo_path, x=10, y=10, w=30)
        
        # Move to just below logo area for company info
        pdf.ln(10)
        
        # Company header (centered, full width)
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 8, "PHEMEDIA ONGUARD SERVICES LTD", ln=True, align="C")
        
        # RC Number (centered, bold and bigger)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 4, "R C 8218219", ln=True, align="C")
        
        # Bank account details (centered)
        pdf.set_font("Helvetica", "", 8)
        pdf.cell(0, 3, "Bank: Moniepoint | Account: 6707932476 | Account Name: Phemedia Onguard Services LTD", ln=True, align="C")
        
        # Line separator
        pdf.ln(2)
        pdf.set_draw_color(52, 152, 219)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(3)
        
        # Title (centered, bold)
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 8, title, ln=True, align="C")
        
        # Subtitle (centered)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 5, subtitle, ln=True, align="C")
        
        pdf.ln(2)
        
    except Exception as e:
        print(f"Error adding PDF header: {str(e)}")


def add_signatures_to_pdf(pdf, form_data, submission_id, signature_label="Signature:", start_x=20, sig_width=35, sig_height=20):
    """
    Add both drawn and uploaded signatures to PDF side by side if both exist
    Returns True if any signature was added, False otherwise
    """
    sig_added = False
    drawn_sig_path = None
    uploaded_sig_path = None
    
    try:
        # Handle drawn signature
        drawn_sig_data = form_data.get('clientSignatureData_drawn', '')
        if drawn_sig_data and drawn_sig_data.startswith('data:image/png;base64,'):
            try:
                sig_base64 = drawn_sig_data.replace('data:image/png;base64,', '')
                sig_bytes = base64.b64decode(sig_base64)
                drawn_sig_path = os.path.join(PDFS_FOLDER, f'temp_drawn_sig_{submission_id}_{int(time.time() * 1000)}_{id(sig_bytes)}.png')
                with open(drawn_sig_path, 'wb') as f:
                    f.write(sig_bytes)
                sig_added = True
            except Exception as e:
                print(f"Error processing drawn signature: {str(e)}")
                drawn_sig_path = None
        
        # Handle uploaded signature
        uploaded_sig_data = form_data.get('clientSignatureData_uploaded', '')
        if uploaded_sig_data and (uploaded_sig_data.startswith('data:image/') or uploaded_sig_data.startswith('data:application/octet-stream')):
            try:
                # Extract base64 data
                if 'base64,' in uploaded_sig_data:
                    sig_base64 = uploaded_sig_data.split('base64,')[1]
                else:
                    sig_base64 = uploaded_sig_data
                sig_bytes = base64.b64decode(sig_base64)
                uploaded_sig_path = os.path.join(PDFS_FOLDER, f'temp_uploaded_sig_{submission_id}_{int(time.time() * 1000)}_{id(sig_bytes)}.png')
                with open(uploaded_sig_path, 'wb') as f:
                    f.write(sig_bytes)
                sig_added = True
            except Exception as e:
                print(f"Error processing uploaded signature: {str(e)}")
                uploaded_sig_path = None
        
        # Add signatures to PDF
        if sig_added:
            pdf.set_font("helvetica", "B", 8)
            pdf.cell(0, 3, signature_label, ln=True)
            
            current_y = pdf.get_y()
            
            # Add drawn signature
            if drawn_sig_path and os.path.exists(drawn_sig_path):
                try:
                    pdf.set_font("helvetica", "", 7)
                    pdf.text(start_x, current_y + sig_height + 2, "Drawn Signature:")
                    pdf.image(drawn_sig_path, x=start_x, y=current_y, w=sig_width, h=sig_height)
                except Exception as e:
                    print(f"Error adding drawn signature to PDF: {str(e)}")
            
            # Add uploaded signature
            if uploaded_sig_path and os.path.exists(uploaded_sig_path):
                try:
                    uploaded_x = start_x + sig_width + 10
                    pdf.set_font("helvetica", "", 7)
                    pdf.text(uploaded_x, current_y + sig_height + 2, "Uploaded Signature:")
                    pdf.image(uploaded_sig_path, x=uploaded_x, y=current_y, w=sig_width, h=sig_height)
                except Exception as e:
                    print(f"Error adding uploaded signature to PDF: {str(e)}")
            
            # Move down for next content
            pdf.ln(sig_height + 8)
        
        return sig_added
        
    finally:
        # Clean up temporary files
        for sig_path in [drawn_sig_path, uploaded_sig_path]:
            if sig_path and os.path.exists(sig_path):
                try:
                    os.remove(sig_path)
                except:
                    pass


def generate_service_agreement_pdf(submission_id, stamp_path=None, stamp_drawn_path=None, output_path=None, approver_name=None, approver_email=None, approver_position=None):
    """
    Generate professional PDF using fpdf2
    stamp_path: Optional path to approval signature/stamp image to include at bottom
    output_path: Optional specific output path for the PDF
    approver_name: Optional approver name for approval section
    approver_email: Optional approver email for approval section
    approver_position: Optional approver position/title
    Returns: Path to generated PDF or None if failed
    """
    print(f"[generate_service_agreement_pdf] Called with submission_id={submission_id}")
    try:
        submission = FormSubmission.query.get(submission_id)
        if not submission or submission.form_type != 'serviceagreement':
            return None
        
        # Get form data
        form_data = submission.submitted_data
        company_address = CompanyAddress.query.filter_by(is_active=True).first()
        
        # Determine output path
        if not output_path:
            pdf_filename = f'agreement_{submission_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            output_path = os.path.join(PDFS_FOLDER, pdf_filename)
        
        # Create PDF using fpdf2
        print(f"[generate_service_agreement_pdf] HAS_PDF_SUPPORT={HAS_PDF_SUPPORT}")
        if HAS_PDF_SUPPORT:
            try:
                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.set_margins(15, 15, 15)
                pdf.add_page()

                pdf_filename_base = os.path.basename(output_path)

                # Header
                add_pdf_header(pdf, "SERVICE AGREEMENT", "Professional Service Agreement Document")

                # Agreement Date line
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 5, f"Agreement Date: {form_data.get('agreement_date', 'N/A')} | Client Agreement Date: {form_data.get('client_agreement_date', 'N/A')}", ln=True)
                pdf.ln(2)

                # ==== CLIENT INFORMATION ====
                pdf.set_font("helvetica", "B", 12)
                pdf.set_fill_color(52, 152, 219)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 7, "CLIENT INFORMATION", ln=True, fill=True)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(1)

                for label, value in [
                    ("Client Name",        form_data.get('client_name', 'N/A')),
                    ("Client Address",     form_data.get('client_address', 'N/A')),
                    ("Client Phone",       form_data.get('client_phone', 'N/A')),
                    ("Client Email",       form_data.get('client_email', 'N/A')),
                    ("Representative",     form_data.get('client_sig_name', 'N/A')),
                    ("Designation",        form_data.get('client_designation', 'N/A')),
                ]:
                    pdf.set_font("helvetica", "B", 10)
                    pdf.cell(55, 5, f"{label}:", ln=False)
                    pdf.set_font("helvetica", "", 10)
                    pdf.cell(0, 5, str(value)[:80], ln=True)
                pdf.ln(2)

                # ==== SERVICE PROVIDER INFORMATION ====
                pdf.set_font("helvetica", "B", 12)
                pdf.set_fill_color(52, 152, 219)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 7, "SERVICE PROVIDER INFORMATION", ln=True, fill=True)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(1)

                company_addr = company_address.address if company_address else 'N/A'
                for label, value in [
                    ("Service Provider", "Phemedia Onguard Services Ltd"),
                    ("Address",          str(company_addr)[:80]),
                    ("Email",            "info@phemediaa.com"),
                    ("Telephone",        "08099180391, 0803231746"),
                    ("Website",          "www.phemediaa.com"),
                    ("Company Rep",      form_data.get('company_rep_name', 'N/A')),
                    ("Rep Designation",  form_data.get('company_rep_designation', 'N/A')),
                ]:
                    pdf.set_font("helvetica", "B", 10)
                    pdf.cell(55, 5, f"{label}:", ln=False)
                    pdf.set_font("helvetica", "", 10)
                    pdf.cell(0, 5, str(value), ln=True)
                pdf.ln(2)

                # ==== TERMS & CONDITIONS ====
                pdf.set_font("helvetica", "B", 12)
                pdf.set_fill_color(52, 152, 219)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 7, "TERMS & CONDITIONS", ln=True, fill=True)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(1)

                scope_text = form_data.get('scope_of_services', '') or \
                    "The Company shall provide the Client with professional security guards and/or spy police drivers in accordance with the terms of this Agreement."
                payment_text = form_data.get('payment_terms', '') or \
                    "The Client shall pay the Company the agreed service fees as stated in Schedule A. Payments shall be made in advance on a monthly basis unless otherwise agreed in writing."

                clauses = [
                    ("1. SCOPE OF SERVICES", scope_text),
                    ("2. PAYMENT TERMS", payment_text),
                    ("3. COMPANY'S OWNERSHIP OF PERSONNEL",
                     "All Personnel assigned to the Client remain employees of the Company at all times. The Client shall have no right, title, or interest in the employment relationship between the Company and its Personnel."),
                    ("4. NON-SOLICITATION & ANTI-POACHING CLAUSE",
                     "IMPORTANT: The Client shall not, directly or indirectly, employ, engage, or otherwise contract with any Personnel introduced or assigned by the Company during the term of this Agreement and after termination, without prior written consent of the Company. If the Client breaches this clause, the Client shall pay the Company liquidated damages equal to the Personnel's total annual remuneration."),
                    ("5. LIABILITY & INDEMNITY",
                     "The Client agrees to indemnify and hold harmless the Company against all claims, losses, damages, or expenses arising from the Client's actions, negligence, or failure to provide a safe working environment for the Personnel."),
                    ("6. TERMINATION",
                     "Either party may terminate this Agreement with 30 days' written notice. Termination shall not relieve the Client of obligations incurred before the termination date."),
                    ("7. GOVERNING LAW & DISPUTE RESOLUTION",
                     "This Agreement shall be governed by the laws of the Federal Republic of Nigeria. Any disputes shall be resolved through negotiation, failing which they shall be referred to arbitration in accordance with the Arbitration and Conciliation Act."),
                ]

                for title, body in clauses:
                    pdf.set_font("helvetica", "B", 10)
                    pdf.cell(0, 5, title, ln=True)
                    pdf.set_font("helvetica", "", 9)
                    pdf.multi_cell(0, 4, body)
                    # Bank details block appended after payment terms
                    if title == "2. PAYMENT TERMS":
                        pdf.ln(1)
                        pdf.set_font("helvetica", "B", 9)
                        pdf.cell(0, 4, "Payment Account Details:", ln=True)
                        pdf.set_font("helvetica", "", 9)
                        pdf.cell(0, 4, "Account Name: Phemedia Onguard Services Ltd", ln=True)
                        pdf.set_font("helvetica", "B", 9)
                        pdf.cell(45, 4, "Moniepoint Microfinance Bank:", ln=False)
                        pdf.set_font("helvetica", "", 9)
                        pdf.cell(0, 4, "6707932476", ln=True)
                        pdf.set_font("helvetica", "B", 9)
                        pdf.cell(45, 4, "Providus Bank:", ln=False)
                        pdf.set_font("helvetica", "", 9)
                        pdf.cell(0, 4, "1306872171", ln=True)
                    pdf.ln(1)
                pdf.ln(1)

                # ==== AGREEMENT ACKNOWLEDGMENT ====
                pdf.set_font("helvetica", "B", 12)
                pdf.set_fill_color(52, 152, 219)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 7, "AGREEMENT ACKNOWLEDGMENT", ln=True, fill=True)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(1)

                agreed = form_data.get('read_understand', '')
                agreed_sym = "[YES]" if agreed == 'yes' else "[ ]"
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(12, 5, agreed_sym, ln=False)
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 5, "I have read and fully understand this Service Agreement and agree to all terms and conditions", ln=True)
                pdf.ln(2)

                # ==== SIGNATURES ====
                pdf.set_font("helvetica", "B", 12)
                pdf.set_fill_color(52, 152, 219)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 7, "SIGNATURES", ln=True, fill=True)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(2)

                # Company / Admin Signature
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(0, 5, "FOR AND ON BEHALF OF PHEMEDIA ONGUARD SERVICES LTD:", ln=True)
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 5, f"Name: {form_data.get('company_rep_name', 'N/A')}", ln=True)
                pdf.cell(0, 5, f"Designation: {form_data.get('company_rep_designation', 'N/A')}", ln=True)
                pdf.ln(1)

                # Render company signature images from form_data
                comp_drawn_data = form_data.get('companySignatureData_drawn', '') or form_data.get('companySignatureData', '')
                comp_uploaded_data = form_data.get('companySignatureData_uploaded', '')
                comp_sig_y = pdf.get_y()
                comp_sig_x = pdf.l_margin
                comp_sig_w = 40
                comp_sig_h = 20
                any_comp_sig = False
                comp_temp_paths = []
                try:
                    for sig_data, suffix in [(comp_drawn_data, 'drawn'), (comp_uploaded_data, 'uploaded')]:
                        if sig_data and 'base64,' in sig_data:
                            raw = base64.b64decode(sig_data.split('base64,')[1])
                            tpath = os.path.join(PDFS_FOLDER, f'temp_comp_{suffix}_{submission_id}_{int(time.time())}.png')
                            with open(tpath, 'wb') as f:
                                f.write(raw)
                            comp_temp_paths.append(tpath)
                            x_pos = comp_sig_x + comp_sig_w + 10 if any_comp_sig else comp_sig_x
                            pdf.image(tpath, x=x_pos, y=comp_sig_y, w=comp_sig_w, h=comp_sig_h)
                            any_comp_sig = True
                except Exception:
                    pass
                finally:
                    for tp in comp_temp_paths:
                        try:
                            os.remove(tp)
                        except:
                            pass
                pdf.ln(comp_sig_h + 5) if any_comp_sig else pdf.ln(5)

                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 5, f"Date: {form_data.get('company_sig_date', 'N/A')}", ln=True)
                pdf.ln(3)

                # Client Signature
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(0, 5, "FOR AND ON BEHALF OF THE CLIENT:", ln=True)
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 5, f"Name: {form_data.get('client_sig_name', 'N/A')}", ln=True)
                pdf.cell(0, 5, f"Designation: {form_data.get('client_designation', 'N/A')}", ln=True)
                pdf.ln(1)

                add_signatures_to_pdf(pdf, form_data, submission_id, "Client Signature:")

                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 5, f"Date: {form_data.get('client_agreement_date', 'N/A')}", ln=True)
                pdf.ln(3)

                # ==== OFFICIAL APPROVAL (only shown when a stamp exists) ====
                if stamp_path or stamp_drawn_path:
                    pdf.set_font("helvetica", "B", 12)
                    pdf.set_fill_color(52, 152, 219)
                    pdf.set_text_color(255, 255, 255)
                    pdf.cell(0, 7, "OFFICIAL APPROVAL & CERTIFICATION", ln=True, fill=True)
                    pdf.set_text_color(0, 0, 0)
                    pdf.ln(1)

                    approval_date = submission.approved_at if submission.approved_at else datetime.now()
                    for label, value in [
                        ("Approved By",    approver_name or 'Company Representative'),
                        ("Position",       approver_position or 'N/A'),
                        ("Email",          approver_email or 'N/A'),
                        ("Approval Date",  approval_date.strftime('%d %B %Y at %H:%M:%S')),
                    ]:
                        pdf.set_font("helvetica", "B", 10)
                        pdf.cell(55, 5, f"{label}:", ln=False)
                        pdf.set_font("helvetica", "", 10)
                        pdf.cell(0, 5, str(value), ln=True)
                    pdf.ln(1)

                    pdf.set_font("helvetica", "B", 10)
                    pdf.cell(0, 5, "Official Approval Stamp & Signature:", ln=True)

                    sig_start_y = pdf.get_y()
                    sig_x = 20
                    sig_w = 50
                    sig_h = 25
                    any_sig = False
                    if stamp_drawn_path and os.path.exists(stamp_drawn_path):
                        try:
                            pdf.set_font("helvetica", "", 9)
                            pdf.text(sig_x, sig_start_y + sig_h + 4, "Drawn Signature:")
                            pdf.image(stamp_drawn_path, x=sig_x, y=sig_start_y, w=sig_w, h=sig_h)
                            any_sig = True
                        except Exception as e:
                            print(f"Error adding drawn admin signature: {str(e)}")
                    if stamp_path and os.path.exists(stamp_path):
                        try:
                            upload_x = sig_x + sig_w + 15 if any_sig else sig_x
                            pdf.set_font("helvetica", "", 9)
                            pdf.text(upload_x, sig_start_y + sig_h + 4, "Uploaded Stamp/Signature:")
                            pdf.image(stamp_path, x=upload_x, y=sig_start_y, w=sig_w, h=sig_h)
                            any_sig = True
                        except Exception as e:
                            print(f"Error adding uploaded admin signature: {str(e)}")
                    if any_sig:
                        pdf.ln(sig_h + 10)
                    else:
                        pdf.ln(18)
                    approval_date = submission.approved_at if submission.approved_at else datetime.now()
                    pdf.set_font("helvetica", "", 10)
                    pdf.cell(0, 5, f"Date: {approval_date.strftime('%d %B %Y at %H:%M:%S')}", ln=True)
                    pdf.ln(2)

                # Separator + Footer
                pdf.set_draw_color(189, 195, 199)
                pdf.line(15, pdf.get_y(), 195, pdf.get_y())
                pdf.ln(3)
                pdf.set_font("helvetica", "", 8)
                pdf.set_text_color(100, 100, 100)
                pdf.multi_cell(0, 4, "This is an official certified Service Agreement approved by Phemedia Onguard Services Ltd. This document is confidential and should be retained for compliance and audit purposes.", align="C")
                pdf.cell(0, 4, f"Generated: {datetime.now().strftime('%d %B %Y at %H:%M:%S')} | Ref: {pdf_filename_base}", ln=True, align="C")
                pdf.set_text_color(0, 0, 0)

                # Save PDF
                pdf.output(output_path)
                print(f"PDF successfully generated: {output_path}")
                return output_path

            except Exception as e:
                print(f"Error generating PDF with fpdf2: {str(e)}")
                return None
        else:
            print("fpdf2 not installed. Install it for PDF generation: pip install fpdf2")
            return None
            
    except Exception as e:
        print(f"Error in generate_service_agreement_pdf: {str(e)}")
        return None
            
    except Exception as e:
        print(f"Error generating service agreement PDF: {str(e)}")
        return None


def generate_backgroundchecks_approval_pdf(submission_id, stamp_path=None, stamp_drawn_path=None, approver_name=None, approver_email=None, approver_position=None):
    """
    Generate comprehensive PDF formatted like the form template with all terms and conditions
    """
    print(f"[generate_backgroundchecks_approval_pdf] Called with submission_id={submission_id}")
    try:
        submission = FormSubmission.query.get(submission_id)
        if not submission or submission.form_type != 'backgroundcheck':
            print(f"[generate_backgroundcheck_approval_pdf] Invalid submission or form type")
            return None
        
        # Get form data
        form_data = submission.submitted_data
        company_address = CompanyAddress.query.filter_by(is_active=True).first()
        
        # Determine output path
        pdf_filename = f'background_checks_approval_{submission_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        output_path = os.path.join(PDFS_FOLDER, pdf_filename)
        
        print(f"[generate_backgroundcheck_approval_pdf] HAS_PDF_SUPPORT={HAS_PDF_SUPPORT}")
        if HAS_PDF_SUPPORT:
            try:
                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.set_margins(15, 15, 15)
                pdf.add_page()
                
                # Add standard header with logo and title
                add_pdf_header(pdf, "BACKGROUND CHECK SERVICE AGREEMENT", "Approved & Certified Document")
                
                # Agreement Date
                pdf.set_font("helvetica", "", 10)
                agreement_date = form_data.get('agreement_date', 'N/A')
                client_agreement_date = form_data.get('client_agreement_date', 'N/A')
                pdf.cell(0, 5, f"Agreement Date: {agreement_date} | Client Agreement Date: {client_agreement_date}", ln=True)
                pdf.ln(2)
                
                # ==== CLIENT INFORMATION SECTION ====
                pdf.set_font("helvetica", "B", 12)
                pdf.set_fill_color(52, 152, 219)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 7, "CLIENT INFORMATION", ln=True, fill=True)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(1)
                
                client_info = [
                    ("Client Name", form_data.get('client_name', 'N/A')),
                    ("Client Type", form_data.get('client_type', 'N/A')),
                    ("Client Address", form_data.get('client_address', 'N/A')),
                    ("Client Phone", form_data.get('client_phone', 'N/A')),
                    ("Client Email", form_data.get('client_email', 'N/A')),
                    ("Signatory Name", form_data.get('client_sig_name', 'N/A')),
                    ("Signatory Designation", form_data.get('client_designation', 'N/A')),
                ]
                
                for label, value in client_info:
                    pdf.set_font("helvetica", "B", 10)
                    pdf.cell(55, 5, f"{label}:", ln=False)
                    pdf.set_font("helvetica", "", 10)
                    value_str = str(value)[:80]
                    pdf.cell(0, 5, value_str, ln=True)
                
                pdf.ln(2)
                
                # ==== SERVICE PROVIDER INFORMATION SECTION ====
                pdf.set_font("helvetica", "B", 12)
                pdf.set_fill_color(52, 152, 219)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 7, "SERVICE PROVIDER INFORMATION", ln=True, fill=True)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(1)
                
                company_addr = company_address.address if company_address else 'N/A'
                sp_info = [
                    ("Service Provider", "Phemedia Onguard Services Ltd"),
                    ("Address", company_addr[:60] if isinstance(company_addr, str) else str(company_addr)[:60]),
                    ("Email", "info@phemediaa.com"),
                    ("Telephone", "08099180391, 0803231746"),
                    ("Website", "www.phemediaa.com"),
                ]
                
                for label, value in sp_info:
                    pdf.set_font("helvetica", "B", 10)
                    pdf.cell(55, 5, f"{label}:", ln=False)
                    pdf.set_font("helvetica", "", 10)
                    pdf.cell(0, 5, str(value), ln=True)
                
                pdf.ln(2)
                
                # ==== TERMS & CONDITIONS ====
                pdf.set_font("helvetica", "B", 12)
                pdf.set_fill_color(52, 152, 219)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 7, "TERMS & CONDITIONS", ln=True, fill=True)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(1)
                
                # 1. Purpose
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(0, 5, "1. PURPOSE", ln=True)
                pdf.set_font("helvetica", "", 9)
                pdf.multi_cell(0, 4, "The Client engages the Service Provider to conduct background check and related verification services on individuals, employees, contractors, or other persons as requested by the Client, in accordance with the terms of this Agreement.")
                pdf.ln(1)
                
                # 2. Scope of Services
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(0, 5, "2. SCOPE OF SERVICES", ln=True)
                pdf.set_font("helvetica", "", 9)
                scope_text = "The Service Provider shall provide background check including, but not limited to:\n- Identity verification\n- Criminal record checks (subject to legal requirements)\n- Employment history verification\n- Academic qualification verification\n- Reference checks\n- Credit checks (where legally permitted)"
                pdf.multi_cell(0, 4, scope_text)
                pdf.ln(1)
                
                # 3. Client Responsibilities
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(0, 5, "3. CLIENT RESPONSIBILITIES", ln=True)
                pdf.set_font("helvetica", "", 9)
                resp_text = "The Client shall:\n- Provide accurate and complete information necessary for the Service Provider to carry out the checks\n- Obtain all necessary written consents from the subject(s) of the background check, as required by law\n- Use the information provided solely for lawful and legitimate purposes"
                pdf.multi_cell(0, 4, resp_text)
                pdf.ln(1)
                
                # 4. Confidentiality
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(0, 5, "4. CONFIDENTIALITY", ln=True)
                pdf.set_font("helvetica", "", 9)
                conf_text = "- All information obtained, processed, or provided under this Agreement shall remain strictly confidential\n- Neither Party shall disclose such information to any third party without prior written consent, except where required by law"
                pdf.multi_cell(0, 4, conf_text)
                pdf.ln(1)
                
                # 5. Data Protection Compliance
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(0, 5, "5. DATA PROTECTION COMPLIANCE", ln=True)
                pdf.set_font("helvetica", "", 9)
                dptext = "The Parties shall comply with the Nigeria Data Protection Regulation (NDPR) and any other applicable laws regarding personal data collection, storage, and processing."
                pdf.multi_cell(0, 4, dptext)
                pdf.ln(1)
                
                # 6. Reports & Limitations
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(0, 5, "6. REPORTS & LIMITATIONS", ln=True)
                pdf.set_font("helvetica", "", 9)
                rep_text = "- The Service Provider will provide factual reports based on information obtained from reliable sources, but does not guarantee the completeness or absolute accuracy of such information\n- The Service Provider shall not be liable for any loss, damage, or claim arising from reliance on the information provided, except in cases of proven negligence or willful misconduct"
                pdf.multi_cell(0, 4, rep_text)
                pdf.ln(1)
                
                # 7. Fees & Payment
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(0, 5, "7. FEES & PAYMENT", ln=True)
                pdf.set_font("helvetica", "", 9)
                pdf.multi_cell(0, 4, "The Client shall pay the Service Provider the agreed fee of NGN __________ per background check/report. Full Payment shall be made as agreed.")
                pdf.ln(1)
                fee_amount = form_data.get('check_amount', 'N/A')
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(65, 5, "Agreed Fee per Background Check:", ln=False)
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 5, f"NGN {fee_amount}", ln=True)
                pdf.ln(1)
                
                # 8. Term & Termination
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(0, 5, "8. TERM & TERMINATION", ln=True)
                pdf.set_font("helvetica", "", 9)
                notice_days = form_data.get('notice_period', 'N/A')
                pdf.multi_cell(0, 4, "- This Agreement shall commence on the date first written above and continue until terminated by either Party with the notice period (days) written below.\n- The Service Provider may terminate this Agreement immediately if the Client breaches any of its terms.")
                pdf.ln(1)
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(90, 5, "Notice Period Required for Termination (in days):", ln=False)
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 5, str(notice_days), ln=True)
                pdf.ln(1)
                
                # 9. Non-Solicitation
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(0, 5, "9. NON-SOLICITATION", ln=True)
                pdf.set_font("helvetica", "", 9)
                nons_text = "The Client shall not directly or indirectly hire, contract, or otherwise engage any employee or contractor of the Service Provider for a period of twelve (12) months after the completion of the services without prior written consent."
                pdf.multi_cell(0, 4, nons_text)
                pdf.ln(1)
                
                # 10. Governing Law
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(0, 5, "10. GOVERNING LAW & DISPUTE RESOLUTION", ln=True)
                pdf.set_font("helvetica", "", 9)
                gov_text = "This Agreement shall be governed by and construed in accordance with the laws of the Federal Republic of Nigeria. Disputes shall be resolved amicably, failing which they shall be referred to arbitration in accordance with the Arbitration and Conciliation Act."
                pdf.multi_cell(0, 4, gov_text)
                pdf.ln(1)
                
                # 11. Entire Agreement
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(0, 5, "11. ENTIRE AGREEMENT", ln=True)
                pdf.set_font("helvetica", "", 9)
                entire_text = "This Agreement constitutes the entire understanding between the Parties and supersedes all prior discussions, agreements, or understandings."
                pdf.multi_cell(0, 4, entire_text)
                pdf.ln(2)

                # Client acknowledgement checkbox
                entire_agreed = form_data.get('entire_agreement', '')
                agreed_symbol = "[YES]" if entire_agreed == 'yes' else "[ ]"
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(10, 5, agreed_symbol, ln=False)
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 5, "I have read and understand the entire agreement and agree to all terms and conditions", ln=True)
                pdf.ln(2)
                
                # ==== SIGNATURES SECTION ====
                pdf.set_font("helvetica", "B", 12)
                pdf.set_fill_color(52, 152, 219)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 7, "SIGNATURES", ln=True, fill=True)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(2)
                
                # Client Signature Section
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(0, 5, "FOR AND ON BEHALF OF THE CLIENT:", ln=True)
                pdf.set_font("helvetica", "", 10)
                
                client_sig_name = form_data.get('client_sig_name', 'N/A')
                client_designation = form_data.get('client_designation', 'N/A')
                pdf.cell(0, 5, f"Name: {client_sig_name}", ln=True)
                pdf.cell(0, 5, f"Designation: {client_designation}", ln=True)
                pdf.ln(1)
                
                # Client Signature Image
                add_signatures_to_pdf(pdf, form_data, submission_id, "Client Signature:")
                
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 5, f"Date: {form_data.get('client_agreement_date', 'N/A')}", ln=True)
                pdf.ln(3)
                
                # Service Provider Signature Section
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(0, 5, "FOR AND ON BEHALF OF PHEMEDIA ONGUARD SERVICES LTD:", ln=True)
                pdf.set_font("helvetica", "", 10)
                
                pdf.cell(0, 5, f"Authorized Officer: {approver_name or 'Company Representative'}", ln=True)
                pdf.cell(0, 5, f"Position: {approver_position or 'N/A'}", ln=True)
                pdf.ln(1)
                
                # Service Provider Signature Image
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(0, 5, "Official Approval Stamp & Signature:", ln=True)
                
                sig_start_y = pdf.get_y()
                sig_x = 20
                sig_w = 50
                sig_h = 25
                any_sig = False

                # Drawn signature (left)
                if stamp_drawn_path and os.path.exists(stamp_drawn_path):
                    try:
                        pdf.set_font("helvetica", "", 9)
                        pdf.text(sig_x, sig_start_y + sig_h + 4, "Drawn Signature:")
                        pdf.image(stamp_drawn_path, x=sig_x, y=sig_start_y, w=sig_w, h=sig_h)
                        any_sig = True
                    except Exception as e:
                        print(f"Error adding drawn admin signature: {str(e)}")

                # Uploaded stamp (right, or left if no drawn)
                if stamp_path and os.path.exists(stamp_path):
                    try:
                        upload_x = sig_x + sig_w + 15 if any_sig else sig_x
                        pdf.set_font("helvetica", "", 9)
                        pdf.text(upload_x, sig_start_y + sig_h + 4, "Uploaded Stamp/Signature:")
                        pdf.image(stamp_path, x=upload_x, y=sig_start_y, w=sig_w, h=sig_h)
                        any_sig = True
                    except Exception as e:
                        print(f"Error adding uploaded admin signature: {str(e)}")

                if any_sig:
                    pdf.ln(sig_h + 10)
                else:
                    pdf.ln(18)
                
                approval_date = submission.approved_at if submission.approved_at else datetime.now()
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 5, f"Date: {approval_date.strftime('%d %B %Y at %H:%M:%S')}", ln=True)
                pdf.ln(2)
                
                # Separator line
                pdf.set_draw_color(189, 195, 199)
                pdf.line(15, pdf.get_y(), 195, pdf.get_y())
                pdf.ln(3)
                
                # Footer with compliance notice
                pdf.set_font("helvetica", "", 8)
                pdf.set_text_color(100, 100, 100)
                footer_text = "This is an official certified Background Check Service Agreement approved by Phemedia Onguard Services Ltd. This document is confidential and should be retained for compliance and audit purposes."
                pdf.multi_cell(0, 4, footer_text, align="C")
                pdf.cell(0, 4, f"Generated: {datetime.now().strftime('%d %B %Y at %H:%M:%S')} | Ref: {pdf_filename}", ln=True, align="C")
                pdf.set_text_color(0, 0, 0)
                
                # Save PDF
                pdf.output(output_path)
                print(f"[generate_backgroundcheck_approval_pdf] PDF generated successfully at {output_path}")
                return pdf_filename
                
            except Exception as e:
                print(f"Error generating PDF with fpdf2: {str(e)}")
                import traceback
                traceback.print_exc()
                raise  # re-raise so caller receives the real error message
        else:
            print("fpdf2 not installed")
            return None
            
    except Exception as e:
        print(f"Error in generate_backgroundcheck_approval_pdf: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def sanitize_for_pdf(text):
    """Sanitize text for PDF output - remove Unicode characters not supported by helvetica font"""
    if not text:
        return 'N/A'
    
    text_str = str(text)
    # Replace common special characters with text equivalents
    replacements = {
        '₦': 'NGN ',  # Nigerian Naira
        '₨': 'Rs ',   # Indian Rupee
        '€': 'EUR ',  # Euro
        '£': 'GBP ',  # Pound
        '¥': 'CNY ',  # Yuan
        '$': 'USD ',  # Dollar
        '•': '*',     # Bullet point
        '–': '-',     # En dash
        '—': '-',     # Em dash
        ''': "'",     # Right single quotation mark
        ''': "'",     # Left single quotation mark
        '"': '"',     # Left double quotation mark
        '"': '"',     # Right double quotation mark
    }
    
    for char, replacement in replacements.items():
        text_str = text_str.replace(char, replacement)
    
    # Remove other non-ASCII characters
    text_str = text_str.encode('ascii', 'ignore').decode('ascii')
    
    return text_str if text_str.strip() else 'N/A'


def generate_clientengagement_approval_pdf(submission_id, stamp_path=None, stamp_drawn_path=None, approver_name=None, approver_email=None, approver_position=None):
    """
    Generate comprehensive PDF for client engagement form approval
    """
    print(f"[generate_clientengagement_approval_pdf] Called with submission_id={submission_id}")
    try:
        submission = FormSubmission.query.get(submission_id)
        if not submission or submission.form_type != 'clientengagement':
            print(f"[generate_clientengagement_approval_pdf] Invalid submission or form type")
            return None
        
        # Get form data
        form_data = submission.submitted_data
        company_address = CompanyAddress.query.filter_by(is_active=True).first()
        
        # Determine output path
        pdf_filename = f'clientengagement_approval_{submission_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        output_path = os.path.join(PDFS_FOLDER, pdf_filename)
        
        print(f"[generate_clientengagement_approval_pdf] HAS_PDF_SUPPORT={HAS_PDF_SUPPORT}")
        if HAS_PDF_SUPPORT:
            try:
                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.set_margins(15, 15, 15)
                pdf.add_page()

                # Add standard header with logo and title
                add_pdf_header(pdf, "CLIENT ENGAGEMENT FORM & AGREEMENT", "Approved & Certified Document")

                # ==== CLIENT INFORMATION SECTION ====
                pdf.set_font("helvetica", "B", 12)
                pdf.set_fill_color(52, 152, 219)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 7, "CLIENT INFORMATION", ln=True, fill=True)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(1)

                client_info = [
                    ("Client Name", sanitize_for_pdf(form_data.get('client_name'))),
                    ("Client Type", sanitize_for_pdf(form_data.get('client_type'))),
                    ("Client Address", sanitize_for_pdf(form_data.get('client_address'))),
                    ("Phone / WhatsApp", sanitize_for_pdf(form_data.get('client_phone'))),
                    ("Email", sanitize_for_pdf(form_data.get('client_email'))),
                ]

                for label, value in client_info:
                    pdf.set_font("helvetica", "B", 10)
                    pdf.cell(55, 5, f"{label}:", ln=False)
                    pdf.set_font("helvetica", "", 10)
                    pdf.cell(0, 5, str(value)[:80], ln=True)

                pdf.ln(2)

                # ==== SERVICE DETAILS SECTION ====
                pdf.set_font("helvetica", "B", 12)
                pdf.set_fill_color(52, 152, 219)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 7, "SERVICE DETAILS", ln=True, fill=True)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(1)

                service_details = [
                    ("Service Type", sanitize_for_pdf(form_data.get('service_type'))),
                    ("Number of Guards", sanitize_for_pdf(form_data.get('number_of_guards'))),
                    ("Deployment Location", sanitize_for_pdf(form_data.get('deployment_location'))),
                    ("Duration/Frequency", sanitize_for_pdf(form_data.get('deployment_type'))),
                    ("Start Date", sanitize_for_pdf(form_data.get('start_date'))),
                ]

                for label, value in service_details:
                    pdf.set_font("helvetica", "B", 10)
                    pdf.cell(55, 5, f"{label}:", ln=False)
                    pdf.set_font("helvetica", "", 10)
                    pdf.cell(0, 5, str(value), ln=True)

                # Estimated Deployment Timeline
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(55, 5, "Estimated Deployment Timeline:", ln=False)
                pdf.set_font("helvetica", "", 10)
                timeline_val = sanitize_for_pdf(form_data.get('estimated_timeline',
                    'Between 1 week to 4 weeks from receipt of non-administrative fee and completed formalities'))
                rem_w = pdf.w - pdf.r_margin - pdf.x
                pdf.multi_cell(rem_w, 5, str(timeline_val))
                pdf.set_x(pdf.l_margin)

                pdf.ln(2)

                # ==== FEES & PAYMENT TERMS SECTION ====
                pdf.set_font("helvetica", "B", 12)
                pdf.set_fill_color(52, 152, 219)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 7, "FEES & PAYMENT TERMS", ln=True, fill=True)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(1)

                non_admin_fee = sanitize_for_pdf(form_data.get('non_admin_fee', 'N/A'))
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(65, 5, "Non-Administrative Fee:", ln=False)
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 5, str(non_admin_fee), ln=True)
                pdf.ln(1)

                pdf.set_font("helvetica", "B", 10)
                pdf.cell(0, 5, "Payment Method:", ln=True)
                pdf.set_font("helvetica", "", 9)
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(pdf.epw, 4,
                    "Phemedia Onguard Services Ltd\n"
                    "Moniepoint Microfinance Bank Account: 6707932476\n"
                    "OR\n"
                    "Providus Bank Account: 1306872171")
                pdf.set_x(pdf.l_margin)
                pdf.ln(2)

                # ==== TERMS & CONDITIONS ====
                pdf.set_font("helvetica", "B", 12)
                pdf.set_fill_color(52, 152, 219)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 7, "TERMS & CONDITIONS", ln=True, fill=True)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(1)

                terms_lines = [
                    "- Deployment shall commence within 1-4 weeks after payment of the non-administrative fee.",
                    "- If the client needs more than five guards, the non-administrative fee will increase.",
                    "- Signing of this form and completion of any required site assessment or documentation are necessary.",
                    "- All guards, armed officers, bouncers, and spy police officers are trained and qualified.",
                    "- Client agrees to provide safe working conditions and report any issues promptly.",
                    "- Any changes to requirements may affect the timeline or fees.",
                    "- This agreement is governed by Nigerian law.",
                ]
                pdf.set_font("helvetica", "", 9)
                for line in terms_lines:
                    pdf.set_x(pdf.l_margin)
                    pdf.multi_cell(pdf.epw, 4, line)
                pdf.ln(2)

                # ==== CLIENT ACKNOWLEDGMENT ====
                pdf.set_font("helvetica", "B", 12)
                pdf.set_fill_color(52, 152, 219)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 7, "CLIENT ACKNOWLEDGMENT", ln=True, fill=True)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(1)

                acknowledged = form_data.get('acknowledgment', '')
                ack_symbol = "[YES]" if acknowledged == 'yes' else "[ ]"
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(13, 5, ack_symbol, ln=False)
                pdf.set_font("helvetica", "", 10)
                rem_ack = pdf.w - pdf.r_margin - pdf.x
                pdf.multi_cell(rem_ack, 5,
                    "I/We have read and agree to the terms above, including payment of the non-administrative "
                    "fee prior to guard, bouncer, spy police officer, and armed officer deployment.")
                pdf.set_x(pdf.l_margin)
                pdf.ln(2)

                # ==== SIGNATURES SECTION ====
                pdf.set_font("helvetica", "B", 12)
                pdf.set_fill_color(52, 152, 219)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 7, "SIGNATURES", ln=True, fill=True)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(2)

                # Client Signature
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(0, 5, "FOR AND ON BEHALF OF THE CLIENT:", ln=True)
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 5, f"Client Name: {sanitize_for_pdf(form_data.get('client_name'))}", ln=True)
                pdf.ln(1)

                add_signatures_to_pdf(pdf, form_data, submission_id, "Client Signature:")

                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 5, f"Date: {sanitize_for_pdf(form_data.get('signature_date'))}", ln=True)
                pdf.ln(3)

                # Service Provider Signature
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(0, 5, "FOR AND ON BEHALF OF PHEMEDIA ONGUARD SERVICES LTD:", ln=True)
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 5, f"Authorized Officer: {approver_name or 'Company Representative'}", ln=True)
                pdf.cell(0, 5, f"Position: {approver_position or 'N/A'}", ln=True)
                pdf.ln(1)

                pdf.set_font("helvetica", "B", 10)
                pdf.cell(0, 5, "Official Approval Stamp & Signature:", ln=True)

                sig_start_y = pdf.get_y()
                sig_x = 20
                sig_w = 50
                sig_h = 25
                any_sig = False

                # Drawn signature (left)
                if stamp_drawn_path and os.path.exists(stamp_drawn_path):
                    try:
                        pdf.set_font("helvetica", "", 9)
                        pdf.text(sig_x, sig_start_y + sig_h + 4, "Drawn Signature:")
                        pdf.image(stamp_drawn_path, x=sig_x, y=sig_start_y, w=sig_w, h=sig_h)
                        any_sig = True
                    except Exception as e:
                        print(f"Error adding drawn admin signature: {str(e)}")

                # Uploaded stamp (right, or left if no drawn)
                if stamp_path and os.path.exists(stamp_path):
                    try:
                        upload_x = sig_x + sig_w + 15 if any_sig else sig_x
                        pdf.set_font("helvetica", "", 9)
                        pdf.text(upload_x, sig_start_y + sig_h + 4, "Uploaded Stamp/Signature:")
                        pdf.image(stamp_path, x=upload_x, y=sig_start_y, w=sig_w, h=sig_h)
                        any_sig = True
                    except Exception as e:
                        print(f"Error adding uploaded admin signature: {str(e)}")

                if any_sig:
                    pdf.ln(sig_h + 10)
                else:
                    pdf.ln(18)

                approval_date = submission.approved_at if submission.approved_at else datetime.now()
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 5, f"Date: {approval_date.strftime('%d %B %Y at %H:%M:%S')}", ln=True)
                pdf.ln(2)

                # Separator line
                pdf.set_draw_color(189, 195, 199)
                pdf.line(15, pdf.get_y(), 195, pdf.get_y())
                pdf.ln(3)

                # Footer
                pdf.set_font("helvetica", "", 8)
                pdf.set_text_color(100, 100, 100)
                footer_text = ("This is an official certified Client Engagement Agreement approved by "
                               "Phemedia Onguard Services Ltd. This document is confidential and should "
                               "be retained for compliance and record purposes.")
                pdf.multi_cell(0, 4, footer_text, align="C")
                pdf.cell(0, 4, f"Generated: {datetime.now().strftime('%d %B %Y at %H:%M:%S')} | Ref: {pdf_filename}", ln=True, align="C")
                pdf.set_text_color(0, 0, 0)

                # Save PDF
                pdf.output(output_path)
                print(f"[generate_clientengagement_approval_pdf] PDF generated successfully at {output_path}")
                return pdf_filename

            except Exception as e:
                print(f"Error generating PDF with fpdf2: {str(e)}")
                import traceback
                traceback.print_exc()
                raise
        else:
            raise RuntimeError("fpdf2 not installed")
            
    except Exception as e:
        print(f"Error in generate_clientengagement_approval_pdf: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


def process_form_submission(form_type, form_data):
    """Process form submission and send emails"""
    if form_type not in FORM_TYPES:
        return {'success': False, 'message': 'Invalid form type.'}
    
    # Sanitize all inputs
    sanitized_data = {}
    for key, value in form_data.items():
        if isinstance(value, list):
            sanitized_data[key] = [sanitize_input(v) for v in value]
        else:
            sanitized_data[key] = sanitize_input(value)
    
    # Validate email if present (handle different field names for different forms)
    if form_type in ['serviceagreement', 'trackingagreement', 'oilgasservicerequest', 'clientengagement', 'backgroundcheck']:
        # Try client_email first, then email as fallback
        user_email = sanitized_data.get('client_email', '') or sanitized_data.get('email', '')
    elif form_type == 'declarationbyemployee':
        # Employee declaration uses employee_email
        user_email = sanitized_data.get('employee_email', '')
    elif form_type == 'guarantorundertaking':
        # Guarantor undertaking uses guarantor_email
        user_email = sanitized_data.get('guarantor_email', '')
    else:
        user_email = sanitized_data.get('email', '')
    
    if user_email and not validate_email(user_email):
        return {'success': False, 'message': 'Please provide a valid email address.'}
    
    # Special handling for Service Agreement - Two-part workflow (Admin fills, then client signs)
    if form_type == 'serviceagreement':
        try:
            # Check if this is client submission (has agreement_token) or admin submission
            agreement_token = form_data.get('agreement_token')
            # Handle case where agreement_token might be a list
            if isinstance(agreement_token, list):
                agreement_token = agreement_token[0] if agreement_token else None
            
            if agreement_token:
                # This is CLIENT SUBMISSION - finding the admin's submission and adding client signature
                admin_submission = FormSubmission.query.filter_by(
                    client_acceptance_token=agreement_token,
                    form_type='serviceagreement'
                ).first()
                
                if not admin_submission:
                    return {'success': False, 'message': 'Invalid or expired agreement link.'}
                
                if admin_submission.client_acceptance_completed:
                    return {'success': False, 'message': 'This agreement has already been signed by the client.'}
                
                # Merge client data with admin's data
                merged_data = admin_submission.submitted_data.copy()
                # Add client signature and client-only fields
                merged_data['client_sig_name'] = sanitized_data.get('client_sig_name')
                merged_data['client_designation'] = sanitized_data.get('client_designation')
                merged_data['client_agreement_date'] = sanitized_data.get('client_agreement_date')
                merged_data['clientSignatureData'] = sanitized_data.get('clientSignatureData')
                # Map base signature to _drawn/_uploaded so add_signatures_to_pdf can render it
                merged_data['clientSignatureData_drawn'] = sanitized_data.get('clientSignatureData_drawn') or sanitized_data.get('clientSignatureData')
                merged_data['clientSignatureData_uploaded'] = sanitized_data.get('clientSignatureData_uploaded')
                
                # Update the submission
                admin_submission.submitted_data = merged_data
                admin_submission.client_acceptance_completed = True
                admin_submission.client_acceptance_completed_at = datetime.utcnow()
                admin_submission.client_signature_data = sanitized_data.get('clientSignatureData')
                admin_submission.status = 'submitted'  # Mark as complete and ready for processing
                db.session.commit()
                
                # Generate final PDF with backgroundcheck-style design (pending approval)
                sa_pdf_filename = f'service_agreement_{admin_submission.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
                sa_pdf_filepath = os.path.join(app.config['PDFS_FOLDER'], sa_pdf_filename)
                pdf_path = generate_service_agreement_pdf(
                    admin_submission.id,
                    stamp_path=None,
                    stamp_drawn_path=None,
                    output_path=sa_pdf_filepath
                )
                final_pdf_filename = None
                if pdf_path and os.path.exists(pdf_path):
                    final_pdf_filename = os.path.basename(pdf_path)
                    admin_submission.pdf_filename = final_pdf_filename
                    admin_submission.final_pdf_filename = final_pdf_filename
                    db.session.commit()
                
                # Send final confirmation email with PDF
                confirmation_html = """<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: 'Poppins', 'Segoe UI', sans-serif; line-height: 1.6; color: #333; }
        .header { background-color: #27ae60; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; }
        .footer { background-color: #f5f5f5; padding: 15px; text-align: center; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class='header'>
        <h2>✓ Your Service Agreement is Fully Signed</h2>
    </div>
    <div class='content'>
        <p>Dear Valued Client,</p>
        <p>Thank you for signing the Service Agreement. Both the Company and Client sections have been completed and executed.</p>
        <p><strong>Status: ✅ FULLY SIGNED AND BINDING</strong></p>
        <p>Please find the final signed and executed agreement attached to this email. Keep this for your records.</p>
        <p>If you have any questions, please contact us at info@phemediaa.com or call 08099180391.</p>
        <p>Best regards,<br>Phemedia Onguard Services Ltd</p>
    </div>
    <div class='footer'>
        <p>&copy; 2026 Phemedia Onguard Services Ltd. All rights reserved.</p>
    </div>
</body>
</html>"""
                
                if user_email:
                    if pdf_path and os.path.exists(pdf_path):
                        send_email_with_attachment(user_email, 'Your Fully Signed Service Agreement', confirmation_html, pdf_path, final_pdf_filename)
                    else:
                        send_email(user_email, 'Service Agreement Signed Successfully', confirmation_html)
                
                # Notify admin that agreement is complete
                admin_notification_html = f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Poppins', sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background-color: #27ae60; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .footer {{ background-color: #f5f5f5; padding: 15px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class='header'>
        <h2>Service Agreement Fully Signed</h2>
    </div>
    <div class='content'>
        <p>A Service Agreement (ID: {admin_submission.id}) has been fully signed by both parties and is ready for approval.</p>
        <p><strong>Client:</strong> {merged_data.get('client_name', 'N/A')}</p>
        <p><strong>Client Email:</strong> {user_email}</p>
        <p>Please review and approve this agreement in your admin dashboard.</p>
    </div>
    <div class='footer'>
        <p>&copy; 2026 Phemedia Onguard Services Ltd</p>
    </div>
</body>
</html>"""
                
                notification_emails = NotificationEmail.query.filter(
                    (NotificationEmail.form_type == 'serviceagreement') | (NotificationEmail.form_type == 'all'),
                    NotificationEmail.is_active == True
                ).all()
                
                if not notification_emails:
                    notification_emails = [type('', (), {'email': ADMIN_EMAIL})]
                
                for notif in notification_emails:
                    send_email(notif.email, f'Service Agreement Fully Signed - Ready for Approval (#{admin_submission.id})', admin_notification_html)
                
                return {
                    'success': True,
                    'message': 'Service Agreement signed successfully. Thank you for completing the process.',
                    'submission_id': admin_submission.id,
                    'form_type': form_type
                }
            
            else:
                # This is ADMIN SUBMISSION - Generate client link and token
                token = str(uuid.uuid4())
                client_link = f"{request.host_url.rstrip('/')}/serviceagreement/sign/{token}"
                
                # Create submission with token
                submission = FormSubmission(
                    form_type=form_type,
                    submitted_data=sanitized_data,
                    user_email=user_email,
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent', 'Unknown'),
                    status='submitted',
                    client_acceptance_token=token,
                    client_acceptance_link=client_link
                )
                db.session.add(submission)
                db.session.commit()
                
                # Send client link email
                if user_email:
                    client_email_html = f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Poppins', 'Segoe UI', sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background-color: #3498db; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .link-box {{ background: #e8f4f8; padding: 20px; border-radius: 6px; margin: 20px 0; text-align: center; }}
        .btn-link {{ display: inline-block; background: #3498db; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; }}
        .footer {{ background-color: #f5f5f5; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class='header'>
        <h2>Action Required: Sign Your Service Agreement</h2>
    </div>
    <div class='content'>
        <p>Dear Valued Client,</p>
        <p>A Service Agreement has been prepared for you by Phemedia Onguard Services Ltd. We need your signature to complete the process.</p>
        <p><strong>What to do:</strong></p>
        <ol>
            <li>Click the button below to review the agreement</li>
            <li>Fill in your information in the Client section</li>
            <li>Sign the agreement (by drawing or uploading your signature)</li>
            <li>Submit to complete the process</li>
        </ol>
        <div class='link-box'>
            <a href='{client_link}' class='btn-link'>Sign Service Agreement</a>
            <p style='margin-top: 15px; color: #666; font-size: 12px;'>Or copy and paste this link in your browser:<br>{client_link}</p>
        </div>
        <p>This link is unique to you and will expire after the agreement is signed. If you have any questions, please contact us.</p>
        <p>Best regards,<br>Phemedia Onguard Services Ltd Team</p>
    </div>
    <div class='footer'>
        <p>&copy; 2026 Phemedia Onguard Services Ltd. All rights reserved.</p>
        <p>Contact: info@phemediaa.com | Phone: +234 803 231 7546</p>
    </div>
</body>
</html>"""
                    send_email(user_email, 'Action Required: Sign Your Service Agreement', client_email_html)
                
                # Send admin confirmation
                admin_conf_html = """<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: 'Poppins', sans-serif; line-height: 1.6; color: #333; }
        .header { background-color: #3498db; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; }
        .footer { background-color: #f5f5f5; padding: 15px; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class='header'>
        <h2>Service Agreement Sent for Client Signature</h2>
    </div>
    <div class='content'>
        <p>Your Service Agreement has been prepared and a signing link has been sent to the client.</p>
        <p><strong>Client Email:</strong> """ + user_email + """</p>
        <p>Once the client signs, you will receive a notification to approve the agreement.</p>
    </div>
    <div class='footer'>
        <p>&copy; 2026 Phemedia Onguard Services Ltd</p>
    </div>
</body>
</html>"""
                
                notification_emails = NotificationEmail.query.filter(
                    (NotificationEmail.form_type == 'serviceagreement') | (NotificationEmail.form_type == 'all'),
                    NotificationEmail.is_active == True
                ).all()
                
                if not notification_emails:
                    notification_emails = [type('', (), {'email': ADMIN_EMAIL})]
                
                for notif in notification_emails:
                    send_email(notif.email, f'Service Agreement Sent to Client - Awaiting Signature (#{submission.id})', admin_conf_html)
                
                return {
                    'success': True,
                    'message': 'Service Agreement prepared successfully. A signing link has been sent to the client.',
                    'submission_id': submission.id,
                    'form_type': form_type
                }
        except Exception as e:
            error_msg = f"Error processing service agreement: {str(e)}"
            print(error_msg, flush=True)
            import traceback
            error_trace = traceback.format_exc()
            print(error_trace, flush=True)
            with open('form_submission_errors.log', 'a') as f:
                f.write(f"\n{'='*80}\n{datetime.now()}\n{error_msg}\n{error_trace}\n")
            db.session.rollback()
            return {'success': False, 'message': 'An error occurred while processing the agreement. Please try again.'}
    
    # Special handling for Tracking Agreement - generate client acceptance link
    if form_type == 'trackingagreement':
        try:
            # Generate unique token for client acceptance
            token = str(uuid.uuid4())
            acceptance_link = f"{request.host_url}client-acceptance/{token}"
            
            # Create submission
            submission = FormSubmission(
                form_type=form_type,
                submitted_data=sanitized_data,
                user_email=user_email,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', 'Unknown'),
                status='submitted',
                client_acceptance_token=token,
                client_acceptance_link=acceptance_link
            )
            db.session.add(submission)
            db.session.commit()
            
            # Send client acceptance link email
            if user_email:
                send_client_acceptance_email(submission, user_email, acceptance_link)
            
            return {
                'success': True,
                'message': 'Tracking Agreement submitted successfully. A link for digital signature has been sent to the client email.',
                'submission_id': submission.id,
                'form_type': form_type
            }
        except Exception as e:
            print(f"Error processing tracking agreement: {str(e)}")
            db.session.rollback()
            return {'success': False, 'message': 'An error occurred while processing your agreement. Please try again.'}

    # Special handling for Oil & Gas Service Request - Two-part workflow (Admin fills, then client signs)
    if form_type == 'oilgasservicerequest':
        try:
            # Check if this is client submission (has request_token) or admin submission
            request_token = form_data.get('request_token')
            # Handle case where request_token might be a list
            if isinstance(request_token, list):
                request_token = request_token[0] if request_token else None
            
            if request_token:
                # This is CLIENT SUBMISSION - finding the admin's submission and adding client signature
                admin_submission = FormSubmission.query.filter_by(
                    client_acceptance_token=request_token,
                    form_type='oilgasservicerequest'
                ).first()
                
                if not admin_submission:
                    return {'success': False, 'message': 'Invalid or expired request link.'}
                
                if admin_submission.client_acceptance_completed:
                    return {'success': False, 'message': 'This service request has already been signed by the client.'}
                
                # Merge client data with admin's data
                merged_data = admin_submission.submitted_data.copy()
                # Admin signature is already stored under adminSignatureData_* keys (set during admin submit)
                # Just add client's fields from the signing form
                merged_data['client_signatory_name'] = sanitized_data.get('signatory_name', '')
                merged_data['client_signatory_position'] = sanitized_data.get('signatory_position', '')
                merged_data['client_signature_date'] = sanitized_data.get('signature_date', '')
                merged_data['clientSignatureData'] = sanitized_data.get('clientSignatureData', '')
                merged_data['clientSignatureData_drawn'] = sanitized_data.get('clientSignatureData_drawn') or sanitized_data.get('clientSignatureData', '')
                merged_data['clientSignatureData_uploaded'] = sanitized_data.get('clientSignatureData_uploaded', '')
                
                # Update the submission
                admin_submission.submitted_data = merged_data
                admin_submission.client_acceptance_completed = True
                admin_submission.client_acceptance_completed_at = datetime.utcnow()
                admin_submission.client_signature_data = sanitized_data.get('client_signature_data')
                admin_submission.status = 'submitted'  # Mark as complete and ready for processing
                db.session.commit()

                # Generate initial PDF (no approval stamp yet)
                initial_pdf_filename = generate_oilgasservicerequest_approval_pdf(admin_submission.id)
                if initial_pdf_filename:
                    admin_submission.pdf_filename = initial_pdf_filename
                    admin_submission.final_pdf_filename = initial_pdf_filename
                    db.session.commit()
                
                # Send final confirmation email
                confirmation_html = """<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: 'Poppins', 'Segoe UI', sans-serif; line-height: 1.6; color: #333; }
        .header { background-color: #27ae60; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; }
        .footer { background-color: #f5f5f5; padding: 15px; text-align: center; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class='header'>
        <h2>Service Request Signed Successfully</h2>
    </div>
    <div class='content'>
        <p>Dear Valued Client,</p>
        <p>Thank you for signing the Oil & Gas Sector Service Request. Both the Company and Client sections have been completed.</p>
        <p><strong>Status: ✅ SIGNED AND READY FOR PROCESSING</strong></p>
        <p>Our team will now process your completed request. You will receive the final PDF copy with all signatures and approval stamp via email within 1-2 business days.</p>
        <p>Best regards,<br>Phemedia Onguard Services Ltd</p>
    </div>
    <div class='footer'>
        <p>&copy; 2026 Phemedia Onguard Services Ltd. All rights reserved.</p>
    </div>
</body>
</html>"""
                if user_email:
                    send_email(user_email, 'Oil & Gas Service Request Signed Successfully', confirmation_html)
                
                # Notify admin that request is complete
                admin_notification_html = f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Poppins', sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background-color: #27ae60; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .footer {{ background-color: #f5f5f5; padding: 15px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class='header'>
        <h2>Oil & Gas Service Request Fully Signed</h2>
    </div>
    <div class='content'>
        <p>An Oil & Gas Sector Service Request (ID: {admin_submission.id}) has been fully signed by both parties and is ready for approval.</p>
        <p><strong>Client:</strong> {merged_data.get('client_name', 'N/A')}</p>
        <p><strong>Client Email:</strong> {user_email}</p>
        <p>Please review and approve this request in your admin dashboard.</p>
    </div>
    <div class='footer'>
        <p>&copy; 2026 Phemedia Onguard Services Ltd</p>
    </div>
</body>
</html>"""
                
                notification_emails = NotificationEmail.query.filter(
                    (NotificationEmail.form_type == 'oilgasservicerequest') | (NotificationEmail.form_type == 'all'),
                    NotificationEmail.is_active == True
                ).all()
                
                if not notification_emails:
                    notification_emails = [type('', (), {'email': ADMIN_EMAIL})]
                
                for notif in notification_emails:
                    send_email(notif.email, f'Oil & Gas Service Request Fully Signed - Ready for Approval (#{admin_submission.id})', admin_notification_html)
                
                return {
                    'success': True,
                    'message': 'Oil & Gas Service Request signed successfully. Thank you for completing the process.',
                    'submission_id': admin_submission.id,
                    'form_type': form_type
                }
            
            else:
                # This is ADMIN SUBMISSION - Generate client link and token
                token = str(uuid.uuid4())
                client_link = f"{request.host_url.rstrip('/')}/oilgasservicerequest/sign/{token}"
                
                # Create submission with token
                submission = FormSubmission(
                    form_type=form_type,
                    submitted_data=sanitized_data,
                    user_email=user_email,
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent', 'Unknown'),
                    status='submitted',
                    client_acceptance_token=token,
                    client_acceptance_link=client_link
                )
                db.session.add(submission)
                db.session.commit()
                
                # Send client link email
                if user_email:
                    client_email_html = f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Poppins', 'Segoe UI', sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background-color: #3498db; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .link-box {{ background: #e8f4f8; padding: 20px; border-radius: 6px; margin: 20px 0; text-align: center; }}
        .btn-link {{ display: inline-block; background: #3498db; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; }}
        .footer {{ background-color: #f5f5f5; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class='header'>
        <h2>Action Required: Sign Your Oil & Gas Service Request</h2>
    </div>
    <div class='content'>
        <p>Dear Valued Client,</p>
        <p>An Oil & Gas Sector Service Request has been prepared for you by Phemedia Onguard Services Ltd. We need your signature to complete the process.</p>
        <p><strong>What to do:</strong></p>
        <ol>
            <li>Click the button below to review the request</li>
            <li>Fill in your information in the Client section</li>
            <li>Sign the request (by drawing or uploading your signature)</li>
            <li>Submit to complete the process</li>
        </ol>
        <div class='link-box'>
            <a href='{client_link}' class='btn-link'>Sign Service Request</a>
            <p style='margin-top: 15px; color: #666; font-size: 12px;'>Or copy and paste this link in your browser:<br>{client_link}</p>
        </div>
        <p>This link is unique to you and will expire after the request is signed. If you have any questions, please contact us.</p>
        <p>Best regards,<br>Phemedia Onguard Services Ltd Team</p>
    </div>
    <div class='footer'>
        <p>&copy; 2026 Phemedia Onguard Services Ltd. All rights reserved.</p>
        <p>Contact: info@phemediaa.com | Phone: +234 803 231 7546</p>
    </div>
</body>
</html>"""
                    send_email(user_email, 'Action Required: Sign Your Oil & Gas Service Request', client_email_html)
                
                # Send admin confirmation
                admin_conf_html = """<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: 'Poppins', sans-serif; line-height: 1.6; color: #333; }
        .header { background-color: #3498db; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; }
        .footer { background-color: #f5f5f5; padding: 15px; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class='header'>
        <h2>Oil & Gas Service Request Sent to Client</h2>
    </div>
    <div class='content'>
        <p>You have successfully submitted an Oil & Gas Sector Service Request (ID: {submission.id}) and a signing link has been sent to the client.</p>
        <p><strong>Client Email:</strong> {user_email}</p>
        <p>The client will complete their section and sign the request.</p>
    </div>
    <div class='footer'>
        <p>&copy; 2026 Phemedia Onguard Services Ltd</p>
    </div>
</body>
</html>"""
                
                notification_emails = NotificationEmail.query.filter(
                    (NotificationEmail.form_type == 'oilgasservicerequest') | (NotificationEmail.form_type == 'all'),
                    NotificationEmail.is_active == True
                ).all()
                
                if not notification_emails:
                    notification_emails = [type('', (), {'email': ADMIN_EMAIL})]
                
                for notif in notification_emails:
                    send_email(notif.email, f'Oil & Gas Service Request Sent to Client for Signature (#{submission.id})', admin_conf_html)
                
                return {
                    'success': True,
                    'message': 'Oil & Gas Service Request submitted successfully. A signing link has been sent to the client email.',
                    'submission_id': submission.id,
                    'form_type': form_type
                }
        except Exception as e:
            error_msg = f"Error processing Oil & Gas Service Request: {str(e)}"
            print(error_msg, flush=True)
            import traceback
            error_trace = traceback.format_exc()
            print(error_trace, flush=True)
            with open('form_submission_errors.log', 'a') as f:
                f.write(f"\n{'='*80}\n{datetime.now()}\n{error_msg}\n{error_trace}\n")
            db.session.rollback()
            return {'success': False, 'message': 'An error occurred while processing the request. Please try again.'}
    
    
    # Special handling for Service Agreement, Background Check, Client Engagement, Employee Declaration, and Guarantor Undertaking - requires approval
    if form_type in ['backgroundcheck', 'clientengagement', 'declarationbyemployee', 'guarantorundertaking']:
        try:
            # Define form_name based on form type
            if form_type == 'serviceagreement':
                form_name = 'Service Agreement'
            elif form_type == 'backgroundcheck':
                form_name = 'Background Check Service Agreement'
            elif form_type == 'clientengagement':
                form_name = 'Client Engagement Form'
            elif form_type == 'oilgasservicerequest':
                form_name = 'Oil & Gas Sector Service Request'
            elif form_type == 'guarantorundertaking':
                form_name = "Guarantor's Undertaking"
            else:
                form_name = 'Employee Declaration & Undertaking'
            
            # Create submission with pending approval status
            submission = FormSubmission(
                form_type=form_type,
                submitted_data=sanitized_data,
                user_email=user_email,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', 'Unknown'),
                status='pending_approval',  # Service agreements and background check require approval
                photo_filename=sanitized_data.get('employee_photograph') if form_type == 'declarationbyemployee' else None,
                nin_filename=sanitized_data.get('employee_nin') if form_type == 'declarationbyemployee' else None
            )
            db.session.add(submission)
            db.session.commit()
            
            # Send confirmation to client
            if user_email:
                confirmation_html = f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Poppins', 'Segoe UI', sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background-color: #f39c12; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .footer {{ background-color: #f5f5f5; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class='header'>
        <h2>{form_name} Received</h2>
    </div>
    <div class='content'>
        <p>Dear Valued Client,</p>
        <p>Thank you for submitting your {form_name} on <strong>{datetime.now().strftime('%d %B %Y at %H:%M:%S')}</strong>.</p>
        <p><strong>Status: ⏳ PENDING APPROVAL</strong></p>
        <p>Your agreement has been received and is currently under review by our team. A PDF copy of your agreement will be sent to this email once it has been approved and stamped with our official seal.</p>
        <p>We typically process agreements within 1-2 business days. If we need any additional information, we will contact you.</p>
        <p>Best regards,<br>{COMPANY_NAME} Team</p>
    </div>
    <div class='footer'>
        <p>&copy; 2026 {COMPANY_NAME}. All rights reserved.</p>
    </div>
</body>
</html>"""
                send_email(user_email, f'{form_name} Received - Pending Approval', confirmation_html)
            
            # Notify admin about pending approval
            admin_email_html = generate_admin_email(form_type, sanitized_data)
            notification_emails = NotificationEmail.query.filter(
                (NotificationEmail.form_type == form_type) | (NotificationEmail.form_type == 'all'),
                NotificationEmail.is_active == True
            ).all()
            
            if not notification_emails:
                notification_emails = [type('', (), {'email': ADMIN_EMAIL})]
            
            for notif in notification_emails:
                send_email(notif.email, f'{form_name} Pending Approval (Submission #{submission.id})', admin_email_html)
            
            return {
                'success': True,
                'message': f'Your {form_name} has been submitted successfully and is pending approval. You will receive a PDF copy via email once it has been approved.',
                'submission_id': submission.id,
                'form_type': form_type
            }
        except Exception as e:
            error_msg = f"Error processing form: {str(e)}"
            print(error_msg, flush=True)
            import traceback
            error_trace = traceback.format_exc()
            print(error_trace, flush=True)
            # Also write to file for debugging
            with open('form_submission_errors.log', 'a') as f:
                f.write(f"\n{'='*80}\n{datetime.now()}\n{error_msg}\n{error_trace}\n")
            db.session.rollback()
            return {'success': False, 'message': 'An error occurred while processing your agreement. Please try again.'}
    
    # Standard processing for other forms
    admin_email_html = generate_admin_email(form_type, sanitized_data)
    form_title = FORM_TYPES[form_type]['title']
    admin_subject = f"PHEMEDAA - {form_title} Submission - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # Send to all active notification emails for this form type
    notification_emails = NotificationEmail.query.filter(
        (NotificationEmail.form_type == form_type) | (NotificationEmail.form_type == 'all'),
        NotificationEmail.is_active == True
    ).all()
    
    if not notification_emails:
        # Fall back to admin email if no notification emails configured
        notification_emails = [type('', (), {'email': ADMIN_EMAIL})]
    
    admin_sent = False
    for notif in notification_emails:
        if send_email(notif.email, admin_subject, admin_email_html):
            admin_sent = True
    
    # Send user confirmation if email provided
    user_sent = True
    if user_email:
        user_email_html = generate_user_email(form_type)
        user_subject = f"Form Submission Confirmation - {form_title}"
        user_sent = send_email(user_email, user_subject, user_email_html)
    
    # Store in database
    db_saved_successfully = False
    try:
        submission = FormSubmission(
            form_type=form_type,
            submitted_data=sanitized_data,
            user_email=user_email,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', 'Unknown'),
            status='submitted'  # Default status for other forms
        )
        db.session.add(submission)
        db.session.commit()
        db_saved_successfully = True
    except Exception as e:
        print(f"Error storing submission: {str(e)}")
        db.session.rollback()
    
    # Return success if the form was saved to the database, regardless of email status
    # Email sending is a secondary notification task
    if db_saved_successfully:
        return {
            'success': True,
            'message': 'Your form has been submitted successfully.'
        }
    else:
        return {
            'success': False,
            'message': 'There was an error submitting your form. Please try again later.'
        }


@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html', 
                         form_types=FORM_TYPES,
                         company_name=COMPANY_NAME,
                         support_email=SUPPORT_EMAIL,
                         support_phone=SUPPORT_PHONE)


@app.route('/confirmation')
def confirmation():
    """Form submission confirmation page"""
    return render_template('confirmation.html',
                         company_name=COMPANY_NAME,
                         support_email=SUPPORT_EMAIL,
                         support_phone=SUPPORT_PHONE)


@app.route('/backgroundcheck')
def backgroundcheck_form():
    """Background Check Form"""
    return render_template('backgroundcheck.html',
                         company_name=COMPANY_NAME,
                         support_email=SUPPORT_EMAIL,
                         support_phone=SUPPORT_PHONE)


@app.route('/declarationbyemployee')
def declarationbyemployee_form():
    """Declaration by Employee Form"""
    return render_template('declarationbyemployee.html',
                         company_name=COMPANY_NAME,
                         support_email=SUPPORT_EMAIL,
                         support_phone=SUPPORT_PHONE)


@app.route('/clientengagement')
def clientengagement_form():
    """Client Engagement Form & Agreement"""
    return render_template('clientengagement.html',
                         company_name=COMPANY_NAME,
                         support_email=SUPPORT_EMAIL,
                         support_phone=SUPPORT_PHONE)


@app.route('/guarantorundertaking')
def guarantorundertaking_form():
    """Guarantor Undertaking Form"""
    return render_template('guarantorundertaking.html',
                         company_name=COMPANY_NAME,
                         support_email=SUPPORT_EMAIL,
                         support_phone=SUPPORT_PHONE)


@app.route('/serviceagreement')
@require_admin_or_superadmin
def serviceagreement_form():
    """Service Agreement Form - Admin Only"""
    company_address = CompanyAddress.query.filter_by(is_active=True).first()
    return render_template('serviceagreement.html',
                         company_name=COMPANY_NAME,
                         support_email=SUPPORT_EMAIL,
                         support_phone=SUPPORT_PHONE,
                         company_address=company_address.address if company_address else '',
                         is_admin_form=True)


@app.route('/serviceagreement/sign/<token>')
def serviceagreement_client_sign(token):
    """Client Signature for Service Agreement"""
    # Find the submission with this token
    submission = FormSubmission.query.filter_by(client_acceptance_token=token, form_type='serviceagreement').first()
    if not submission or submission.client_acceptance_completed:
        return render_template('error.html', message='Invalid or expired link. This agreement has already been signed or does not exist.'), 404
    
    company_address = CompanyAddress.query.filter_by(is_active=True).first()
    # Decode the submitted data to pass to template
    agreement_data = submission.submitted_data if submission.submitted_data else {}
    
    return render_template('serviceagreement.html',
                         company_name=COMPANY_NAME,
                         support_email=SUPPORT_EMAIL,
                         support_phone=SUPPORT_PHONE,
                         company_address=company_address.address if company_address else '',
                         is_admin_form=False,
                         agreement_token=token,
                         agreement_data=agreement_data)


@app.route('/trackingagreement')
def trackingagreement_form():
    """Tracking Agreement Form"""
    return render_template('trackingagreement.html',
                         company_name=COMPANY_NAME,
                         support_email=SUPPORT_EMAIL,
                         support_phone=SUPPORT_PHONE)


@app.route('/oilgasservicerequest')
@require_admin_or_superadmin
def oilgasservicerequest_form():
    """Oil & Gas Sector Service Request Form - Admin Only"""
    company_address = CompanyAddress.query.filter_by(is_active=True).first()
    return render_template('oilgasservicerequest.html',
                         company_name=COMPANY_NAME,
                         support_email=SUPPORT_EMAIL,
                         support_phone=SUPPORT_PHONE,
                         company_address=company_address.address if company_address else '',
                         is_admin_form=True)


@app.route('/oilgasservicerequest/sign/<token>')
def oilgasservicerequest_client_sign(token):
    """Client Signature for Oil & Gas Service Request"""
    submission = FormSubmission.query.filter_by(client_acceptance_token=token, form_type='oilgasservicerequest').first()
    if not submission or submission.client_acceptance_completed:
        return render_template('error.html', message='Invalid or expired link.'), 404
    
    company_address = CompanyAddress.query.filter_by(is_active=True).first()
    request_data = submission.submitted_data if submission.submitted_data else {}
    
    return render_template('oilgasservicerequest.html',
                         company_name=COMPANY_NAME,
                         support_email=SUPPORT_EMAIL,
                         support_phone=SUPPORT_PHONE,
                         company_address=company_address.address if company_address else '',
                         is_admin_form=False,
                         request_token=token,
                         request_data=request_data)


@app.route('/submit-form', methods=['POST'])
@csrf.exempt  # CSRF validation handled via X-CSRFToken header in JavaScript
def submit_form():
    """Handle form submission"""
    try:
        # Handle both JSON and form-encoded data
        if request.is_json:
            form_data = request.get_json()
        else:
            form_data = request.form.to_dict(flat=False)
            # Convert single-item lists to strings
            for key, value in form_data.items():
                if len(value) == 1:
                    form_data[key] = value[0]
                elif len(value) > 1:
                    form_data[key] = value
        
        form_type = form_data.get('form_type')
        
        # Remove form_type from data
        if 'form_type' in form_data:
            del form_data['form_type']
        
        # Handle file uploads for declarationbyemployee form
        if form_type == 'declarationbyemployee':
            if 'employee_photograph' in request.files and request.files['employee_photograph'].filename != '':
                file = request.files['employee_photograph']
                if file:
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f'photo_{timestamp}_{filename}'
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    form_data['employee_photograph'] = filename
            
            if 'employee_nin' in request.files and request.files['employee_nin'].filename != '':
                file = request.files['employee_nin']
                if file:
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f'nin_{timestamp}_{filename}'
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    form_data['employee_nin'] = filename
        
        result = process_form_submission(form_type, form_data)
        
        return jsonify(result)
    except Exception as e:
        import traceback
        error_msg = f'An error occurred: {str(e)}'
        error_trace = traceback.format_exc()
        print(f"[ERROR] submit_form exception: {error_msg}", flush=True)
        print(f"[ERROR] Traceback: {error_trace}", flush=True)
        # Also write to file for debugging
        with open('form_submission_errors.log', 'a') as f:
            f.write(f"\n{'='*80}\nsubmit_form error\n{datetime.now()}\n{error_msg}\n{error_trace}\n")
        return jsonify({'success': False, 'message': error_msg}), 500


@app.route('/test')
def test_system():
    """System test page"""
    php_version = "N/A (Python Flask)"
    
    tests = [
        {
            'name': 'Flask Framework',
            'current': 'Installed',
            'required': 'Required',
            'passed': True
        },
        {
            'name': 'Jinja2 Templates',
            'current': 'Available',
            'required': 'Required',
            'passed': True
        },
        {
            'name': 'Python Email',
            'current': 'Available',
            'required': 'Required',
            'passed': True
        },
        {
            'name': 'Static Files',
            'current': 'Configured',
            'required': 'Required',
            'passed': os.path.exists('static/styles.css')
        },
        {
            'name': 'Templates',
            'current': 'Configured',
            'required': 'Required',
            'passed': os.path.exists('templates')
        },
    ]
    
    all_passed = all(test['passed'] for test in tests)
    
    return render_template('test.html',
                         tests=tests,
                         all_passed=all_passed,
                         company_name=COMPANY_NAME)


# ==================== ADMIN ROUTES ====================

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check SuperAdmin
        superadmin = SuperAdmin.query.filter_by(username=username).first()
        if superadmin and verify_password(password, superadmin.password):
            session['superadmin_id'] = superadmin.id
            session['user_type'] = 'superadmin'
            return redirect(url_for('superadmin_dashboard'))
        
        # Check Admin
        admin = Admin.query.filter_by(username=username, is_active=True).first()
        if admin and verify_password(password, admin.password):
            session['admin_id'] = admin.id
            session['user_type'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        
        flash('Invalid username or password', 'danger')
    
    return render_template('admin_login.html',
                         company_name=COMPANY_NAME,
                         support_email=SUPPORT_EMAIL,
                         support_phone=SUPPORT_PHONE)


@app.route('/admin_logout')
def admin_logout():
    """Logout admin"""
    session.clear()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('index'))


@app.route('/superadmin/dashboard')
@require_superadmin
def superadmin_dashboard():
    """Superadmin dashboard"""
    admins = Admin.query.all()
    notification_emails = NotificationEmail.query.all()
    
    return render_template('superadmin_dashboard.html',
                         admins=admins,
                         notification_emails=notification_emails,
                         company_name=COMPANY_NAME,
                         support_email=SUPPORT_EMAIL,
                         support_phone=SUPPORT_PHONE)


@app.route('/admin/dashboard')
@require_admin_or_superadmin
def admin_dashboard():
    """Admin dashboard (for staff admins)"""
    if is_superadmin_logged_in():
        return redirect(url_for('superadmin_dashboard'))
    
    current_admin = get_current_admin()
    return render_template('admin_dashboard.html',
                         admin=current_admin,
                         company_name=COMPANY_NAME,
                         support_email=SUPPORT_EMAIL,
                         support_phone=SUPPORT_PHONE)


@app.route('/superadmin/admin/create', methods=['GET', 'POST'])
@require_superadmin
def create_admin():
    """Create new admin"""
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone_number')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate
        if not all([first_name, last_name, email, phone, username, password]):
            flash('All fields are required', 'danger')
            return redirect(url_for('create_admin'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('create_admin'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return redirect(url_for('create_admin'))
        
        if Admin.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('create_admin'))
        
        if Admin.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return redirect(url_for('create_admin'))
        
        # Create admin (disabled by default until enabled by superadmin)
        superadmin = get_current_superadmin()
        admin = Admin(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone,
            username=username,
            password=hash_password(password),
            is_active=False,
            created_by=superadmin.id
        )
        db.session.add(admin)
        db.session.commit()
        
        flash(f'Admin {first_name} {last_name} created successfully (disabled - enable to allow login)', 'success')
        return redirect(url_for('superadmin_dashboard'))
    
    return render_template('admin_form.html',
                         company_name=COMPANY_NAME,
                         support_email=SUPPORT_EMAIL,
                         support_phone=SUPPORT_PHONE)


@app.route('/superadmin/admin/<int:admin_id>/edit', methods=['GET'])
@require_superadmin
def edit_admin(admin_id):
    """Edit admin"""
    admin = Admin.query.get_or_404(admin_id)
    
    return render_template('admin_form.html',
                         admin=admin,
                         company_name=COMPANY_NAME,
                         support_email=SUPPORT_EMAIL,
                         support_phone=SUPPORT_PHONE)


@app.route('/superadmin/admin/<int:admin_id>/update', methods=['POST'])
@require_superadmin
def update_admin(admin_id):
    """Update admin"""
    admin = Admin.query.get_or_404(admin_id)
    
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    phone = request.form.get('phone_number')
    password = request.form.get('password')
    is_active = request.form.get('is_active') == '1'
    
    if not all([first_name, last_name, email, phone]):
        flash('All required fields must be filled', 'danger')
        return redirect(url_for('edit_admin', admin_id=admin_id))
    
    # Check for duplicate email (but allow same email)
    if email != admin.email:
        if Admin.query.filter_by(email=email).first():
            flash('Email already in use', 'danger')
            return redirect(url_for('edit_admin', admin_id=admin_id))
    
    admin.first_name = first_name
    admin.last_name = last_name
    admin.email = email
    admin.phone_number = phone
    admin.is_active = is_active
    
    if password:
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return redirect(url_for('edit_admin', admin_id=admin_id))
        admin.password = hash_password(password)
    
    db.session.commit()
    
    flash(f'Admin {first_name} {last_name} updated successfully', 'success')
    return redirect(url_for('superadmin_dashboard'))


@app.route('/superadmin/admin/<int:admin_id>/toggle', methods=['POST'])
@require_superadmin
def toggle_admin(admin_id):
    """Enable/disable admin"""
    admin = Admin.query.get_or_404(admin_id)
    admin.is_active = not admin.is_active
    db.session.commit()
    
    status = 'enabled' if admin.is_active else 'disabled'
    flash(f'Admin {admin.first_name} {admin.last_name} has been {status}', 'success')
    return redirect(url_for('superadmin_dashboard'))


@app.route('/superadmin/submissions/<form_type>')
@require_superadmin
def get_submissions(form_type):
    """Get submissions for a form type (JSON)"""
    submissions = FormSubmission.query.filter_by(form_type=form_type).all()
    
    result = []
    for sub in submissions:
        # Get email - try user_email first, then fall back to client_email from submitted_data
        email = sub.user_email or (sub.submitted_data.get('client_email') if sub.submitted_data else None) or 'N/A'
        
        item = {
            'id': sub.id,
            'submitted_at': sub.submitted_at.isoformat(),
            'user_email': email,
            'status': sub.status or 'pending',
            'pdf_filename': sub.pdf_filename if hasattr(sub, 'pdf_filename') else None,
            'submitted_data': sub.submitted_data
        }
        
        # Add client acceptance fields for forms with two-part workflow
        if form_type in ['trackingagreement', 'serviceagreement', 'oilgasservicerequest']:
            item['client_acceptance_completed'] = sub.client_acceptance_completed if hasattr(sub, 'client_acceptance_completed') else False
            item['client_acceptance_completed_at'] = sub.client_acceptance_completed_at.isoformat() if hasattr(sub, 'client_acceptance_completed_at') and sub.client_acceptance_completed_at else None
            item['client_acceptance_link'] = sub.client_acceptance_link if hasattr(sub, 'client_acceptance_link') else None
            item['client_acceptance_token'] = sub.client_acceptance_token if hasattr(sub, 'client_acceptance_token') else None
            item['final_pdf_filename'] = sub.final_pdf_filename if hasattr(sub, 'final_pdf_filename') else None
        
        result.append(item)
    
    return jsonify({'submissions': result})


@app.route('/superadmin/submission/<int:submission_id>')
@require_superadmin
def view_submission(submission_id):
    """View submission details"""
    submission = FormSubmission.query.get_or_404(submission_id)
    
    return render_template('submission_details.html',
                         submission=submission,
                         company_name=COMPANY_NAME,
                         support_email=SUPPORT_EMAIL,
                         support_phone=SUPPORT_PHONE)


@app.route('/submission/<int:submission_id>/pdf')
@require_admin_or_superadmin
def view_submission_pdf(submission_id):
    """View/download the approved PDF for a submission"""
    submission = FormSubmission.query.get_or_404(submission_id)
    
    # Check if PDF exists - try both pdf_filename and final_pdf_filename
    pdf_filename = None
    if hasattr(submission, 'final_pdf_filename') and submission.final_pdf_filename:
        pdf_filename = submission.final_pdf_filename
    elif hasattr(submission, 'pdf_filename') and submission.pdf_filename:
        pdf_filename = submission.pdf_filename
    
    if not pdf_filename:
        flash('No PDF available for this submission', 'danger')
        return redirect(request.referrer or url_for('superadmin_dashboard'))
    
    pdf_path = os.path.join(app.config['PDFS_FOLDER'], pdf_filename)
    
    if not os.path.exists(pdf_path):
        flash('PDF file not found', 'danger')
        return redirect(request.referrer or url_for('superadmin_dashboard'))
    
    return send_file(pdf_path, as_attachment=False, mimetype='application/pdf')


@app.route('/submission/<int:submission_id>/nin')
@require_admin_or_superadmin
def download_submission_nin(submission_id):
    """Download the NIN/ID file for an employee declaration"""
    submission = FormSubmission.query.get_or_404(submission_id)
    
    # Only allow NIN download for declarationbyemployee forms
    if submission.form_type != 'declarationbyemployee':
        flash('This submission does not have a NIN file', 'danger')
        return redirect(request.referrer or url_for('superadmin_dashboard'))
    
    # Check if NIN file exists
    if not hasattr(submission, 'nin_filename') or not submission.nin_filename:
        flash('No NIN file available for this submission', 'danger')
        return redirect(request.referrer or url_for('superadmin_dashboard'))
    
    nin_path = os.path.join(app.config['UPLOAD_FOLDER'], submission.nin_filename)
    
    if not os.path.exists(nin_path):
        flash('NIN file not found', 'danger')
        return redirect(request.referrer or url_for('superadmin_dashboard'))
    
    return send_file(nin_path, as_attachment=True, download_name=f"NIN_{submission_id}_{submission.nin_filename.split('_', 2)[-1]}")


@app.route('/submission/<int:submission_id>/photo')
@require_admin_or_superadmin
def download_submission_photo(submission_id):
    """Download the passport photo for an employee declaration"""
    submission = FormSubmission.query.get_or_404(submission_id)
    
    # Only allow photo download for declarationbyemployee forms
    if submission.form_type != 'declarationbyemployee':
        flash('This submission does not have a photo file', 'danger')
        return redirect(request.referrer or url_for('superadmin_dashboard'))
    
    # Check if photo file exists
    if not hasattr(submission, 'photo_filename') or not submission.photo_filename:
        flash('No photo file available for this submission', 'danger')
        return redirect(request.referrer or url_for('superadmin_dashboard'))
    
    photo_path = os.path.join(app.config['UPLOAD_FOLDER'], submission.photo_filename)
    
    if not os.path.exists(photo_path):
        flash('Photo file not found', 'danger')
        return redirect(request.referrer or url_for('superadmin_dashboard'))
    
    return send_file(photo_path, as_attachment=True, download_name=f"PHOTO_{submission_id}_{submission.photo_filename.split('_', 2)[-1]}")


# ==================== ADMIN SUBMISSION ROUTES ====================
# These allow regular admins (staff) to view form submissions

@app.route('/admin/submissions/<form_type>')
@require_admin_or_superadmin
def get_admin_submissions(form_type):
    """Get submissions for a form type - accessible to admins (JSON)"""
    if is_superadmin_logged_in():
        # Superadmin can see all submissions
        submissions = FormSubmission.query.filter_by(form_type=form_type).all()
    else:
        # Regular admin can see all submissions (no restrictions)
        submissions = FormSubmission.query.filter_by(form_type=form_type).all()
    
    result = []
    for sub in submissions:
        item = {
            'id': sub.id,
            'submitted_at': sub.submitted_at.isoformat(),
            'user_email': sub.user_email or (sub.submitted_data.get('client_email') if sub.form_type == 'trackingagreement' else None) or 'N/A',
            'status': sub.status or 'pending',
            'pdf_filename': sub.pdf_filename if hasattr(sub, 'pdf_filename') else None,
            'submitted_data': sub.submitted_data
        }
        
        # Add client acceptance fields for forms with two-part workflow
        if form_type in ['trackingagreement', 'serviceagreement', 'oilgasservicerequest']:
            item['client_acceptance_completed'] = sub.client_acceptance_completed if hasattr(sub, 'client_acceptance_completed') else False
            item['client_acceptance_completed_at'] = sub.client_acceptance_completed_at.isoformat() if hasattr(sub, 'client_acceptance_completed_at') and sub.client_acceptance_completed_at else None
            item['client_acceptance_link'] = sub.client_acceptance_link if hasattr(sub, 'client_acceptance_link') else None
            item['client_acceptance_token'] = sub.client_acceptance_token if hasattr(sub, 'client_acceptance_token') else None
            item['final_pdf_filename'] = sub.final_pdf_filename if hasattr(sub, 'final_pdf_filename') else None
        
        result.append(item)
    
    return jsonify({'submissions': result})


@app.route('/admin/submission/<int:submission_id>')
@require_admin_or_superadmin
def view_admin_submission(submission_id):
    """View submission details - accessible to admins"""
    submission = FormSubmission.query.get_or_404(submission_id)
    
    return render_template('submission_details.html',
                         submission=submission,
                         company_name=COMPANY_NAME,
                         support_email=SUPPORT_EMAIL,
                         support_phone=SUPPORT_PHONE)


# ==================== APPROVAL ROUTES ====================
# Routes for superadmin and admin to approve service agreements

@app.route('/superadmin/approve-agreement/<int:submission_id>', methods=['GET'])
@require_superadmin
def show_approval_form_superadmin(submission_id):
    """Show approval form for superadmin"""
    submission = FormSubmission.query.get_or_404(submission_id)
    
    # Only allow approving service agreements with pending_approval status
    if submission.form_type != 'serviceagreement' or submission.status != 'pending_approval':
        flash('This agreement cannot be approved', 'danger')
        return redirect(url_for('view_submission', submission_id=submission_id))
    
    current_user = SuperAdmin.query.get(session.get('user_id'))
    return render_template('approve_serviceagreement.html',
                         submission=submission,
                         current_user=current_user,
                         approver_role='superadmin')


@app.route('/superadmin/approve-agreement/<int:submission_id>', methods=['POST'])
@require_superadmin
def process_approval_superadmin(submission_id):
    """Process approval from superadmin"""
    submission = FormSubmission.query.get_or_404(submission_id)
    
    # Validate submission
    if submission.form_type != 'serviceagreement' or submission.status != 'pending_approval':
        flash('This agreement cannot be approved', 'danger')
        return redirect(url_for('view_submission', submission_id=submission_id))
    
    approver_name = request.form.get('approver_name', '').strip()
    approver_email = request.form.get('approver_email', '').strip()
    approver_position = request.form.get('approver_position', '').strip()
    signature_data = request.form.get('signature_data', '').strip()             # uploaded
    signature_data_drawn = request.form.get('signature_data_drawn', '').strip() # drawn

    if not approver_name:
        flash('Approver name is required', 'danger')
        return redirect(url_for('show_approval_form_superadmin', submission_id=submission_id))

    if not approver_email or not validate_email(approver_email):
        flash('Valid approver email is required', 'danger')
        return redirect(url_for('show_approval_form_superadmin', submission_id=submission_id))

    if not approver_position:
        flash('Approver position/title is required', 'danger')
        return redirect(url_for('show_approval_form_superadmin', submission_id=submission_id))

    if not signature_data and not signature_data_drawn:
        flash('Signature is required', 'danger')
        return redirect(url_for('show_approval_form_superadmin', submission_id=submission_id))

    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        stamp_filepath = None
        stamp_drawn_filepath = None
        filename = None

        # Save uploaded signature
        if signature_data:
            sig_bytes = base64.b64decode(signature_data.split(',')[1] if ',' in signature_data else signature_data)
            filename = secure_filename(f'approval_signature_{submission_id}_{timestamp}.png')
            stamp_filepath = os.path.join(app.config['STAMPS_FOLDER'], filename)
            with open(stamp_filepath, 'wb') as f:
                f.write(sig_bytes)

        # Save drawn signature
        if signature_data_drawn:
            sig_bytes_drawn = base64.b64decode(signature_data_drawn.split(',')[1] if ',' in signature_data_drawn else signature_data_drawn)
            filename_drawn = secure_filename(f'approval_sig_drawn_{submission_id}_{timestamp}.png')
            stamp_drawn_filepath = os.path.join(app.config['STAMPS_FOLDER'], filename_drawn)
            with open(stamp_drawn_filepath, 'wb') as f:
                f.write(sig_bytes_drawn)
            if not filename:
                filename = filename_drawn

        # Update submission
        current_user = SuperAdmin.query.get(session.get('superadmin_id'))
        submission.status = 'approved'
        submission.approved_by_superadmin = current_user.id
        submission.approved_at = datetime.now()
        submission.approver_position = approver_position
        if filename:
            submission.stamp_filename = filename
        db.session.commit()

        # Generate PDF with approval
        pdf_filename = f'service_agreement_{submission_id}_approved.pdf'
        pdf_filepath = os.path.join(app.config['PDFS_FOLDER'], pdf_filename)

        # Generate PDF and capture result
        generated_pdf = generate_service_agreement_pdf(submission_id, stamp_path=stamp_filepath,
                                      stamp_drawn_path=stamp_drawn_filepath,
                                      output_path=pdf_filepath,
                                      approver_name=approver_name,
                                      approver_email=approver_email,
                                      approver_position=approver_position)
        
        # Send emails to client and approver
        client_email = submission.user_email
        
        # Email to client
        client_subject = f'Service Agreement Approved - {COMPANY_NAME}'
        client_html = f"""
        <html>
        <body style="font-family: 'Poppins', 'Segoe UI', sans-serif; color: #333;">
            <h2>Your Service Agreement Has Been Approved</h2>
            <p>Dear Client,</p>
            <p>Your service agreement has been reviewed and approved by {approver_name}, {approver_position} at {COMPANY_NAME}.</p>
            <p><strong>Approval Date:</strong> {datetime.now().strftime('%d %B %Y at %H:%M:%S')}</p>
            <p><strong>Approved By:</strong> {approver_name}, {approver_position} ({approver_email})</p>
            <p>Please find the signed agreement attached to this email.</p>
            <p>If you have any questions, please contact us at {SUPPORT_EMAIL}.</p>
            <p>Best regards,<br>{COMPANY_NAME}</p>
        </body>
        </html>
        """
        if generated_pdf:
            send_email_with_attachment(client_email, client_subject, client_html, 
                                      pdf_filepath, pdf_filename)
        else:
            send_email_with_attachment(client_email, client_subject, client_html, None, None)
        
        # Email to approver
        approver_subject = f'Service Agreement Approved - {COMPANY_NAME}'
        approver_html = f"""
        <html>
        <body style="font-family: 'Poppins', 'Segoe UI', sans-serif; color: #333;">
            <h2>Service Agreement Approval Confirmation</h2>
            <p>Dear {approver_name},</p>
            <p>This is to confirm that you have approved the service agreement for submission #{submission_id}.</p>
            <p><strong>Client Email:</strong> {client_email}</p>
            <p><strong>Approval Date:</strong> {datetime.now().strftime('%d %B %Y at %H:%M:%S')}</p>
            <p>The approved agreement has been sent to the client.</p>
            <p>Best regards,<br>{COMPANY_NAME}</p>
        </body>
        </html>
        """
        if generated_pdf:
            send_email_with_attachment(approver_email, approver_subject, approver_html,
                                      pdf_filepath, pdf_filename)
        else:
            send_email_with_attachment(approver_email, approver_subject, approver_html, None, None)
        
        # Save PDF filename to submission ONLY if PDF was generated successfully
        if generated_pdf:
            submission.pdf_filename = pdf_filename
            submission.final_pdf_filename = pdf_filename
            db.session.commit()
            flash('Agreement approved successfully! PDF sent to client and approver.', 'success')
        else:
            db.session.commit()
            flash('Agreement approved successfully. PDF generation encountered an issue.', 'warning')
        return redirect(url_for('view_submission', submission_id=submission_id))
        
    except Exception as e:
        print(f"Error processing approval: {str(e)}")
        db.session.rollback()
        flash(f'Error approving agreement: {str(e)}', 'danger')
        return redirect(url_for('show_approval_form_superadmin', submission_id=submission_id))


@app.route('/admin/approve-agreement/<int:submission_id>', methods=['GET'])
@require_admin_or_superadmin
def show_approval_form_admin(submission_id):
    """Show approval form for admin"""
    submission = FormSubmission.query.get_or_404(submission_id)
    
    # Only allow approving service agreements with pending_approval status
    if submission.form_type != 'serviceagreement' or submission.status != 'pending_approval':
        flash('This agreement cannot be approved', 'danger')
        return redirect(url_for('view_admin_submission', submission_id=submission_id))
    
    current_user = None
    if is_superadmin_logged_in():
        current_user = SuperAdmin.query.get(session.get('user_id'))
        approver_role = 'superadmin'
    else:
        current_user = Admin.query.get(session.get('user_id'))
        approver_role = 'admin'
    
    return render_template('approve_serviceagreement.html',
                         submission=submission,
                         current_user=current_user,
                         approver_role=approver_role)


@app.route('/admin/approve-agreement/<int:submission_id>', methods=['POST'])
@require_admin_or_superadmin
def process_approval_admin(submission_id):
    """Process approval from admin or superadmin"""
    print(f"\n[DEBUG] process_approval_admin called with submission_id={submission_id}")
    submission = FormSubmission.query.get_or_404(submission_id)
    
    # Validate submission
    if submission.form_type != 'serviceagreement' or submission.status != 'pending_approval':
        flash('This agreement cannot be approved', 'danger')
        return redirect(url_for('view_admin_submission', submission_id=submission_id))
    
    approver_name = request.form.get('approver_name', '').strip()
    approver_email = request.form.get('approver_email', '').strip()
    approver_position = request.form.get('approver_position', '').strip()
    signature_data = request.form.get('signature_data', '').strip()
    
    # DEBUG: Log what was received
    print(f"\n=== ADMIN APPROVAL ROUTE DEBUG ===")
    print(f"Name: '{approver_name}' (len: {len(approver_name)})")
    print(f"Email: '{approver_email}' (len: {len(approver_email)})")
    print(f"Position: '{approver_position}' (len: {len(approver_position)})")
    print(f"Sig data: '{signature_data[:50]}...' (len: {len(signature_data)})")
    print(f"ALL form keys: {list(request.form.keys())}")
    print(f"===================================\n")
    
    if not approver_name:
        flash('Approver name is required', 'danger')
        return redirect(url_for('show_approval_form_admin', submission_id=submission_id))
    
    if not approver_email or not validate_email(approver_email):
        flash('Valid approver email is required', 'danger')
        return redirect(url_for('show_approval_form_admin', submission_id=submission_id))
    
    if not approver_position:
        flash('Approver position/title is required', 'danger')
        return redirect(url_for('show_approval_form_admin', submission_id=submission_id))
    
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        stamp_filepath = None
        stamp_drawn_filepath = None
        filename = None

        # Save uploaded signature
        if signature_data:
            sig_bytes = base64.b64decode(signature_data.split(',')[1] if ',' in signature_data else signature_data)
            filename = secure_filename(f'approval_signature_{submission_id}_{timestamp}.png')
            stamp_filepath = os.path.join(app.config['STAMPS_FOLDER'], filename)
            with open(stamp_filepath, 'wb') as f:
                f.write(sig_bytes)

        # Save drawn signature
        if signature_data_drawn:
            sig_bytes_drawn = base64.b64decode(signature_data_drawn.split(',')[1] if ',' in signature_data_drawn else signature_data_drawn)
            filename_drawn = secure_filename(f'approval_sig_drawn_{submission_id}_{timestamp}.png')
            stamp_drawn_filepath = os.path.join(app.config['STAMPS_FOLDER'], filename_drawn)
            with open(stamp_drawn_filepath, 'wb') as f:
                f.write(sig_bytes_drawn)
            if not filename:
                filename = filename_drawn

        # Update submission
        current_user = None
        if is_superadmin_logged_in():
            current_user = SuperAdmin.query.get(session.get('superadmin_id'))
            submission.approved_by_superadmin = current_user.id
        else:
            current_user = Admin.query.get(session.get('admin_id'))
            submission.approved_by_admin = current_user.id

        submission.status = 'approved'
        submission.approved_at = datetime.now()
        submission.approver_position = approver_position
        if filename:
            submission.stamp_filename = filename
        db.session.commit()

        # Generate PDF with approval
        pdf_filename = f'service_agreement_{submission_id}_approved.pdf'
        pdf_filepath = os.path.join(app.config['PDFS_FOLDER'], pdf_filename)

        # Generate PDF and capture result
        generated_pdf = generate_service_agreement_pdf(submission_id, stamp_path=stamp_filepath,
                                                      stamp_drawn_path=stamp_drawn_filepath,
                                                      output_path=pdf_filepath,
                                                      approver_name=approver_name,
                                                      approver_email=approver_email,
                                                      approver_position=approver_position)
        
        # Send emails to client and approver
        client_email = submission.user_email
        
        # Email to client
        client_subject = f'Service Agreement Approved - {COMPANY_NAME}'
        client_html = f"""
        <html>
        <body style="font-family: 'Poppins', 'Segoe UI', sans-serif; color: #333;">
            <h2>Your Service Agreement Has Been Approved</h2>
            <p>Dear Client,</p>
            <p>Your service agreement has been reviewed and approved by {approver_name}, {approver_position} at {COMPANY_NAME}.</p>
            <p><strong>Approval Date:</strong> {datetime.now().strftime('%d %B %Y at %H:%M:%S')}</p>
            <p><strong>Approved By:</strong> {approver_name}, {approver_position} ({approver_email})</p>
            <p>Please find the signed agreement attached to this email.</p>
            <p>If you have any questions, please contact us at {SUPPORT_EMAIL}.</p>
            <p>Best regards,<br>{COMPANY_NAME}</p>
        </body>
        </html>
        """
        if generated_pdf:
            send_email_with_attachment(client_email, client_subject, client_html,
                                      pdf_filepath, pdf_filename)
        else:
            send_email_with_attachment(client_email, client_subject, client_html, None, None)
        
        # Email to approver
        approver_subject = f'Service Agreement Approved - {COMPANY_NAME}'
        approver_html = f"""
        <html>
        <body style="font-family: 'Poppins', 'Segoe UI', sans-serif; color: #333;">
            <h2>Service Agreement Approval Confirmation</h2>
            <p>Dear {approver_name},</p>
            <p>This is to confirm that you have approved the service agreement for submission #{submission_id}.</p>
            <p><strong>Client Email:</strong> {client_email}</p>
            <p><strong>Approval Date:</strong> {datetime.now().strftime('%d %B %Y at %H:%M:%S')}</p>
            <p>The approved agreement has been sent to the client.</p>
            <p>Best regards,<br>{COMPANY_NAME}</p>
        </body>
        </html>
        """
        if generated_pdf:
            send_email_with_attachment(approver_email, approver_subject, approver_html,
                                      pdf_filepath, pdf_filename)
        else:
            send_email_with_attachment(approver_email, approver_subject, approver_html, None, None)
        
        # Save PDF filename to submission ONLY if PDF was generated successfully
        if generated_pdf:
            submission.pdf_filename = pdf_filename
            submission.final_pdf_filename = pdf_filename
            db.session.commit()
            flash('Agreement approved successfully! PDF sent to client and approver.', 'success')
        else:
            db.session.commit()
            flash('Agreement approved successfully. PDF generation encountered an issue.', 'warning')
        return redirect(url_for('view_admin_submission', submission_id=submission_id))
        
    except Exception as e:
        print(f"Error processing approval: {str(e)}")
        db.session.rollback()
        flash(f'Error approving agreement: {str(e)}', 'danger')
        return redirect(url_for('show_approval_form_admin', submission_id=submission_id))


@app.route('/admin/approve-backgroundcheck/<int:submission_id>', methods=['GET'])
@require_admin_or_superadmin
def show_approval_form_backgroundcheck(submission_id):
    """Show approval form for background checks"""
    submission = FormSubmission.query.get_or_404(submission_id)
    
    # Only allow approving background checks with pending_approval status
    if submission.form_type != 'backgroundcheck' or submission.status != 'pending_approval':
        flash('This agreement cannot be approved', 'danger')
        return redirect(url_for('view_admin_submission', submission_id=submission_id))
    
    current_user = None
    if is_superadmin_logged_in():
        current_user = SuperAdmin.query.get(session.get('user_id'))
        approver_role = 'superadmin'
    else:
        current_user = Admin.query.get(session.get('user_id'))
        approver_role = 'admin'
    
    return render_template('approve_backgroundcheck.html',
                         submission=submission,
                         current_user=current_user,
                         approver_role=approver_role)


@app.route('/admin/approve-backgroundcheck/<int:submission_id>', methods=['POST'])
@require_admin_or_superadmin
def process_approval_backgroundcheck(submission_id):
    """Process approval for background checks"""
    print(f"\n[DEBUG] process_approval_backgroundcheck called with submission_id={submission_id}")
    submission = FormSubmission.query.get_or_404(submission_id)
    
    # Validate submission
    if submission.form_type != 'backgroundcheck' or submission.status != 'pending_approval':
        flash('This agreement cannot be approved', 'danger')
        return redirect(url_for('view_admin_submission', submission_id=submission_id))
    
    approver_name = request.form.get('approver_name', '').strip()
    approver_email = request.form.get('approver_email', '').strip()
    approver_position = request.form.get('approver_position', '').strip()
    signature_data = request.form.get('signature_data', '').strip()       # uploaded
    signature_data_drawn = request.form.get('signature_data_drawn', '').strip()  # drawn
    
    if not approver_name:
        flash('Approver name is required', 'danger')
        return redirect(url_for('show_approval_form_backgroundcheck', submission_id=submission_id))
    
    if not approver_email or not validate_email(approver_email):
        flash('Valid approver email is required', 'danger')
        return redirect(url_for('show_approval_form_backgroundcheck', submission_id=submission_id))
    
    if not approver_position:
        flash('Approver position/title is required', 'danger')
        return redirect(url_for('show_approval_form_backgroundcheck', submission_id=submission_id))
    
    if not signature_data and not signature_data_drawn:
        flash('Signature is required', 'danger')
        return redirect(url_for('show_approval_form_backgroundcheck', submission_id=submission_id))
    
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        stamp_filepath = None
        stamp_drawn_filepath = None

        # Save uploaded/legacy signature
        if signature_data:
            sig_bytes = base64.b64decode(signature_data.split(',')[1] if ',' in signature_data else signature_data)
            filename = secure_filename(f'approval_signature_{submission_id}_{timestamp}.png')
            stamp_filepath = os.path.join(app.config['STAMPS_FOLDER'], filename)
            with open(stamp_filepath, 'wb') as f:
                f.write(sig_bytes)
        else:
            filename = None

        # Save drawn signature
        if signature_data_drawn:
            sig_bytes_drawn = base64.b64decode(signature_data_drawn.split(',')[1] if ',' in signature_data_drawn else signature_data_drawn)
            filename_drawn = secure_filename(f'approval_sig_drawn_{submission_id}_{timestamp}.png')
            stamp_drawn_filepath = os.path.join(app.config['STAMPS_FOLDER'], filename_drawn)
            with open(stamp_drawn_filepath, 'wb') as f:
                f.write(sig_bytes_drawn)
            if not filename:
                filename = filename_drawn  # store at least one filename
        
        # Update submission
        current_user = None
        if is_superadmin_logged_in():
            current_user = SuperAdmin.query.get(session.get('superadmin_id'))
            submission.approved_by_superadmin = current_user.id
        else:
            current_user = Admin.query.get(session.get('admin_id'))
            submission.approved_by_admin = current_user.id
        
        submission.status = 'approved'
        submission.approved_at = datetime.now()
        submission.approver_position = approver_position
        if filename:
            submission.stamp_filename = filename
        db.session.commit()
        
        # Generate PDF approval document
        pdf_filename = generate_backgroundchecks_approval_pdf(
            submission_id,
            stamp_path=stamp_filepath,
            stamp_drawn_path=stamp_drawn_filepath,
            approver_name=approver_name,
            approver_email=approver_email,
            approver_position=approver_position
        )
        
        # Update submission with PDF filename if generated successfully
        if pdf_filename:
            submission.pdf_filename = pdf_filename
            db.session.commit()
            print(f"[process_approval_backgroundchecks] PDF saved to database: {pdf_filename}")
        else:
            print(f"[process_approval_backgroundchecks] PDF generation failed")
        
        # Send emails to client and approver
        client_email = submission.user_email
        
        # Email to client
        client_subject = f'Background Check Service Agreement Approved - {COMPANY_NAME}'
        client_html = f"""
        <html>
        <body style="font-family: 'Poppins', 'Segoe UI', sans-serif; color: #333;">
            <h2>Your Background Check Service Agreement Has Been Approved</h2>
            <p>Dear Client,</p>
            <p>Your background check service agreement has been reviewed and approved by {approver_name}, {approver_position} at {COMPANY_NAME}.</p>
            <p><strong>Approval Date:</strong> {datetime.now().strftime('%d %B %Y at %H:%M:%S')}</p>
            <p><strong>Approved By:</strong> {approver_name}, {approver_position} ({approver_email})</p>
            <p>If you have any questions, please contact us at {SUPPORT_EMAIL}.</p>
            <p>Best regards,<br>{COMPANY_NAME}</p>
        </body>
        </html>
        """
        send_email_with_attachment(client_email, client_subject, client_html, None, None)
        
        # Email to approver
        approver_subject = f'Background Check Service Agreement Approved - {COMPANY_NAME}'
        approver_html = f"""
        <html>
        <body style="font-family: 'Poppins', 'Segoe UI', sans-serif; color: #333;">
            <h2>Background Check Service Agreement Approval Confirmation</h2>
            <p>Dear {approver_name},</p>
            <p>This is to confirm that you have approved the background check service agreement for submission #{submission_id}.</p>
            <p><strong>Client Email:</strong> {client_email}</p>
            <p><strong>Approval Date:</strong> {datetime.now().strftime('%d %B %Y at %H:%M:%S')}</p>
            <p>Best regards,<br>{COMPANY_NAME}</p>
        </body>
        </html>
        """
        send_email_with_attachment(approver_email, approver_subject, approver_html, None, None)
        
        db.session.commit()
        flash('Background Check Agreement approved successfully!', 'success')
        return redirect(url_for('view_admin_submission', submission_id=submission_id))
        
    except Exception as e:
        print(f"Error processing background check approval: {str(e)}")
        db.session.rollback()
        flash(f'Error approving agreement: {str(e)}', 'danger')
        return redirect(url_for('show_approval_form_backgroundcheck', submission_id=submission_id))


@app.route('/admin/regenerate-backgroundcheck-pdf/<int:submission_id>', methods=['POST'])
@csrf.exempt
@require_admin_or_superadmin
def regenerate_backgroundcheck_pdf(submission_id):
    """Regenerate the approval PDF for an already-approved backgroundcheck submission"""
    submission = FormSubmission.query.get_or_404(submission_id)

    if submission.form_type != 'backgroundcheck' or submission.status != 'approved':
        return jsonify({'success': False, 'error': 'Submission is not an approved backgroundcheck'}), 400

    # Resolve approver info from stored relationships
    approver_name = None
    approver_email = None
    if submission.approved_by_superadmin:
        sa = SuperAdmin.query.get(submission.approved_by_superadmin)
        if sa:
            approver_name = sa.username
            approver_email = sa.email
    elif submission.approved_by_admin:
        adm = Admin.query.get(submission.approved_by_admin)
        if adm:
            approver_name = f"{adm.first_name} {adm.last_name}".strip()
            approver_email = adm.email

    approver_position = submission.approver_position or 'Company Representative'

    # Resolve stamp file paths
    stamp_filepath = None
    stamp_drawn_filepath = None
    if submission.stamp_filename:
        candidate = os.path.join(app.config['STAMPS_FOLDER'], submission.stamp_filename)
        if os.path.exists(candidate):
            stamp_filepath = candidate

    try:
        pdf_filename = generate_backgroundchecks_approval_pdf(
            submission_id,
            stamp_path=stamp_filepath,
            stamp_drawn_path=stamp_drawn_filepath,
            approver_name=approver_name,
            approver_email=approver_email,
            approver_position=approver_position
        )
        if pdf_filename:
            submission.pdf_filename = pdf_filename
            db.session.commit()
            return jsonify({'success': True, 'pdf_filename': pdf_filename})
        else:
            # Check the Flask/server logs for the detailed traceback
            return jsonify({'success': False, 'error': 'PDF generation failed - check server logs for details'}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== CLIENT ENGAGEMENT APPROVAL ROUTES ====================

@app.route('/admin/approve-clientengagement/<int:submission_id>', methods=['GET'])
@require_admin_or_superadmin
def show_approval_form_clientengagement(submission_id):
    """Show approval form for client engagement"""
    submission = FormSubmission.query.get_or_404(submission_id)
    
    # Only allow approving client engagement with pending_approval status
    if submission.form_type != 'clientengagement' or submission.status != 'pending_approval':
        flash('This form cannot be approved', 'danger')
        return redirect(url_for('view_admin_submission', submission_id=submission_id))
    
    current_user = None
    if is_superadmin_logged_in():
        current_user = SuperAdmin.query.get(session.get('user_id'))
        approver_role = 'superadmin'
    else:
        current_user = Admin.query.get(session.get('user_id'))
        approver_role = 'admin'
    
    return render_template('approve_clientengagement.html',
                         submission=submission,
                         current_user=current_user,
                         approver_role=approver_role)


@app.route('/admin/approve-clientengagement/<int:submission_id>', methods=['POST'])
@require_admin_or_superadmin
def process_approval_clientengagement(submission_id):
    """Process approval for client engagement"""
    print(f"\n[DEBUG] process_approval_clientengagement called with submission_id={submission_id}")
    submission = FormSubmission.query.get_or_404(submission_id)
    
    # Validate submission
    if submission.form_type != 'clientengagement' or submission.status != 'pending_approval':
        flash('This form cannot be approved', 'danger')
        return redirect(url_for('view_admin_submission', submission_id=submission_id))
    
    approver_name = request.form.get('approver_name', '').strip()
    approver_email = request.form.get('approver_email', '').strip()
    approver_position = request.form.get('approver_position', '').strip()
    signature_data = request.form.get('signature_data', '').strip()          # uploaded
    signature_data_drawn = request.form.get('signature_data_drawn', '').strip()  # drawn

    if not approver_name:
        flash('Approver name is required', 'danger')
        return redirect(url_for('show_approval_form_clientengagement', submission_id=submission_id))

    if not approver_email or not validate_email(approver_email):
        flash('Valid approver email is required', 'danger')
        return redirect(url_for('show_approval_form_clientengagement', submission_id=submission_id))

    if not approver_position:
        flash('Approver position/title is required', 'danger')
        return redirect(url_for('show_approval_form_clientengagement', submission_id=submission_id))

    if not signature_data and not signature_data_drawn:
        flash('Signature is required', 'danger')
        return redirect(url_for('show_approval_form_clientengagement', submission_id=submission_id))

    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        stamp_filepath = None
        stamp_drawn_filepath = None
        filename = None

        # Save uploaded signature
        if signature_data:
            sig_bytes = base64.b64decode(signature_data.split(',')[1] if ',' in signature_data else signature_data)
            filename = secure_filename(f'approval_signature_ce_{submission_id}_{timestamp}.png')
            stamp_filepath = os.path.join(app.config['STAMPS_FOLDER'], filename)
            with open(stamp_filepath, 'wb') as f:
                f.write(sig_bytes)

        # Save drawn signature
        if signature_data_drawn:
            sig_bytes_drawn = base64.b64decode(signature_data_drawn.split(',')[1] if ',' in signature_data_drawn else signature_data_drawn)
            filename_drawn = secure_filename(f'approval_sig_drawn_ce_{submission_id}_{timestamp}.png')
            stamp_drawn_filepath = os.path.join(app.config['STAMPS_FOLDER'], filename_drawn)
            with open(stamp_drawn_filepath, 'wb') as f:
                f.write(sig_bytes_drawn)
            if not filename:
                filename = filename_drawn

        # Update submission
        current_user = None
        if is_superadmin_logged_in():
            current_user = SuperAdmin.query.get(session.get('superadmin_id'))
            submission.approved_by_superadmin = current_user.id
        else:
            current_user = Admin.query.get(session.get('admin_id'))
            submission.approved_by_admin = current_user.id

        submission.status = 'approved'
        submission.approved_at = datetime.now()
        submission.approver_position = approver_position
        if filename:
            submission.stamp_filename = filename
        db.session.commit()

        # Generate PDF approval document
        pdf_filename = generate_clientengagement_approval_pdf(
            submission_id,
            stamp_path=stamp_filepath,
            stamp_drawn_path=stamp_drawn_filepath,
            approver_name=approver_name,
            approver_email=approver_email,
            approver_position=approver_position
        )
        
        # Update submission with PDF filename if generated successfully
        if pdf_filename:
            submission.pdf_filename = pdf_filename
            db.session.commit()
            print(f"[process_approval_clientengagement] PDF saved to database: {pdf_filename}")
        else:
            print(f"[process_approval_clientengagement] PDF generation failed")
        
        # Send emails to client and approver
        client_email = submission.user_email or submission.submitted_data.get('client_email')
        
        # Email to client
        client_subject = f'Client Engagement Form Approved - {COMPANY_NAME}'
        client_html = f"""
        <html>
        <body style="font-family: 'Poppins', 'Segoe UI', sans-serif; color: #333;">
            <h2>Your Client Engagement Form Has Been Approved</h2>
            <p>Dear Client,</p>
            <p>Your client engagement form has been reviewed and approved by {approver_name}, {approver_position} at {COMPANY_NAME}.</p>
            <p><strong>Approval Date:</strong> {datetime.now().strftime('%d %B %Y at %H:%M:%S')}</p>
            <p><strong>Approved By:</strong> {approver_name}, {approver_position} ({approver_email})</p>
            <p>The approved agreement document is attached to this email.</p>
            <p>If you have any questions, please contact us at {SUPPORT_EMAIL}.</p>
            <p>Best regards,<br>{COMPANY_NAME}</p>
        </body>
        </html>
        """
        
        # Add PDF attachment if available
        pdf_path = None
        if pdf_filename:
            pdf_path = os.path.join(PDFS_FOLDER, pdf_filename)
        
        send_email_with_attachment(client_email, client_subject, client_html, pdf_path, pdf_filename)
        
        # Email to approver
        approver_subject = f'Client Engagement Form Approval Confirmation - {COMPANY_NAME}'
        approver_html = f"""
        <html>
        <body style="font-family: 'Poppins', 'Segoe UI', sans-serif; color: #333;">
            <h2>Client Engagement Form Approval Confirmation</h2>
            <p>Dear {approver_name},</p>
            <p>This is to confirm that you have approved the client engagement form for submission #{submission_id}.</p>
            <p><strong>Client Email:</strong> {client_email}</p>
            <p><strong>Approval Date:</strong> {datetime.now().strftime('%d %B %Y at %H:%M:%S')}</p>
            <p>The approved agreement has been sent to the client.</p>
            <p>Best regards,<br>{COMPANY_NAME}</p>
        </body>
        </html>
        """
        send_email_with_attachment(approver_email, approver_subject, approver_html, pdf_path, pdf_filename)
        
        db.session.commit()
        flash('Client Engagement Form approved successfully!', 'success')
        return redirect(url_for('view_admin_submission', submission_id=submission_id))
        
    except Exception as e:
        print(f"Error processing client engagement approval: {str(e)}")
        db.session.rollback()
        flash(f'Error approving form: {str(e)}', 'danger')
        return redirect(url_for('show_approval_form_clientengagement', submission_id=submission_id))


@app.route('/admin/regenerate-clientengagement-pdf/<int:submission_id>', methods=['POST'])
@csrf.exempt
@require_admin_or_superadmin
def regenerate_clientengagement_pdf(submission_id):
    """Regenerate the approval PDF for an already-approved clientengagement submission"""
    submission = FormSubmission.query.get_or_404(submission_id)

    if submission.form_type != 'clientengagement' or submission.status != 'approved':
        return jsonify({'success': False, 'error': 'Submission is not an approved clientengagement'}), 400

    # Resolve approver info
    approver_name = None
    approver_email = None
    if submission.approved_by_superadmin:
        sa = SuperAdmin.query.get(submission.approved_by_superadmin)
        if sa:
            approver_name = sa.username
            approver_email = sa.email
    elif submission.approved_by_admin:
        adm = Admin.query.get(submission.approved_by_admin)
        if adm:
            approver_name = f"{adm.first_name} {adm.last_name}".strip()
            approver_email = adm.email

    approver_position = submission.approver_position or 'Company Representative'

    stamp_filepath = None
    if submission.stamp_filename:
        candidate = os.path.join(app.config['STAMPS_FOLDER'], submission.stamp_filename)
        if os.path.exists(candidate):
            stamp_filepath = candidate

    try:
        pdf_filename = generate_clientengagement_approval_pdf(
            submission_id,
            stamp_path=stamp_filepath,
            stamp_drawn_path=None,
            approver_name=approver_name,
            approver_email=approver_email,
            approver_position=approver_position
        )
        submission.pdf_filename = pdf_filename
        db.session.commit()
        return jsonify({'success': True, 'pdf_filename': pdf_filename})
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/admin/regenerate-serviceagreement-pdf/<int:submission_id>', methods=['POST'])
@csrf.exempt
@require_admin_or_superadmin
def regenerate_serviceagreement_pdf(submission_id):
    """Regenerate the approval PDF for an already-approved serviceagreement submission"""
    submission = FormSubmission.query.get_or_404(submission_id)

    if submission.form_type != 'serviceagreement':
        return jsonify({'success': False, 'error': 'Submission is not a serviceagreement'}), 400

    # Resolve approver info
    approver_name = None
    approver_email = None
    if submission.approved_by_superadmin:
        sa = SuperAdmin.query.get(submission.approved_by_superadmin)
        if sa:
            approver_name = sa.username
            approver_email = sa.email
    elif submission.approved_by_admin:
        adm = Admin.query.get(submission.approved_by_admin)
        if adm:
            approver_name = f"{adm.first_name} {adm.last_name}".strip()
            approver_email = adm.email

    approver_position = submission.approver_position or 'Company Representative'

    stamp_filepath = None
    if submission.stamp_filename:
        candidate = os.path.join(app.config['STAMPS_FOLDER'], submission.stamp_filename)
        if os.path.exists(candidate):
            stamp_filepath = candidate

    try:
        pdf_filename = f'service_agreement_{submission_id}_approved.pdf'
        pdf_filepath = os.path.join(app.config['PDFS_FOLDER'], pdf_filename)
        result = generate_service_agreement_pdf(
            submission_id,
            stamp_path=stamp_filepath,
            stamp_drawn_path=None,
            output_path=pdf_filepath,
            approver_name=approver_name,
            approver_email=approver_email,
            approver_position=approver_position
        )
        if result:
            submission.pdf_filename = pdf_filename
            submission.final_pdf_filename = pdf_filename
            db.session.commit()
            return jsonify({'success': True, 'pdf_filename': pdf_filename})
        else:
            return jsonify({'success': False, 'error': 'PDF generation failed - check server logs for details'}), 500
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/superadmin/email/create', methods=['GET', 'POST'])
@require_superadmin
def create_email():
    """Add notification email"""
    if request.method == 'POST':
        email = request.form.get('email')
        form_type = request.form.get('form_type', 'all')
        
        if not email or not validate_email(email):
            flash('Please provide a valid email address', 'danger')
            return redirect(url_for('create_email'))
        
        # Check for duplicate
        existing = NotificationEmail.query.filter_by(email=email, form_type=form_type).first()
        if existing:
            flash('This email is already configured for this form type', 'danger')
            return redirect(url_for('create_email'))
        
        superadmin = get_current_superadmin()
        notif_email = NotificationEmail(
            email=email,
            form_type=form_type,
            is_active=True,
            added_by_superadmin=superadmin.id
        )
        db.session.add(notif_email)
        db.session.commit()
        
        flash(f'Notification email {email} added successfully', 'success')
        return redirect(url_for('superadmin_dashboard'))
    
    return render_template('email_form.html',
                         company_name=COMPANY_NAME,
                         support_email=SUPPORT_EMAIL,
                         support_phone=SUPPORT_PHONE)


@app.route('/superadmin/email/<int:email_id>/edit', methods=['GET'])
@require_superadmin
def edit_email(email_id):
    """Edit notification email"""
    email = NotificationEmail.query.get_or_404(email_id)
    
    return render_template('email_form.html',
                         email=email,
                         company_name=COMPANY_NAME,
                         support_email=SUPPORT_EMAIL,
                         support_phone=SUPPORT_PHONE)


@app.route('/superadmin/email/<int:email_id>/update', methods=['POST'])
@require_superadmin
def update_email(email_id):
    """Update notification email"""
    email = NotificationEmail.query.get_or_404(email_id)
    
    email_addr = request.form.get('email')
    form_type = request.form.get('form_type', 'all')
    is_active = request.form.get('is_active') == '1'
    
    if not email_addr or not validate_email(email_addr):
        flash('Please provide a valid email address', 'danger')
        return redirect(url_for('edit_email', email_id=email_id))
    
    # Check for duplicate (but allow same email/form)
    if email_addr != email.email or form_type != email.form_type:
        existing = NotificationEmail.query.filter_by(email=email_addr, form_type=form_type).first()
        if existing:
            flash('This email is already configured for this form type', 'danger')
            return redirect(url_for('edit_email', email_id=email_id))
    
    email.email = email_addr
    email.form_type = form_type
    email.is_active = is_active
    db.session.commit()
    
    flash('Notification email updated successfully', 'success')
    return redirect(url_for('superadmin_dashboard'))


@app.route('/superadmin/email/<int:email_id>/toggle', methods=['POST'])
@require_superadmin
def toggle_email(email_id):
    """Enable/disable notification email"""
    email = NotificationEmail.query.get_or_404(email_id)
    email.is_active = not email.is_active
    db.session.commit()
    
    status = 'enabled' if email.is_active else 'disabled'
    flash(f'Notification email {email.email} has been {status}', 'success')
    return redirect(url_for('superadmin_dashboard'))


@app.route('/superadmin/email/<int:email_id>/delete', methods=['POST'])
@require_superadmin
def delete_email(email_id):
    """Delete notification email"""
    email = NotificationEmail.query.get_or_404(email_id)
    db.session.delete(email)
    db.session.commit()
    
    flash(f'Notification email {email.email} deleted successfully', 'success')
    return redirect(url_for('superadmin_dashboard'))


# ========== COMPANY ADDRESS MANAGEMENT ==========

@app.route('/superadmin/company-address', methods=['GET', 'POST'])
@require_superadmin
def manage_company_address():
    """Manage company address"""
    if request.method == 'POST':
        address = request.form.get('address', '').strip()
        
        if not address:
            flash('Address cannot be empty', 'error')
            return redirect(url_for('manage_company_address'))
        
        # Deactivate previous addresses and create new one
        previous = CompanyAddress.query.filter_by(is_active=True).first()
        if previous:
            previous.is_active = False
        
        new_address = CompanyAddress(
            address=address,
            is_active=True,
            created_by=get_current_superadmin().id
        )
        db.session.add(new_address)
        db.session.commit()
        
        flash('Company address updated successfully', 'success')
        return redirect(url_for('manage_company_address'))
    
    current_address = CompanyAddress.query.filter_by(is_active=True).first()
    all_addresses = CompanyAddress.query.order_by(CompanyAddress.created_at.desc()).all()
    
    return render_template('company_address.html',
                         current_address=current_address,
                         all_addresses=all_addresses,
                         company_name=COMPANY_NAME)


@app.route('/superadmin/company-address/<int:address_id>/delete', methods=['POST'])
@require_superadmin
def delete_company_address(address_id):
    """Delete company address"""
    address = CompanyAddress.query.get_or_404(address_id)
    db.session.delete(address)
    db.session.commit()
    
    flash('Company address deleted successfully', 'success')
    return redirect(url_for('manage_company_address'))


@app.route('/superadmin/company-address/<int:address_id>/activate', methods=['POST'])
@require_superadmin
def activate_company_address(address_id):
    """Activate a company address"""
    address = CompanyAddress.query.get_or_404(address_id)
    
    # Deactivate all other addresses
    CompanyAddress.query.update({CompanyAddress.is_active: False})
    
    # Activate selected address
    address.is_active = True
    db.session.commit()
    
    flash('Company address activated successfully', 'success')
    return redirect(url_for('manage_company_address'))


@app.route('/api/company-address')
def get_company_address():
    """API endpoint to get active company address"""
    address = CompanyAddress.query.filter_by(is_active=True).first()
    if address:
        return jsonify({'address': address.address})
    return jsonify({'address': ''})


@app.route('/init-superadmin')
def init_superadmin():
    """Initialize superadmin (for first setup only)"""
    # Check if superadmin already exists
    if SuperAdmin.query.first():
        return jsonify({'error': 'Superadmin already exists'}), 400
    
    # Create default superadmin
    superadmin = SuperAdmin(
        username='admin',
        password=hash_password('admin123'),
        email='admin@phemediaa.com'
    )
    db.session.add(superadmin)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Superadmin created',
        'credentials': {
            'username': 'admin',
            'password': 'admin123',
            'email': 'admin@phemediaa.com'
        },
        'warning': 'Please change these credentials immediately after login!'
    })



@app.route('/admin/approve-declarationbyemployee/<int:submission_id>', methods=['GET'])
@require_admin_or_superadmin
def show_approval_form_declarationbyemployee(submission_id):
    """Show approval form for employee declaration"""
    submission = FormSubmission.query.get_or_404(submission_id)
    
    # Only allow approving employee declarations with pending_approval status
    if submission.form_type != 'declarationbyemployee' or submission.status != 'pending_approval':
        flash('This declaration cannot be approved', 'danger')
        return redirect(url_for('view_admin_submission', submission_id=submission_id))
    
    current_user = None
    if is_superadmin_logged_in():
        current_user = SuperAdmin.query.get(session.get('superadmin_id'))
        approver_role = 'superadmin'
    else:
        current_user = Admin.query.get(session.get('admin_id'))
        approver_role = 'admin'
    
    return render_template('approve_declarationbyemployee.html',
                         submission=submission,
                         current_user=current_user,
                         approver_role=approver_role)


def generate_declarationbyemployee_approval_pdf(submission_id, stamp_path=None, stamp_drawn_path=None, approver_name=None, approver_position=None):
    """Generate comprehensive PDF for employee declaration form approval"""
    print(f"[generate_declarationbyemployee_approval_pdf] Called with submission_id={submission_id}")
    try:
        submission = FormSubmission.query.get(submission_id)
        if not submission or submission.form_type != 'declarationbyemployee':
            print(f"[generate_declarationbyemployee_approval_pdf] Invalid submission or form type")
            return None
        
        form_data = submission.submitted_data
        
        # Determine output path
        pdf_filename = f'declarationbyemployee_approval_{submission_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        output_path = os.path.join(PDFS_FOLDER, pdf_filename)
        
        print(f"[generate_declarationbyemployee_approval_pdf] HAS_PDF_SUPPORT={HAS_PDF_SUPPORT}")
        if HAS_PDF_SUPPORT:
            try:
                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.set_margins(15, 15, 15)
                pdf.add_page()
                
                # Add standard header with logo and title
                add_pdf_header(pdf, "EMPLOYEE DECLARATION & UNDERTAKING", "Approved & Certified Document")
                
                # ==== EMPLOYEE INFORMATION SECTION ====
                pdf.set_font("helvetica", "B", 12)
                pdf.set_fill_color(52, 152, 219)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 7, "EMPLOYEE INFORMATION", ln=True, fill=True)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(1)

                employee_info = [
                    ("Full Name", sanitize_for_pdf(form_data.get('employee_full_name', 'N/A'))),
                    ("Father's/Parent's Name", sanitize_for_pdf(form_data.get('father_name', 'N/A'))),
                    ("Date of Birth", sanitize_for_pdf(form_data.get('employee_dob', 'N/A'))),
                    ("Residential Address", sanitize_for_pdf(form_data.get('employee_residential_address', 'N/A'))),
                    ("Phone Number", sanitize_for_pdf(form_data.get('employee_phone', 'N/A'))),
                    ("Email Address", sanitize_for_pdf(form_data.get('employee_email', 'N/A'))),
                    ("Position Applied For", sanitize_for_pdf(form_data.get('position_applied', 'N/A'))),
                ]

                for label, value in employee_info:
                    pdf.set_font("helvetica", "B", 10)
                    pdf.cell(55, 5, f"{label}:", ln=False)
                    pdf.set_font("helvetica", "", 10)
                    value_str = str(value)[:100]
                    pdf.cell(0, 5, value_str, ln=True)

                pdf.ln(2)
                
                # ==== UNDERTAKINGS SECTION ====
                pdf.set_font("helvetica", "B", 12)
                pdf.set_fill_color(52, 152, 219)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 7, "UNDERTAKINGS & DECLARATIONS", ln=True, fill=True)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(1)

                undertakings = [
                    (
                        "1. Compliance with Company Rules and Regulations",
                        "comply_rules",
                        "I undertake to strictly obey and comply with all rules, regulations, policies, "
                        "standing orders, instructions, and directives issued by Phemedia Onguard Services "
                        "Ltd from time to time, including but not limited to the company's code of conduct, "
                        "uniform policy, duty roster, reporting procedures, and any amendments thereto.",
                        "I acknowledge and agree to comply with all company rules and regulations",
                    ),
                    (
                        "2. Punctuality and Attendance",
                        "punctuality",
                        "I commit to being punctual for all assigned duties and shifts. Lateness, "
                        "unauthorized absence, or absenteeism without prior approval is unacceptable "
                        "and will attract disciplinary action, including warnings, salary deductions, "
                        "suspension, or termination.",
                        "I commit to punctuality and regular attendance",
                    ),
                    (
                        "3. Maintenance of Good Character and Conduct",
                        "good_conduct",
                        "I pledge to maintain exemplary personal and professional conduct, high moral "
                        "standards, integrity, honesty, discipline, and good behavior at all times. "
                        "I shall not engage in any act that brings disrepute to the company, its "
                        "clients, or the security profession.",
                        "I pledge to maintain exemplary conduct and high moral standards",
                    ),
                    (
                        "4. Notice Period for Resignation / Termination",
                        "notice_period",
                        "I agree to give a minimum of 30 (thirty) days' written notice to the "
                        "management before resigning or terminating my employment. Failure to serve "
                        "the required notice may result in forfeiture of any outstanding benefits, "
                        "salary in lieu of notice deduction, or legal action for damages caused to "
                        "the company.",
                        "I agree to give 30 days' written notice before resignation or termination",
                    ),
                    (
                        "5. Prohibition of Sabotage and Misconduct",
                        "sabotage_prohibition",
                        "I understand and agree that any form of sabotage, including but not limited "
                        "to deliberate damage to company or client property, leakage of confidential "
                        "information, negligence leading to security breach, insubordination, theft, "
                        "fraud, collusion with unauthorized persons, or any act prejudicial to the "
                        "company's interests/security operations, shall result in immediate dismissal "
                        "without notice, forfeiture of all benefits, and possible legal prosecution "
                        "under relevant Nigerian laws (including the Private Guard Companies Act and "
                        "Criminal Code).",
                        "I understand the prohibitions on sabotage and misconduct",
                    ),
                    (
                        "6. Confidentiality and Non-Disclosure",
                        "confidentiality",
                        "I undertake to treat all company information, client details, operational "
                        "strategies, security protocols, and any other sensitive data as strictly "
                        "confidential during and after my employment. I shall not disclose, copy, "
                        "or misuse such information without written permission.",
                        "I agree to maintain strict confidentiality of company and client information",
                    ),
                    (
                        "7. Obedience to Lawful Orders and Assignment",
                        "lawful_orders",
                        "I agree to perform all lawful duties assigned to me diligently, to the best "
                        "of my ability, and in the interest of the company and its clients. I shall "
                        "report any suspicious activity, incident, or irregularity immediately to "
                        "my superior.",
                        "I agree to perform all lawful duties diligently and report irregularities",
                    ),
                    (
                        "8. Uniform, Equipment, and Company Property",
                        "equipment_care",
                        "I undertake to wear the prescribed uniform properly, handle all company-issued "
                        "equipment (e.g., baton, torch, radio, ID card) with care, and return the same "
                        "in good condition upon leaving service. Any loss or damage due to negligence "
                        "will be recovered from my salary/dues.",
                        "I agree to properly maintain all company property and equipment",
                    ),
                ]

                for title, field_key, description, checkbox_label in undertakings:
                    checked = form_data.get(field_key, '') == 'yes'
                    symbol = "[YES]" if checked else "[ ]"
                    pdf.set_font("helvetica", "B", 10)
                    pdf.set_x(pdf.l_margin)
                    pdf.cell(0, 5, title, ln=True)
                    pdf.set_font("helvetica", "", 9)
                    pdf.set_x(pdf.l_margin)
                    pdf.multi_cell(pdf.epw, 4, description)
                    pdf.set_x(pdf.l_margin)
                    pdf.set_font("helvetica", "B", 9)
                    pdf.cell(10, 5, symbol, ln=False)
                    pdf.set_font("helvetica", "", 9)
                    rem_w = pdf.w - pdf.r_margin - pdf.x
                    pdf.multi_cell(rem_w, 5, checkbox_label)
                    pdf.set_x(pdf.l_margin)
                    pdf.ln(1)

                pdf.ln(1)
                
                # ==== SIGNATURES SECTION ====
                pdf.set_font("helvetica", "B", 12)
                pdf.set_fill_color(52, 152, 219)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 7, "EMPLOYEE SIGNATURE & DECLARATION DATE", ln=True, fill=True)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(1)

                pdf.set_font("helvetica", "B", 10)
                pdf.cell(35, 5, "Employee Name:", ln=False)
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 5, sanitize_for_pdf(form_data.get('employee_full_name', 'N/A')), ln=True)
                pdf.ln(1)
                
                # ==== EMPLOYEE PHOTO SECTION ====
                pdf.set_font("helvetica", "B", 12)
                pdf.set_fill_color(52, 152, 219)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 7, "EMPLOYEE PHOTOGRAPH", ln=True, fill=True)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(1)
                
                photo_added = False
                # Try to add the employee passport photo
                try:
                    photo_filename = form_data.get('employee_photograph')
                    if photo_filename:
                        photo_path = os.path.join(UPLOADS_FOLDER, photo_filename)
                        if os.path.exists(photo_path) and os.path.getsize(photo_path) > 0:
                            try:
                                pdf.image(photo_path, x=20, y=pdf.get_y(), w=35, h=45)
                                pdf.ln(47)
                                photo_added = True
                            except Exception as e:
                                print(f"Warning: Could not add passport photo: {str(e)}")
                except Exception as e:
                    print(f"Warning: Error processing passport photo: {str(e)}")
                
                if not photo_added:
                    pdf.set_font("helvetica", "", 10)
                    pdf.cell(0, 5, "[No photograph provided]", ln=True)
                
                pdf.ln(1)
                
                # Employee Signature Image
                add_signatures_to_pdf(pdf, form_data, submission_id, "Employee Signature:")
                
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(15, 5, "Date:", ln=False)
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 5, sanitize_for_pdf(form_data.get('declaration_date', 'N/A')), ln=True)
                decl_place = sanitize_for_pdf(form_data.get('declaration_place', ''))
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(15, 5, "Place:", ln=False)
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 5, decl_place if decl_place and decl_place != 'N/A' else '', ln=True)
                pdf.ln(2)

                # ==== REQUIRED DOCUMENTS ====
                pdf.set_font("helvetica", "B", 12)
                pdf.set_fill_color(52, 152, 219)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 7, "REQUIRED DOCUMENTS", ln=True, fill=True)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(1)

                nin_filename = form_data.get('employee_nin', '')
                if nin_filename:
                    pdf.set_font("helvetica", "B", 9)
                    pdf.cell(8, 5, "[YES]", ln=False)
                    pdf.set_font("helvetica", "", 9)
                    pdf.cell(0, 5, f"Copy of Valid National Identification Number (NIN) - Uploaded: {nin_filename}", ln=True)
                else:
                    pdf.set_font("helvetica", "B", 9)
                    pdf.cell(8, 5, "[ ]", ln=False)
                    pdf.set_font("helvetica", "", 9)
                    pdf.cell(0, 5, "Copy of Valid National Identification Number (NIN) - Not provided", ln=True)
                pdf.ln(2)
                
                # ==== APPROVAL SECTION ====
                pdf.set_font("helvetica", "B", 12)
                pdf.set_fill_color(52, 152, 219)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 7, "APPROVAL & CERTIFICATION", ln=True, fill=True)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(1)

                pdf.set_font("helvetica", "B", 10)
                pdf.cell(35, 5, "Approved By:", ln=False)
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 5, approver_name or 'Company Representative', ln=True)
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(35, 5, "Position:", ln=False)
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 5, approver_position or 'N/A', ln=True)
                pdf.ln(1)

                # Admin stamp (dual: drawn left, uploaded right)
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(0, 5, "Official Approval Stamp & Signature:", ln=True)

                sig_start_y = pdf.get_y()
                sig_x = 20
                sig_w = 50
                sig_h = 25
                any_sig = False

                if stamp_drawn_path and os.path.exists(stamp_drawn_path):
                    try:
                        pdf.set_font("helvetica", "", 9)
                        pdf.text(sig_x, sig_start_y + sig_h + 4, "Drawn Signature:")
                        pdf.image(stamp_drawn_path, x=sig_x, y=sig_start_y, w=sig_w, h=sig_h)
                        any_sig = True
                    except Exception as e:
                        print(f"Error adding drawn admin signature: {str(e)}")

                if stamp_path and os.path.exists(stamp_path):
                    try:
                        upload_x = sig_x + sig_w + 15 if any_sig else sig_x
                        pdf.set_font("helvetica", "", 9)
                        pdf.text(upload_x, sig_start_y + sig_h + 4, "Uploaded Stamp/Signature:")
                        pdf.image(stamp_path, x=upload_x, y=sig_start_y, w=sig_w, h=sig_h)
                        any_sig = True
                    except Exception as e:
                        print(f"Error adding uploaded admin signature: {str(e)}")

                if any_sig:
                    pdf.ln(sig_h + 10)
                else:
                    pdf.ln(18)

                approval_date = submission.approved_at if submission.approved_at else datetime.now()
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 5, f"Approval Date: {approval_date.strftime('%d %B %Y at %H:%M:%S')}", ln=True)
                pdf.ln(2)
                
                # ==== FOOTER ====
                pdf.set_draw_color(189, 195, 199)
                pdf.line(12, pdf.get_y(), 198, pdf.get_y())
                pdf.ln(2)
                
                pdf.set_font("helvetica", "", 8)
                pdf.set_text_color(127, 140, 141)
                footer_text = f"This Employee Declaration & Undertaking has been reviewed, approved, and certified by {COMPANY_NAME}. Reference #: {submission_id} | Generated: {datetime.now().strftime('%d %b %Y at %H:%M:%S')} | This document is confidential and property of {COMPANY_NAME}."
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(pdf.epw, 3, footer_text, align="C")
                
                # Save PDF
                pdf.output(output_path)
                print(f"[generate_declarationbyemployee_approval_pdf] PDF saved to {output_path}")
                
                return pdf_filename
                
            except Exception as e:
                print(f"[generate_declarationbyemployee_approval_pdf] Error generating PDF: {str(e)}")
                return None
        else:
            print(f"[generate_declarationbyemployee_approval_pdf] HAS_PDF_SUPPORT is False, creating placeholder")
            # Create empty placeholder file
            with open(output_path, 'w') as f:
                f.write(f"Employee Declaration & Undertaking - Approval Document (Reference: {submission_id})")
            return pdf_filename
            
    except Exception as e:
        print(f"[generate_declarationbyemployee_approval_pdf] Unexpected error: {str(e)}")
        return None


@app.route('/admin/approve-declarationbyemployee/<int:submission_id>', methods=['POST'])
@require_admin_or_superadmin
def process_approval_declarationbyemployee(submission_id):
    """Process approval for employee declaration"""
    print(f"\n[DEBUG] process_approval_declarationbyemployee called with submission_id={submission_id}")
    submission = FormSubmission.query.get_or_404(submission_id)
    
    # Validate submission
    if submission.form_type != 'declarationbyemployee' or submission.status != 'pending_approval':
        flash('This declaration cannot be approved', 'danger')
        return redirect(url_for('view_admin_submission', submission_id=submission_id))
    
    approver_name = request.form.get('approver_name', '').strip()
    approver_email = request.form.get('approver_email', '').strip()
    approver_position = request.form.get('approver_position', '').strip()
    signature_data = request.form.get('approvalSignatureData', '').strip()       # uploaded
    signature_data_drawn = request.form.get('approvalSignatureData_drawn', '').strip()  # drawn

    if not approver_name:
        return jsonify({'success': False, 'message': 'Approver name is required'}), 400

    if not approver_email or not validate_email(approver_email):
        return jsonify({'success': False, 'message': 'Valid approver email is required'}), 400

    if not approver_position:
        return jsonify({'success': False, 'message': 'Approver position/title is required'}), 400

    if not signature_data and not signature_data_drawn:
        return jsonify({'success': False, 'message': 'Signature is required'}), 400

    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        stamp_filepath = None
        stamp_drawn_filepath = None
        filename = None

        # Save uploaded signature
        if signature_data:
            sig_bytes = base64.b64decode(signature_data.split(',')[1] if ',' in signature_data else signature_data)
            filename = secure_filename(f'approval_signature_{submission_id}_{timestamp}.png')
            stamp_filepath = os.path.join(app.config['STAMPS_FOLDER'], filename)
            with open(stamp_filepath, 'wb') as f:
                f.write(sig_bytes)

        # Save drawn signature
        if signature_data_drawn:
            sig_bytes_drawn = base64.b64decode(signature_data_drawn.split(',')[1] if ',' in signature_data_drawn else signature_data_drawn)
            filename_drawn = secure_filename(f'approval_sig_drawn_{submission_id}_{timestamp}.png')
            stamp_drawn_filepath = os.path.join(app.config['STAMPS_FOLDER'], filename_drawn)
            with open(stamp_drawn_filepath, 'wb') as f:
                f.write(sig_bytes_drawn)
            if not filename:
                filename = filename_drawn

        # Update submission
        if is_superadmin_logged_in():
            submission.approved_by_superadmin = session.get('superadmin_id')
        else:
            submission.approved_by_admin = session.get('admin_id')

        submission.status = 'approved'
        submission.approved_at = datetime.now()
        submission.approver_position = approver_position
        if filename:
            submission.stamp_filename = filename

        # Generate approval PDF
        pdf_filename = generate_declarationbyemployee_approval_pdf(
            submission_id,
            stamp_path=stamp_filepath,
            stamp_drawn_path=stamp_drawn_filepath,
            approver_name=approver_name,
            approver_position=approver_position
        )
        if pdf_filename:
            submission.pdf_filename = pdf_filename
            print(f"[process_approval_declarationbyemployee] PDF generated: {pdf_filename}")
        else:
            print(f"[process_approval_declarationbyemployee] PDF generation failed")

        db.session.commit()
        
        # Send emails to employee and approver
        employee_email = submission.user_email
        
        # Email to employee with PDF attachment
        employee_subject = f'Employee Declaration & Undertaking Approved - {COMPANY_NAME}'
        employee_html = f"""
        <html>
        <body style="font-family: 'Poppins', 'Segoe UI', sans-serif; color: #333;">
            <h2>Your Employee Declaration & Undertaking Has Been Approved</h2>
            <p>Dear Employee,</p>
            <p>Your Employee Declaration & Undertaking has been reviewed and approved by {approver_name}, {approver_position} at {COMPANY_NAME}.</p>
            <p><strong>Approval Date:</strong> {datetime.now().strftime('%d %B %Y at %H:%M:%S')}</p>
            <p><strong>Approved By:</strong> {approver_name}, {approver_position}</p>
            <p>Your declaration is now complete and in effect. A copy of your approved declaration is attached to this email for your records. If you have any questions, please contact us at {SUPPORT_EMAIL}.</p>
            <p>Best regards,<br>{COMPANY_NAME}</p>
        </body>
        </html>
        """
        
        # Send email with PDF attachment if available
        if pdf_filename:
            pdf_path = os.path.join(PDFS_FOLDER, pdf_filename)
            send_email_with_attachment(employee_email, employee_subject, employee_html, pdf_path, 'Employee_Declaration_Approval.pdf')
        else:
            send_email(employee_email, employee_subject, employee_html)
        
        # Email to approver
        approver_subject = f'Employee Declaration & Undertaking - Approval Recorded'
        approver_html = f"""
        <html>
        <body style="font-family: 'Poppins', 'Segoe UI', sans-serif; color: #333;">
            <h2>Declaration Approval Recorded</h2>
            <p>Dear {approver_name},</p>
            <p>This is to confirm that you have approved the Employee Declaration & Undertaking for employee <strong>{submission.submitted_data.get('employee_full_name', 'N/A')}</strong>.</p>
            <p><strong>Employee Email:</strong> {submission.submitted_data.get('employee_email', 'N/A')}</p>
            <p><strong>Position:</strong> {submission.submitted_data.get('position_applied', 'N/A')}</p>
            <p><strong>Approval Date & Time:</strong> {datetime.now().strftime('%d %B %Y at %H:%M:%S')}</p>
            <p>Best regards,<br>{COMPANY_NAME} System</p>
        </body>
        </html>
        """
        send_email(approver_email, approver_subject, approver_html)
        
        return jsonify({'success': True, 'message': 'Declaration approved successfully'})
        
    except Exception as e:
        print(f"Error processing approval: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error approving declaration: {str(e)}'}), 500


def generate_guarantorundertaking_approval_pdf(submission_id, stamp_path=None, stamp_drawn_path=None, approver_name=None, approver_position=None):
    """Generate PDF for guarantor undertaking form approval"""
    print(f"[generate_guarantorundertaking_approval_pdf] Called with submission_id={submission_id}")
    try:
        submission = FormSubmission.query.get(submission_id)
        if not submission or submission.form_type != 'guarantorundertaking':
            print(f"[generate_guarantorundertaking_approval_pdf] Invalid submission or form type")
            return None

        form_data = submission.submitted_data

        # Determine output path
        pdf_filename = f'guarantorundertaking_approval_{submission_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        output_path = os.path.join(PDFS_FOLDER, pdf_filename)

        print(f"[generate_guarantorundertaking_approval_pdf] HAS_PDF_SUPPORT={HAS_PDF_SUPPORT}")
        if HAS_PDF_SUPPORT:
            try:
                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.set_margins(15, 15, 15)
                pdf.add_page()

                add_pdf_header(pdf, "GUARANTOR'S UNDERTAKING", "Approved & Certified Document")

                # ==== APPLICANT'S DETAILS ====
                pdf.set_font("helvetica", "B", 12)
                pdf.set_fill_color(52, 152, 219)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 7, "APPLICANT'S DETAILS", ln=True, fill=True)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(1)

                applicant_rows = [
                    ("Full Name",           sanitize_for_pdf(form_data.get('applicant_full_name', 'N/A'))),
                    ("Position Applied For", sanitize_for_pdf(form_data.get('applicant_position', 'N/A'))),
                    ("Date of Birth",        sanitize_for_pdf(form_data.get('applicant_dob', 'N/A'))),
                    ("Phone Number",         sanitize_for_pdf(form_data.get('applicant_phone', 'N/A'))),
                    ("Email Address",        sanitize_for_pdf(form_data.get('applicant_email', 'N/A'))),
                ]
                for label, value in applicant_rows:
                    pdf.set_font("helvetica", "B", 10)
                    pdf.cell(55, 5, f"{label}:", ln=False)
                    pdf.set_font("helvetica", "", 10)
                    pdf.cell(0, 5, value, ln=True)

                # Residential Address (may be long)
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(55, 5, "Residential Address:", ln=False)
                pdf.set_font("helvetica", "", 10)
                rem_w = pdf.w - pdf.r_margin - pdf.x
                pdf.multi_cell(rem_w, 5, sanitize_for_pdf(form_data.get('applicant_address', 'N/A')))
                pdf.set_x(pdf.l_margin)
                pdf.ln(2)

                # ==== GUARANTOR'S DETAILS ====
                pdf.set_font("helvetica", "B", 12)
                pdf.set_fill_color(52, 152, 219)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 7, "GUARANTOR'S DETAILS", ln=True, fill=True)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(1)

                guarantor_title = sanitize_for_pdf(form_data.get('guarantor_title', ''))
                guarantor_name  = sanitize_for_pdf(form_data.get('guarantor_full_name', 'N/A'))
                full_name_val   = f"{guarantor_title} {guarantor_name}".strip() if guarantor_title else guarantor_name

                guarantor_rows = [
                    ("Title",                    sanitize_for_pdf(form_data.get('guarantor_title', 'N/A'))),
                    ("Full Name",                full_name_val),
                    ("Date of Birth / Age",      sanitize_for_pdf(form_data.get('guarantor_dob', 'N/A'))),
                    ("Occupation / Job Title",   sanitize_for_pdf(form_data.get('guarantor_occupation', 'N/A'))),
                    ("Place of Work / Org.",     sanitize_for_pdf(form_data.get('guarantor_workplace', 'N/A'))),
                    ("Office Phone Number",      sanitize_for_pdf(form_data.get('guarantor_work_phone', 'N/A'))),
                    ("Phone Numbers",            sanitize_for_pdf(form_data.get('guarantor_phone', 'N/A'))),
                    ("Email Address",            sanitize_for_pdf(form_data.get('guarantor_email', 'N/A'))),
                    ("Relationship to Applicant", sanitize_for_pdf(form_data.get('guarantor_relationship', 'N/A'))),
                    ("Known Applicant For",      sanitize_for_pdf(str(form_data.get('known_duration', 'N/A'))) + " year(s)"),
                ]
                for label, value in guarantor_rows:
                    pdf.set_font("helvetica", "B", 10)
                    pdf.cell(55, 5, f"{label}:", ln=False)
                    pdf.set_font("helvetica", "", 10)
                    pdf.cell(0, 5, value, ln=True)

                # Office Address
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(55, 5, "Office Address:", ln=False)
                pdf.set_font("helvetica", "", 10)
                rem_w = pdf.w - pdf.r_margin - pdf.x
                pdf.multi_cell(rem_w, 5, sanitize_for_pdf(form_data.get('guarantor_office_address', 'N/A')))
                pdf.set_x(pdf.l_margin)

                # Residential Address
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(55, 5, "Residential Address:", ln=False)
                pdf.set_font("helvetica", "", 10)
                rem_w = pdf.w - pdf.r_margin - pdf.x
                pdf.multi_cell(rem_w, 5, sanitize_for_pdf(form_data.get('guarantor_residential_address', 'N/A')))
                pdf.set_x(pdf.l_margin)
                pdf.ln(2)

                # ==== DECLARATION & UNDERTAKING ====
                pdf.set_font("helvetica", "B", 12)
                pdf.set_fill_color(52, 152, 219)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 7, "DECLARATION & UNDERTAKING", ln=True, fill=True)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(1)

                # Capacity
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(0, 5, "Capacity in which you know the applicant:", ln=True)
                pdf.set_font("helvetica", "", 9)
                pdf.multi_cell(pdf.epw, 4, sanitize_for_pdf(form_data.get('guarantor_capacity', 'N/A')))
                pdf.set_x(pdf.l_margin)
                pdf.ln(2)

                # Declaration checkbox status
                decl_checked = str(form_data.get('declaration', '')).lower() == 'yes'
                decl_mark = "[YES]" if decl_checked else "[ ]"

                declarations = [
                    ("Character Declaration",
                     "I attest that the applicant is of good character, honest, reliable, and fit for employment as a Security Guard/Staff/Driver with Phemedia Onguard Services Ltd."),
                    ("Conduct Declaration",
                     "I have no reason to believe the applicant would engage in misconduct, theft, or behavior detrimental to the company."),
                    ("Guarantor Responsibility",
                     "I agree to serve as guarantor and accept responsibility as required by the company."),
                    ("Information Authenticity",
                     "I confirm all provided information and attached documents are true and authentic. Any false declaration may lead to consequences."),
                ]
                for decl_title, decl_text in declarations:
                    pdf.set_font("helvetica", "B", 9)
                    pdf.cell(10, 5, decl_mark, ln=False)
                    pdf.set_font("helvetica", "B", 9)
                    pdf.cell(0, 5, decl_title + ":", ln=True)
                    pdf.set_font("helvetica", "", 9)
                    pdf.set_x(pdf.l_margin + 10)
                    rem_w = pdf.w - pdf.r_margin - pdf.x
                    pdf.multi_cell(rem_w, 4, decl_text)
                    pdf.set_x(pdf.l_margin)
                    pdf.ln(1)
                pdf.ln(1)

                # ==== ATTACHMENTS ====
                pdf.set_font("helvetica", "B", 12)
                pdf.set_fill_color(52, 152, 219)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 7, "ATTACHMENTS", ln=True, fill=True)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(1)

                passport_photo = form_data.get('guarantor_passport_photo', '')
                national_id    = form_data.get('guarantor_national_id', '')
                passport_status = "Uploaded" if passport_photo else "Not uploaded"
                national_id_status = "Uploaded" if national_id else "Not uploaded"

                pdf.set_font("helvetica", "B", 10)
                pdf.cell(55, 5, "Passport Photograph:", ln=False)
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 5, passport_status, ln=True)

                pdf.set_font("helvetica", "B", 10)
                pdf.cell(55, 5, "NIN / Valid ID:", ln=False)
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 5, national_id_status, ln=True)
                pdf.ln(2)

                # ==== GUARANTOR SIGNATURE ====
                pdf.set_font("helvetica", "B", 12)
                pdf.set_fill_color(52, 152, 219)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 7, "GUARANTOR SIGNATURE", ln=True, fill=True)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(1)

                add_signatures_to_pdf(pdf, form_data, submission_id, "Guarantor Signature:")

                sig_date = sanitize_for_pdf(form_data.get('signature_date', ''))
                sig_place = sanitize_for_pdf(form_data.get('signature_location', ''))
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(15, 5, "Date:", ln=False)
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 5, sig_date if sig_date else 'N/A', ln=True)
                if sig_place:
                    pdf.set_font("helvetica", "B", 10)
                    pdf.cell(15, 5, "Place:", ln=False)
                    pdf.set_font("helvetica", "", 10)
                    pdf.cell(0, 5, sig_place, ln=True)
                pdf.ln(2)

                # ==== APPROVAL SECTION ====
                pdf.set_font("helvetica", "B", 12)
                pdf.set_fill_color(52, 152, 219)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 7, "OFFICIAL APPROVAL & CERTIFICATION", ln=True, fill=True)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(1)

                pdf.set_font("helvetica", "B", 10)
                pdf.cell(35, 5, "Approved By:", ln=False)
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 5, sanitize_for_pdf(approver_name or 'Company Representative'), ln=True)

                pdf.set_font("helvetica", "B", 10)
                pdf.cell(35, 5, "Position:", ln=False)
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 5, sanitize_for_pdf(approver_position or 'N/A'), ln=True)
                pdf.ln(1)

                # Approval signature(s) — drawn left, uploaded right, matching backgroundcheck pattern
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(0, 5, "Official Approval Stamp & Signature:", ln=True)

                sig_start_y = pdf.get_y()
                sig_x = pdf.l_margin
                sig_w = 50
                sig_h = 25
                any_sig = False

                if stamp_drawn_path and os.path.exists(stamp_drawn_path):
                    try:
                        pdf.set_font("helvetica", "", 9)
                        pdf.text(sig_x, sig_start_y + sig_h + 4, "Drawn Signature:")
                        pdf.image(stamp_drawn_path, x=sig_x, y=sig_start_y, w=sig_w, h=sig_h)
                        any_sig = True
                    except Exception as e:
                        print(f"Error adding drawn admin signature: {str(e)}")

                if stamp_path and os.path.exists(stamp_path):
                    try:
                        upload_x = sig_x + sig_w + 15 if any_sig else sig_x
                        pdf.set_font("helvetica", "", 9)
                        pdf.text(upload_x, sig_start_y + sig_h + 4, "Uploaded Stamp/Signature:")
                        pdf.image(stamp_path, x=upload_x, y=sig_start_y, w=sig_w, h=sig_h)
                        any_sig = True
                    except Exception as e:
                        print(f"Error adding uploaded admin signature: {str(e)}")

                if any_sig:
                    pdf.ln(sig_h + 10)
                else:
                    pdf.ln(5)

                approval_date = submission.approved_at if submission.approved_at else datetime.now()
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 5, f"Approval Date: {approval_date.strftime('%d %B %Y at %H:%M:%S')}", ln=True)
                pdf.ln(3)

                # ==== FOOTER ====
                pdf.set_font("helvetica", "", 8)
                pdf.set_text_color(100, 100, 100)
                footer_text = (
                    f"Document Reference: GU-{submission_id}  |  "
                    f"Generated: {datetime.now().strftime('%d %B %Y at %H:%M:%S')}  |  "
                    "This is an official document. Please keep a copy for your records."
                )
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(pdf.epw, 3, footer_text, align="C")

                pdf.output(output_path)
                print(f"[generate_guarantorundertaking_approval_pdf] PDF created successfully at {output_path}")
                return pdf_filename

            except Exception as e:
                print(f"[generate_guarantorundertaking_approval_pdf] Error creating PDF: {str(e)}")
                return None
        else:
            print(f"[generate_guarantorundertaking_approval_pdf] PDF support not available")
            return None

    except Exception as e:
        print(f"Error in generate_guarantorundertaking_approval_pdf: {str(e)}")
        return None


@app.route('/admin/approve-guarantorundertaking/<int:submission_id>', methods=['GET'])
@require_admin_or_superadmin
def show_approval_form_guarantorundertaking(submission_id):
    """Show approval form for guarantor undertaking"""
    submission = FormSubmission.query.get_or_404(submission_id)
    
    # Only allow approving guarantor undertakings with pending_approval status
    if submission.form_type != 'guarantorundertaking' or submission.status != 'pending_approval':
        flash('This undertaking cannot be approved', 'danger')
        return redirect(url_for('view_admin_submission', submission_id=submission_id))
    
    current_user = None
    if is_superadmin_logged_in():
        current_user = SuperAdmin.query.get(session.get('superadmin_id'))
        approver_role = 'superadmin'
    else:
        current_user = Admin.query.get(session.get('admin_id'))
        approver_role = 'admin'
    
    return render_template('approve_guarantorundertaking.html',
                         submission=submission,
                         current_user=current_user,
                         approver_role=approver_role)


@app.route('/admin/approve-guarantorundertaking/<int:submission_id>', methods=['POST'])
@require_admin_or_superadmin
def process_approval_guarantorundertaking(submission_id):
    """Process approval for guarantor undertaking"""
    print(f"\n[DEBUG] process_approval_guarantorundertaking called with submission_id={submission_id}")
    submission = FormSubmission.query.get_or_404(submission_id)
    
    # Validate submission
    if submission.form_type != 'guarantorundertaking' or submission.status != 'pending_approval':
        flash('This undertaking cannot be approved', 'danger')
        return redirect(url_for('view_admin_submission', submission_id=submission_id))
    
    approver_name = request.form.get('approver_name', '').strip()
    approver_email = request.form.get('approver_email', '').strip()
    approver_position = request.form.get('approver_position', '').strip()
    signature_data = request.form.get('signature_data', '').strip()             # uploaded
    signature_data_drawn = request.form.get('signature_data_drawn', '').strip() # drawn

    if not approver_name:
        flash('Approver name is required', 'danger')
        return redirect(url_for('show_approval_form_guarantorundertaking', submission_id=submission_id))

    if not approver_email or not validate_email(approver_email):
        flash('Valid approver email is required', 'danger')
        return redirect(url_for('show_approval_form_guarantorundertaking', submission_id=submission_id))

    if not approver_position:
        flash('Approver position/title is required', 'danger')
        return redirect(url_for('show_approval_form_guarantorundertaking', submission_id=submission_id))

    if not signature_data and not signature_data_drawn:
        flash('Signature is required', 'danger')
        return redirect(url_for('show_approval_form_guarantorundertaking', submission_id=submission_id))

    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        stamp_filepath = None
        stamp_drawn_filepath = None
        filename = None

        # Save uploaded signature
        if signature_data:
            sig_bytes = base64.b64decode(signature_data.split(',')[1] if ',' in signature_data else signature_data)
            filename = secure_filename(f'approval_signature_{submission_id}_{timestamp}.png')
            stamp_filepath = os.path.join(app.config['STAMPS_FOLDER'], filename)
            with open(stamp_filepath, 'wb') as f:
                f.write(sig_bytes)

        # Save drawn signature
        if signature_data_drawn:
            sig_bytes_drawn = base64.b64decode(signature_data_drawn.split(',')[1] if ',' in signature_data_drawn else signature_data_drawn)
            filename_drawn = secure_filename(f'approval_sig_drawn_{submission_id}_{timestamp}.png')
            stamp_drawn_filepath = os.path.join(app.config['STAMPS_FOLDER'], filename_drawn)
            with open(stamp_drawn_filepath, 'wb') as f:
                f.write(sig_bytes_drawn)
            if not filename:
                filename = filename_drawn

        # Update submission
        if is_superadmin_logged_in():
            submission.approved_by_superadmin = session.get('superadmin_id')
        else:
            submission.approved_by_admin = session.get('admin_id')

        submission.status = 'approved'
        submission.approved_at = datetime.now()
        submission.approver_position = approver_position
        if filename:
            submission.stamp_filename = filename

        # Generate approval PDF
        pdf_filename = generate_guarantorundertaking_approval_pdf(
            submission_id,
            stamp_path=stamp_filepath,
            stamp_drawn_path=stamp_drawn_filepath,
            approver_name=approver_name,
            approver_position=approver_position
        )
        if pdf_filename:
            submission.pdf_filename = pdf_filename
            print(f"[process_approval_guarantorundertaking] PDF generated: {pdf_filename}")
        else:
            print(f"[process_approval_guarantorundertaking] PDF generation failed")
        
        db.session.commit()
        
        # Send emails to guarantor and approver
        guarantor_email = submission.user_email
        
        # Email to guarantor with PDF attachment
        guarantor_subject = f"Guarantor's Undertaking Approved - {COMPANY_NAME}"
        guarantor_html = f"""
        <html>
        <body style="font-family: 'Poppins', 'Segoe UI', sans-serif; color: #333;">
            <h2>Your Guarantor's Undertaking Has Been Approved</h2>
            <p>Dear Guarantor,</p>
            <p>Your Guarantor's Undertaking has been reviewed and approved by {approver_name}, {approver_position} at {COMPANY_NAME}.</p>
            <p><strong>Approval Date:</strong> {datetime.now().strftime('%d %B %Y at %H:%M:%S')}</p>
            <p><strong>Approved By:</strong> {approver_name}, {approver_position}</p>
            <p>Your undertaking is now complete and in effect. A copy of your approved undertaking is attached to this email for your records. If you have any questions, please contact us at {SUPPORT_EMAIL}.</p>
            <p>Best regards,<br>{COMPANY_NAME}</p>
        </body>
        </html>
        """
        
        # Send email with PDF attachment if available
        if pdf_filename:
            pdf_path = os.path.join(PDFS_FOLDER, pdf_filename)
            send_email_with_attachment(guarantor_email, guarantor_subject, guarantor_html, pdf_path, 'Guarantor_Undertaking_Approval.pdf')
        else:
            send_email(guarantor_email, guarantor_subject, guarantor_html)
        
        # Email to approver
        approver_subject = f"Guarantor's Undertaking - Approval Recorded"
        approver_html = f"""
        <html>
        <body style="font-family: 'Poppins', 'Segoe UI', sans-serif; color: #333;">
            <h2>Undertaking Approval Recorded</h2>
            <p>Dear {approver_name},</p>
            <p>This is to confirm that you have approved the Guarantor's Undertaking for <strong>{submission.submitted_data.get('guarantor_full_name', 'N/A')}</strong>.</p>
            <p><strong>Guarantor Email:</strong> {submission.submitted_data.get('guarantor_email', 'N/A')}</p>
            <p><strong>Client Name:</strong> {submission.submitted_data.get('client_name', 'N/A')}</p>
            <p><strong>Approval Date & Time:</strong> {datetime.now().strftime('%d %B %Y at %H:%M:%S')}</p>
            <p>Best regards,<br>{COMPANY_NAME} System</p>
        </body>
        </html>
        """
        send_email(approver_email, approver_subject, approver_html)
        
        flash("Guarantor's Undertaking approved successfully. A confirmation email has been sent.", 'success')
        return redirect(url_for('admin_dashboard'))
        
    except Exception as e:
        print(f"Error processing approval: {str(e)}")
        db.session.rollback()
        flash(f'Error approving undertaking: {str(e)}', 'danger')
        return redirect(url_for('show_approval_form_guarantorundertaking', submission_id=submission_id))


# ==================== OIL & GAS APPROVAL ROUTES ====================

@app.route('/admin/approve-oilgasservicerequest/<int:submission_id>', methods=['GET'])
@require_admin_or_superadmin
def show_approval_form_oilgasservicerequest(submission_id):
    """Show approval form for oil & gas service request"""
    submission = FormSubmission.query.get_or_404(submission_id)
    
    # Only allow approving oil & gas requests with pending_approval status
    if submission.form_type != 'oilgasservicerequest' or submission.status != 'pending_approval':
        flash('This request cannot be approved', 'danger')
        return redirect(url_for('view_admin_submission', submission_id=submission_id))
    
    current_user = SuperAdmin.query.get(session.get('superadmin_id'))
    return render_template('approve_oilgasservicerequest.html',
                         submission=submission,
                         current_user=current_user)


@app.route('/admin/approve-oilgasservicerequest/<int:submission_id>', methods=['POST'])
@require_admin_or_superadmin
def process_approval_oilgasservicerequest(submission_id):
    """Process approval for oil & gas service request"""
    submission = FormSubmission.query.get_or_404(submission_id)
    
    # Validate submission
    if submission.form_type != 'oilgasservicerequest' or submission.status != 'pending_approval':
        flash('This request cannot be approved', 'danger')
        return redirect(url_for('view_admin_submission', submission_id=submission_id))
    
    approver_name = request.form.get('approver_name', '').strip()
    approver_email = request.form.get('approver_email', '').strip()
    approver_position = request.form.get('approver_position', '').strip()
    signature_data = request.form.get('signature_data', '').strip()
    
    if not approver_name:
        flash('Approver name is required', 'danger')
        return redirect(url_for('show_approval_form_oilgasservicerequest', submission_id=submission_id))
    
    if not approver_email or not validate_email(approver_email):
        flash('Valid approver email is required', 'danger')
        return redirect(url_for('show_approval_form_oilgasservicerequest', submission_id=submission_id))
    
    if not approver_position:
        flash('Approver position/title is required', 'danger')
        return redirect(url_for('show_approval_form_oilgasservicerequest', submission_id=submission_id))
    
    if not signature_data:
        flash('Signature is required', 'danger')
        return redirect(url_for('show_approval_form_oilgasservicerequest', submission_id=submission_id))
    
    try:
        # Update submission status
        submission.status = 'approved'
        submission.approval_status = 'approved'
        submission.approver_name = approver_name
        submission.approver_email = approver_email
        submission.approver_position = approver_position
        
        # Save signature
        if signature_data.startswith('data:image'):
            import base64
            header, encoded = signature_data.split(',', 1)
            signature_file = base64.b64decode(encoded)
            sig_filename = f'oilgas_approval_sig_{submission_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            sig_path = os.path.join(app.config['UPLOAD_FOLDER'], sig_filename)
            with open(sig_path, 'wb') as f:
                f.write(signature_file)
            submission.signature_filename = sig_filename
        
        # Generate approval PDF
        pdf_filename = generate_oilgasservicerequest_approval_pdf(submission_id, approver_name, approver_position)
        if pdf_filename:
            submission.pdf_filename = pdf_filename
            submission.final_pdf_filename = pdf_filename
        
        db.session.commit()
        
        # Send approval emails
        client_email = submission.submitted_data.get('client_email') or submission.user_email
        company_name = submission.submitted_data.get('company_name', 'N/A')
        
        if client_email and '@' in client_email:
            client_subject = 'Your Oil & Gas Service Request - Approved'
            client_html = f"""
            <html>
            <body style="font-family: 'Poppins', 'Segoe UI', sans-serif; color: #333;">
                <h2>Service Request Approval</h2>
                <p>Dear {submission.submitted_data.get('contact_person', 'Valued Client')},</p>
                <p>We are pleased to inform you that your Oil & Gas Service Request has been <strong>APPROVED</strong>.</p>
                <p><strong>Company:</strong> {company_name}</p>
                <p><strong>Service Required:</strong> {submission.submitted_data.get('service_required', 'N/A')}</p>
                <p><strong>Location:</strong> {submission.submitted_data.get('location', 'N/A')}</p>
                <p><strong>Approval Date:</strong> {datetime.now().strftime('%d %B %Y at %H:%M:%S')}</p>
                <p><strong>Approved By:</strong> {approver_name} ({approver_position})</p>
                <p>The approved service request document has been attached to this email.</p>
                <p>We will contact you shortly to discuss next steps and deployment details.</p>
                <p>Best regards,<br>{COMPANY_NAME}</p>
            </body>
            </html>
            """
            if pdf_filename:
                pdf_path = os.path.join(PDFS_FOLDER, pdf_filename)
                send_email_with_attachment(client_email, client_subject, client_html, pdf_path, 'Oil_Gas_Service_Approval.pdf')
            else:
                send_email(client_email, client_subject, client_html)
        
        if approver_email:
            approver_subject = 'Oil & Gas Service Request - Approval Recorded'
            approver_html = f"""
            <html>
            <body style="font-family: 'Poppins', 'Segoe UI', sans-serif; color: #333;">
                <h2>Service Request Approval Recorded</h2>
                <p>Dear {approver_name},</p>
                <p>This is to confirm that you have approved the Oil & Gas Service Request from <strong>{company_name}</strong>.</p>
                <p><strong>Contact Email:</strong> {client_email or 'N/A'}</p>
                <p><strong>Service Required:</strong> {submission.submitted_data.get('service_required', 'N/A')}</p>
                <p><strong>Approval Date & Time:</strong> {datetime.now().strftime('%d %B %Y at %H:%M:%S')}</p>
                <p>Best regards,<br>{COMPANY_NAME} System</p>
            </body>
            </html>
            """
            send_email(approver_email, approver_subject, approver_html)
        
        flash('Service request approved successfully!', 'success')
        return redirect(url_for('view_admin_submission', submission_id=submission_id))
        
    except Exception as e:
        print(f"Error approving oil & gas request: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        flash(f'Error approving request: {str(e)}', 'danger')
        return redirect(url_for('show_approval_form_oilgasservicerequest', submission_id=submission_id))


def generate_oilgasservicerequest_approval_pdf(submission_id, approver_name=None, approver_position=None):
    """Generate full-content PDF for oil & gas service request (all form sections)"""
    try:
        submission = FormSubmission.query.get(submission_id)
        if not submission:
            return None

        form_data = submission.submitted_data
        approval_date = datetime.now()

        is_approval = bool(approver_name)
        prefix = 'oilgas_approval' if is_approval else 'oilgas_signed'
        pdf_filename = f'{prefix}_{submission_id}_{approval_date.strftime("%Y%m%d_%H%M%S")}.pdf'
        pdf_path = os.path.join(PDFS_FOLDER, pdf_filename)

        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()

        title = "OIL & GAS SERVICE REQUEST - APPROVED" if is_approval else "OIL & GAS SECTOR SERVICE REQUEST"
        subtitle = "Approved & Certified Document" if is_approval else "Client Service Request Form"
        add_pdf_header(pdf, title, subtitle)

        # ---- helpers ----
        def section_header(text):
            pdf.set_font("helvetica", "B", 12)
            pdf.set_fill_color(52, 152, 219)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(0, 7, text, ln=True, fill=True)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(1)

        def sub_section_header(text):
            pdf.set_font("helvetica", "B", 10)
            pdf.set_fill_color(52, 73, 94)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(0, 6, text, ln=True, fill=True)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(1)

        def info_row(label, value, lw=70):
            pdf.set_font("helvetica", "B", 9)
            pdf.cell(lw, 5, f"{label}:", ln=False)
            pdf.set_font("helvetica", "", 9)
            pdf.cell(0, 5, str(value)[:90] if value else 'N/A', ln=True)

        def info_multiline(label, value):
            pdf.set_font("helvetica", "B", 9)
            pdf.cell(0, 5, f"{label}:", ln=True)
            pdf.set_font("helvetica", "", 9)
            pdf.multi_cell(0, 4, str(value) if value else 'N/A')
            pdf.ln(1)

        # ================================================================
        # 1. CLIENT INFORMATION
        # ================================================================
        section_header("CLIENT INFORMATION")
        info_row("Company Name", form_data.get('company_name'))
        info_row("Contact Person", form_data.get('contact_person'))
        info_row("Position/Title", form_data.get('position_title'))
        info_row("Email Address", form_data.get('client_email'))
        info_row("Phone Number", form_data.get('client_phone') or form_data.get('phone'))
        pdf.ln(2)

        # ================================================================
        # 2. SERVICE REQUIREMENTS
        # ================================================================
        section_header("SERVICE REQUIREMENTS")

        sub_section_header("1. Document Verification & Background Checks")
        info_row("Proof of Product", form_data.get('proof_of_product'))
        info_row("Bill of Lading", form_data.get('bill_of_lading'))
        info_row("Charterer Background Check", form_data.get('charterer_background'))
        pdf.ln(2)

        sub_section_header("2. Equipment & Vessel Rentals")
        swamp_rig = form_data.get('swamp_drilling_rig', 'no')
        info_row("Swamp Drilling Rig for Lease", "[YES]" if swamp_rig == 'yes' else "[NO]")
        if form_data.get('rig_requirements'):
            info_multiline("Rig Requirements", form_data.get('rig_requirements'))
        if form_data.get('vessel_rental'):
            info_multiline("Vessel Rental (Type & Specs)", form_data.get('vessel_rental'))
        crew_boat = form_data.get('crew_security_boat', 'no')
        info_row("Crew Security Boat for Hire", "[YES]" if crew_boat == 'yes' else "[NO]")
        pdf.ln(2)

        sub_section_header("3. Crew & Duration")
        info_row("Number of Security Crew", form_data.get('security_crew_count'))
        info_row("Contract Duration", form_data.get('contract_duration'))
        pdf.ln(2)

        sub_section_header("4. Deployment Details")
        info_row("Destination of Vessels/Boats", form_data.get('vessel_destination'))
        info_row("Kickoff Point/Port", form_data.get('kickoff_point'))
        pdf.ln(2)

        # ================================================================
        # 3. ADDITIONAL INFORMATION
        # ================================================================
        if form_data.get('additional_info'):
            section_header("ADDITIONAL INFORMATION")
            pdf.set_font("helvetica", "", 9)
            pdf.multi_cell(0, 4, str(form_data.get('additional_info', '')))
            pdf.ln(2)

        # ================================================================
        # 4. FINANCIAL & TIMELINE DETAILS
        # ================================================================
        section_header("FINANCIAL & TIMELINE DETAILS")
        pdf.set_font("helvetica", "B", 9)
        pdf.cell(0, 5, "Mobilization Fee:", ln=True)
        pdf.set_font("helvetica", "", 9)
        pdf.multi_cell(0, 4, "A mobilization fee is required to meet a deployment timeline of 1 to 5 days.")
        pdf.ln(1)
        timeline_map = {'1-3_days': '1-3 days', '3-5_days': '3-5 days', 'flexible': 'Flexible'}
        tval = form_data.get('estimated_timeline', '')
        info_row("Confirmed Timeline", timeline_map.get(tval, tval) if tval else 'N/A')
        pdf.ln(2)

        # ================================================================
        # 5. BANK DETAILS
        # ================================================================
        section_header("BANK DETAILS")
        pdf.set_font("helvetica", "B", 9)
        pdf.cell(0, 5, "Account Name: Phemedia Onguard Services Ltd", ln=True)
        pdf.set_font("helvetica", "B", 9)
        pdf.cell(55, 5, "Moniepoint Microfinance Bank:", ln=False)
        pdf.set_font("helvetica", "", 9)
        pdf.cell(0, 5, "6707932476", ln=True)
        pdf.set_font("helvetica", "B", 9)
        pdf.cell(55, 5, "Providus Bank:", ln=False)
        pdf.set_font("helvetica", "", 9)
        pdf.cell(0, 5, "1306872171", ln=True)
        pdf.ln(2)

        # ================================================================
        # 6. ADMIN AUTHORIZATION & AGREEMENT
        # ================================================================
        section_header("ADMIN AUTHORIZATION & AGREEMENT")
        admin_name = form_data.get('signatory_name', '')
        admin_pos  = form_data.get('signatory_position', '')
        admin_date = form_data.get('signature_date', '')
        info_row("Name", admin_name)
        info_row("Position", admin_pos)
        info_row("Date", admin_date)
        pdf.ln(1)
        # Admin signature stored under adminSignatureData_* (renamed in JS before submit)
        # Fall back to admin_clientSignatureData_* for old submissions
        admin_sig_data = {
            'clientSignatureData_drawn': (
                form_data.get('adminSignatureData_drawn') or
                form_data.get('admin_clientSignatureData_drawn', '')
            ),
            'clientSignatureData_uploaded': (
                form_data.get('adminSignatureData_uploaded') or
                form_data.get('admin_clientSignatureData_uploaded', '')
            ),
        }
        add_signatures_to_pdf(pdf, admin_sig_data, submission_id, "Admin Signature:")
        pdf.ln(2)

        # ================================================================
        # 7. CLIENT AUTHORIZATION & AGREEMENT
        # ================================================================
        client_name = form_data.get('client_signatory_name', '')
        if client_name:
            section_header("CLIENT AUTHORIZATION & AGREEMENT")
            info_row("Name", client_name)
            info_row("Position", form_data.get('client_signatory_position', ''))
            info_row("Date", form_data.get('client_signature_date', ''))
            pdf.ln(1)
            add_signatures_to_pdf(pdf, form_data, submission_id, "Client Signature:")
            pdf.ln(2)

        # ================================================================
        # 8. APPROVAL CERTIFICATION (only when approved)
        # ================================================================
        if is_approval:
            section_header("APPROVAL CERTIFICATION")
            info_row("Approved By", approver_name)
            info_row("Position", approver_position)
            info_row("Approval Date", approval_date.strftime('%d %B %Y at %H:%M:%S'))
            pdf.ln(1)
            pdf.set_font("helvetica", "B", 9)
            pdf.cell(0, 5, "Official Approval Stamp:", ln=True)
            pdf.set_font("helvetica", "", 8)
            pdf.cell(0, 5, "(Stamp to be affixed by authorized officer)", ln=True)
            pdf.ln(10)

        # Footer
        pdf.ln(3)
        pdf.set_font("helvetica", "", 8)
        pdf.cell(0, 3, f"Document Reference: OILGAS-{submission_id}", ln=True, align="C")
        pdf.cell(0, 3, f"Generated: {approval_date.strftime('%d %B %Y at %H:%M:%S')}", ln=True, align="C")

        pdf.output(pdf_path)
        return pdf_filename

    except Exception as e:
        print(f"Error generating oil & gas approval PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


@app.errorhandler(404)
def page_not_found(error):
    """Handle 404 errors"""
    return redirect(url_for('index'))


def send_client_acceptance_email(submission, client_email, acceptance_link):
    """Send client acceptance link via email"""
    try:
        client_name = submission.submitted_data.get('client_name', 'Valued Client')
        company_name = submission.submitted_data.get('company_office', '')
        
        email_html = f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Poppins', 'Segoe UI', sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background-color: #3498db; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background-color: #f9f9f9; }}
        .button {{ background-color: #27ae60; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }}
        .footer {{ background-color: #ecf0f1; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
        .warning {{ background-color: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; margin: 15px 0; }}
    </style>
</head>
<body>
    <div class='header'>
        <h2>Action Required: Digital Signature Needed</h2>
    </div>
    <div class='content'>
        <p>Dear {client_name},</p>
        <p>Thank you for initiating the Investigative Service Agreement with Phemedia Onguard Services Ltd. To complete the agreement process, we need your digital signature.</p>
        
        <div style="background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <p><strong>Agreement Summary:</strong></p>
            <ul style="margin: 10px 0; padding-left: 20px;">
                <li><strong>Agreement Date:</strong> {submission.submitted_data.get('agreement_date', 'N/A')}</li>
                <li><strong>Service Fee:</strong> ₦{submission.submitted_data.get('service_fee', '0')}</li>
                <li><strong>Status:</strong> ⏳ Awaiting Your Digital Signature</li>
            </ul>
        </div>
        
        <p>Please click the button below to review and digitally sign the agreement:</p>
        <p style="text-align: center;">
            <a href="{acceptance_link}" class="button">Sign Agreement Now →</a>
        </p>
        
        <div class="warning">
            <strong>⚠ Important:</strong> This link is unique to you and will remain valid for 30 days. Please keep it confidential. You can use this link multiple times if needed.
        </div>
        
        <p>If you have any questions about the agreement, please contact us at info@phemediaa.com or call 08099180391.</p>
        
        <p>Best regards,<br>Phemedia Onguard Services Ltd</p>
    </div>
    <div class='footer'>
        <p>&copy; 2026 Phemedia Onguard Services Ltd. All rights reserved.</p>
        <p>Tel: 08099180391, 0803231746 | Email: info@phemediaa.com</p>
    </div>
</body>
</html>"""
        
        return send_email(client_email, 'Action Required: Digital Signature for Investigative Service Agreement', email_html)
    except Exception as e:
        print(f"Error sending client acceptance email: {str(e)}")
        return False


def generate_signed_pdf(submission, client_signature_data, approver_name=None, approver_email=None, approver_position=None):
    """Generate final approved PDF for Investigative Service Agreement (Tracking Agreement)"""
    try:
        if not HAS_PDF_SUPPORT:
            print("PDF support not available")
            return None

        from fpdf import FPDF

        data = submission.submitted_data or {}
        company_address_obj = CompanyAddress.query.filter_by(is_active=True).first()
        company_addr = company_address_obj.address if company_address_obj else 'Lagos, Nigeria'

        # ── resolve approver info ──────────────────────────────────────────────
        if not approver_name:
            approver_name = data.get('company_signatory_name', 'Authorized Signatory')
        if not approver_position:
            approver_position = submission.approver_position or data.get('company_position', '')

        # ── helpers ───────────────────────────────────────────────────────────
        BLUE  = (41, 128, 185)
        BLACK = (0, 0, 0)
        GREY  = (80, 80, 80)
        LGREY = (245, 245, 245)

        def header_bar(pdf, txt, r=41, g=128, b=185):
            pdf.set_fill_color(r, g, b)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("helvetica", "B", 10)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(190, 7, txt, fill=True, align="L")
            pdf.set_text_color(0, 0, 0)

        def row(pdf, label, value, shade=False):
            if shade:
                pdf.set_fill_color(*LGREY)
            else:
                pdf.set_fill_color(255, 255, 255)
            pdf.set_font("helvetica", "B", 9)
            pdf.cell(55, 6, label, border=0, fill=shade)
            pdf.set_font("helvetica", "", 9)
            remaining = 190 - 55
            # multi-line safe
            x, y = pdf.get_x(), pdf.get_y()
            pdf.multi_cell(remaining, 6, str(value) if value else 'N/A', border=0, fill=shade)

        def clause(pdf, number, title, body):
            pdf.ln(2)
            pdf.set_font("helvetica", "B", 9)
            pdf.set_text_color(*BLACK)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(190, 6, f"{number}. {title.upper()}")
            pdf.set_font("helvetica", "", 9)
            pdf.set_text_color(*GREY)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(190, 5, body)
            pdf.set_text_color(*BLACK)

        # ── build PDF ─────────────────────────────────────────────────────────
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.set_margins(10, 10, 10)
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # ── company header ────────────────────────────────────────────────────
        pdf.set_font("helvetica", "B", 14)
        pdf.set_text_color(*BLUE)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(190, 8, "PHEMEDIA ONGUARD SERVICES LTD", align="C")
        pdf.set_font("helvetica", "", 9)
        pdf.set_text_color(*GREY)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(190, 5, "Tel: 08099180391, 08032317464  |  E-mail: info@phemediaa.com  |  Website: www.phemediaa.com", align="C")
        pdf.set_text_color(*BLACK)
        pdf.set_draw_color(*BLUE)
        pdf.set_line_width(0.8)
        pdf.line(10, pdf.get_y() + 1, 200, pdf.get_y() + 1)
        pdf.ln(4)

        # ── document title ────────────────────────────────────────────────────
        pdf.set_font("helvetica", "B", 13)
        pdf.set_text_color(*BLUE)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(190, 8, "TRACKING AGREEMENT FORM", align="C")
        pdf.set_font("helvetica", "", 9)
        pdf.set_text_color(*GREY)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(190, 5, f"Agreement Date: {data.get('agreement_date', 'N/A')}  |  Submission ID: #{submission.id}", align="C")
        pdf.set_text_color(*BLACK)
        pdf.ln(3)

        # ── SECTION 1: Parties ────────────────────────────────────────────────
        header_bar(pdf, "PARTIES TO THE AGREEMENT")
        pdf.ln(1)
        pdf.set_font("helvetica", "B", 9)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(190, 6, "SERVICE PROVIDER:")
        pdf.set_font("helvetica", "", 9)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(190, 5, f"Phemedia Onguard Services Ltd\n{company_addr}")
        pdf.ln(2)
        pdf.set_font("helvetica", "B", 9)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(190, 6, "CLIENT:")
        pdf.set_font("helvetica", "", 9)
        client_lines = [
            data.get('client_name', 'N/A'),
            data.get('client_address', ''),
            f"Email: {data.get('client_email', '') or submission.user_email or 'N/A'}",
            f"Phone: {data.get('client_phone', 'N/A')}",
        ]
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(190, 5, "\n".join(filter(None, client_lines)))
        pdf.ln(3)

        # ── SECTION 2: Scope of Services ─────────────────────────────────────
        header_bar(pdf, "1. SCOPE OF SERVICES")
        pdf.ln(1)
        pdf.set_font("helvetica", "", 9)
        pdf.set_text_color(*GREY)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(190, 5, "The Service Provider agrees to provide professional investigative support to the Client, which may include:")
        pdf.set_text_color(*BLACK)
        scope_vals = data.get('scope_services', [])
        if isinstance(scope_vals, str):
            scope_vals = [scope_vals]
        all_services = [
            "Mobile device location tracking (within the limits permitted by Nigerian law)",
            "Cryptocurrency fraud investigation, tracing, and reporting",
            "Security intelligence advisory services",
        ]
        for svc in all_services:
            ticked = any(svc.lower()[:20] in sv.lower() for sv in scope_vals) if scope_vals else True
            mark = "[X]" if ticked else "[ ]"
            pdf.set_font("helvetica", "", 9)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(190, 5, f"  {mark}  {svc}")
        pdf.ln(2)

        # ── Clauses 2–9 ───────────────────────────────────────────────────────
        clause(pdf, 2, "Legal Compliance",
               "The Service Provider shall render all services in compliance with the Nigeria Police Act.\n"
               "The Service Provider reserves the right to refuse any request deemed unlawful or unethical.")

        clause(pdf, 3, "Limitations of Service",
               "While the Service Provider shall apply industry-approved investigative methods, no guarantee of "
               "100% success or accuracy is made, as technical limitations or unforeseen circumstances may affect outcomes.")

        clause(pdf, 4, "Client Responsibilities",
               "The Client must provide truthful, accurate, and complete information necessary for the execution of services.")

        clause(pdf, 5, "Confidentiality",
               "Both parties agree to maintain strict confidentiality over all sensitive information exchanged during the course of this Agreement.")

        # ── Clause 6: Fees & Payment ──────────────────────────────────────────
        pdf.ln(2)
        pdf.set_font("helvetica", "B", 9)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(190, 6, "6. FEES & PAYMENT")
        pdf.set_font("helvetica", "B", 9)
        pdf.set_text_color(*GREY)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(190, 5, "Payment Terms:")
        pdf.set_font("helvetica", "", 9)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(190, 5,
            "- The Client shall pay the agreed service fee before commencement of service\n"
            "- No refunds shall be issued once investigative work has begun")
        pdf.set_text_color(*BLACK)
        pdf.ln(1)
        # fee box
        pdf.set_fill_color(*LGREY)
        pdf.set_font("helvetica", "B", 9)
        pdf.set_x(pdf.l_margin)
        pdf.cell(60, 7, "Service Fee (NGN)", border=1, fill=True)
        pdf.set_font("helvetica", "", 9)
        pdf.cell(130, 7, f"NGN {data.get('service_fee', 'N/A')}", border=1, ln=True)
        pdf.ln(1)
        # bank details
        pdf.set_font("helvetica", "B", 9)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(190, 5, "Bank Payment Details:")
        pdf.set_font("helvetica", "", 9)
        pdf.set_text_color(*GREY)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(190, 5,
            "Phemedia Onguard Services Ltd\n"
            "Moniepoint Microfinance Bank  |  Account No: 6707932476\n"
            "OR\n"
            "Providus Bank  |  Account No: 1306872171")
        pdf.set_text_color(*BLACK)

        clause(pdf, 7, "Limitation of Liability",
               "The Service Provider shall not be liable for any indirect, incidental, or consequential damages "
               "arising from the use or results of the services provided.")

        clause(pdf, 8, "Termination",
               "Either party may terminate this Agreement with written notice. However, fees paid are non-refundable.")

        clause(pdf, 9, "Governing Law",
               "This Agreement shall be governed by and construed in accordance with the laws of the Federal Republic of Nigeria.")

        pdf.ln(3)

        # ── SIGNATURES ────────────────────────────────────────────────────────
        header_bar(pdf, "AUTHORIZED SIGNATURES")
        pdf.ln(3)

        # ── helper: decode a list of base64 strings to temp image files ────────
        all_temp_sig_paths = []

        def decode_sig_images(raw_list):
            """Return list of file paths for each valid base64 image in raw_list."""
            paths = []
            for raw in raw_list:
                if not raw:
                    continue
                try:
                    clean = raw.split('base64,')[1] if 'base64,' in raw else raw
                    sig_bytes = base64.b64decode(clean)
                    tpath = os.path.join(PDFS_FOLDER,
                        f'tmp_sig_{submission.id}_{len(all_temp_sig_paths)+len(paths)}_{int(time.time()*1000)}.png')
                    with open(tpath, 'wb') as f:
                        f.write(sig_bytes)
                    paths.append(tpath)
                    all_temp_sig_paths.append(tpath)
                except Exception:
                    pass
            return paths

        # ── resolve client signatures ─────────────────────────────────────────
        client_sig_name = (data.get('client_sig_name') or
                           data.get('client_acceptance_name') or
                           data.get('client_name') or 'N/A')
        client_designation = data.get('client_designation', '')
        client_sig_date = (data.get('client_agreement_date') or
                           data.get('acceptance_date') or
                           datetime.now().strftime('%d %B %Y'))

        c_drawn   = data.get('clientSignatureData_drawn', '') or ''
        c_uploaded = data.get('clientSignatureData_uploaded', '') or data.get('clientSignatureData', '') or ''
        if not c_drawn and not c_uploaded:
            c_drawn = client_signature_data or ''
        # deduplicate: if drawn == uploaded (same data), show once
        raw_client_list = [c_drawn]
        if c_uploaded and c_uploaded != c_drawn:
            raw_client_list.append(c_uploaded)
        client_sig_paths = decode_sig_images(raw_client_list)

        # ── ROW 1: CLIENT details (left 115mm) + signature images (right 75mm) ─
        row1_y = pdf.get_y()
        # details
        pdf.set_font("helvetica", "B", 9)
        pdf.set_text_color(*BLUE)
        pdf.set_xy(10, row1_y)
        pdf.cell(115, 6, "CLIENT SIGNATURE", border=0, ln=True)
        pdf.set_text_color(*BLACK)
        pdf.set_font("helvetica", "", 9)
        pdf.set_x(10)
        pdf.cell(115, 5, f"Name: {client_sig_name}", border=0, ln=True)
        if client_designation:
            pdf.set_x(10)
            pdf.cell(115, 5, f"Designation: {client_designation}", border=0, ln=True)
        pdf.set_x(10)
        pdf.cell(115, 5, f"Date: {client_sig_date}", border=0, ln=True)
        row1_bottom = pdf.get_y()
        # signature images on the right
        sig_x = 128
        if len(client_sig_paths) == 2:
            pdf.image(client_sig_paths[0], x=sig_x,      y=row1_y + 1, w=36, h=18)
            pdf.image(client_sig_paths[1], x=sig_x + 37, y=row1_y + 1, w=36, h=18)
        elif len(client_sig_paths) == 1:
            pdf.image(client_sig_paths[0], x=sig_x, y=row1_y + 1, w=60, h=22)
        # separator line
        row1_end = max(row1_bottom, row1_y + 26)
        pdf.set_y(row1_end)
        pdf.set_draw_color(200, 200, 200)
        pdf.set_line_width(0.3)
        pdf.line(10, pdf.get_y() + 1, 200, pdf.get_y() + 1)
        pdf.ln(4)

        # ── resolve approver stamps ───────────────────────────────────────────
        approver_stamp_paths = []
        if submission.stamp_filename:
            p = os.path.join(STAMPS_FOLDER, submission.stamp_filename)
            if os.path.exists(p):
                approver_stamp_paths.append(p)
        drawn_stamp_name = data.get('approver_stamp_drawn_filename', '')
        if drawn_stamp_name and drawn_stamp_name != submission.stamp_filename:
            p2 = os.path.join(STAMPS_FOLDER, drawn_stamp_name)
            if os.path.exists(p2):
                approver_stamp_paths.append(p2)

        # ── ROW 2: ADMIN details (left 115mm) + stamp images (right 75mm) ─────
        row2_y = pdf.get_y()
        pdf.set_font("helvetica", "B", 9)
        pdf.set_text_color(*BLUE)
        pdf.set_xy(10, row2_y)
        pdf.cell(115, 6, "FOR PHEMEDIA ONGUARD SERVICES LTD", border=0, ln=True)
        pdf.set_text_color(*BLACK)
        pdf.set_font("helvetica", "", 9)
        pdf.set_x(10)
        pdf.cell(115, 5, f"Name: {approver_name or 'N/A'}", border=0, ln=True)
        pdf.set_x(10)
        pdf.cell(115, 5, f"Position: {approver_position or 'N/A'}", border=0, ln=True)
        pdf.set_x(10)
        pdf.cell(115, 5, f"Email: {approver_email or 'N/A'}", border=0, ln=True)
        if submission.approved_at:
            pdf.set_x(10)
            pdf.cell(115, 5, f"Date: {submission.approved_at.strftime('%d %B %Y')}", border=0, ln=True)
        row2_bottom = pdf.get_y()
        # stamp images on the right
        if len(approver_stamp_paths) == 2:
            pdf.image(approver_stamp_paths[0], x=sig_x,      y=row2_y + 1, w=36, h=18)
            pdf.image(approver_stamp_paths[1], x=sig_x + 37, y=row2_y + 1, w=36, h=18)
        elif len(approver_stamp_paths) == 1:
            pdf.image(approver_stamp_paths[0], x=sig_x, y=row2_y + 1, w=60, h=22)

        row2_end = max(row2_bottom, row2_y + 26)
        pdf.set_y(row2_end)
        pdf.ln(4)

        # clean up temp files
        for p in all_temp_sig_paths:
            try:
                if os.path.exists(p): os.remove(p)
            except Exception:
                pass

        # ── footer ────────────────────────────────────────────────────────────
        pdf.set_draw_color(*BLUE)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(2)
        pdf.set_font("helvetica", "I", 8)
        pdf.set_text_color(*GREY)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(190, 4,
            "This is an electronically signed agreement. Both parties have reviewed and accepted all terms and conditions "
            "outlined in this Agreement. This document is legally binding and enforceable under Nigerian law. RC: 82182194")
        pdf.set_text_color(*BLACK)

        # clean up temp files (all_temp_sig_paths populated by decode_sig_images helper)
        for p in all_temp_sig_paths:
            try:
                if os.path.exists(p):
                    os.remove(p)
            except Exception:
                pass

        # ── save ──────────────────────────────────────────────────────────────
        pdf_filename = f'tracking_agreement_{submission.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        pdf_path = os.path.join(PDFS_FOLDER, pdf_filename)
        pdf.output(pdf_path)

        submission.pdf_filename = pdf_filename
        submission.final_pdf_filename = pdf_filename
        db.session.commit()

        print(f"Tracking agreement PDF generated: {pdf_path}")
        return pdf_path

    except Exception as e:
        print(f"Error generating signed PDF: {str(e)}")
        import traceback; traceback.print_exc()
        return None


@app.route('/client-acceptance/<token>')
def client_acceptance_form(token):
    """Display client acceptance form"""
    try:
        submission = FormSubmission.query.filter_by(
            client_acceptance_token=token,
            form_type='trackingagreement'
        ).first()
        
        if not submission:
            return render_template('error.html', error='Invalid or expired link'), 404
        
        # Check if already completed
        if submission.client_acceptance_completed:
            return render_template('error.html', error='This agreement has already been signed. Check your email for the final signed copy.'), 400
        
        return render_template('client_acceptance.html', agreement=submission)
    except Exception as e:
        print(f"Error loading acceptance form: {str(e)}")
        return render_template('error.html', error='An error occurred'), 500


@app.route('/submit-client-acceptance', methods=['POST'])
def submit_client_acceptance():
    """Handle client signature submission"""
    try:
        token = request.form.get('token')
        if not token:
            return jsonify({'success': False, 'message': 'Invalid token'}), 400
        
        submission = FormSubmission.query.filter_by(
            client_acceptance_token=token,
            form_type='trackingagreement'
        ).first()
        
        if not submission:
            return jsonify({'success': False, 'message': 'Agreement not found'}), 404
        
        if submission.client_acceptance_completed:
            return jsonify({'success': False, 'message': 'This agreement has already been signed'}), 400
        
        # Update submission with client acceptance data
        # Use dict reassignment so SQLAlchemy detects the JSON column change
        new_data = dict(submission.submitted_data) if submission.submitted_data else {}
        new_data['clientSignatureData']          = request.form.get('clientSignatureData', '')
        new_data['clientSignatureData_drawn']    = request.form.get('clientSignatureData_drawn', '')
        new_data['clientSignatureData_uploaded'] = request.form.get('clientSignatureData_uploaded', '')
        new_data['client_acceptance_name']       = request.form.get('client_acceptance_name', '')
        new_data['client_acceptance_phone']      = request.form.get('client_acceptance_phone', '')
        new_data['client_acceptance_address']    = request.form.get('client_acceptance_address', '')
        new_data['acceptance_date']              = request.form.get('acceptance_date', '')
        submission.submitted_data = new_data
        submission.client_signature_data = request.form.get('clientSignatureData')
        submission.client_acceptance_completed = True
        submission.client_acceptance_completed_at = datetime.utcnow()
        submission.status = 'pending_approval'  # Requires admin approval before PDF is sent

        db.session.commit()

        # Notify admin that approval is needed
        client_name = submission.submitted_data.get('client_name', 'Valued Client')
        client_email_addr = submission.user_email
        admin_notification_html = f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Poppins', 'Segoe UI', sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background-color: #f39c12; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .footer {{ background-color: #f5f5f5; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class='header'>
        <h2>⏳ Tracking Agreement Signed – Awaiting Approval</h2>
    </div>
    <div class='content'>
        <p>A Tracking Agreement has been signed by the client and is now awaiting your approval.</p>
        <p><strong>Client Name:</strong> {client_name}</p>
        <p><strong>Client Email:</strong> {client_email_addr}</p>
        <p><strong>Agreement Date:</strong> {submission.submitted_data.get('agreement_date', 'N/A')}</p>
        <p><strong>Signed Date:</strong> {datetime.now().strftime('%d %B %Y at %H:%M:%S')}</p>
        <p><strong>Service Fee:</strong> ₦{submission.submitted_data.get('service_fee', '0')}</p>
        <p>Please log in to the admin dashboard to review and approve this agreement.</p>
        <p><a href="/admin/approve-trackingagreement/{submission.id}" style="background:#27ae60;color:white;padding:10px 20px;text-decoration:none;border-radius:4px;">✓ Approve Agreement</a></p>
    </div>
    <div class='footer'>
        <p>&copy; 2026 Phemedia Onguard Services Ltd. All rights reserved.</p>
    </div>
</body>
</html>"""
        send_email(ADMIN_EMAIL, f'Tracking Agreement Signed – Pending Approval (#{submission.id})', admin_notification_html)

        # Acknowledge client
        client_ack_html = f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Poppins', 'Segoe UI', sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background-color: #3498db; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .footer {{ background-color: #f5f5f5; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class='header'>
        <h2>Your Agreement Has Been Received</h2>
    </div>
    <div class='content'>
        <p>Dear {client_name},</p>
        <p>Thank you for signing the Investigative Service Agreement. Your signature has been received and is currently under review.</p>
        <p>You will receive the final approved copy of your agreement via email within 1-2 business days.</p>
        <p>Best regards,<br>Phemedia Onguard Services Ltd</p>
    </div>
    <div class='footer'>
        <p>&copy; 2026 Phemedia Onguard Services Ltd. All rights reserved.</p>
    </div>
</body>
</html>"""
        if client_email_addr:
            send_email(client_email_addr, 'Agreement Received – Pending Approval', client_ack_html)

        return jsonify({'success': True, 'message': 'Agreement signed successfully. You will receive the approved copy via email shortly.'})
    except Exception as e:
        print(f"Error submitting client acceptance: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error processing signature: {str(e)}'}), 500


@app.route('/admin/approve-trackingagreement/<int:submission_id>', methods=['GET'])
@require_admin_or_superadmin
def show_approval_form_trackingagreement(submission_id):
    """Show approval form for tracking agreement"""
    submission = FormSubmission.query.get_or_404(submission_id)
    if submission.form_type != 'trackingagreement' or submission.status not in ('submitted', 'pending_approval'):
        flash('This agreement cannot be approved at this stage.', 'danger')
        return redirect(url_for('view_admin_submission', submission_id=submission_id))
    return render_template('approve_trackingagreement.html', submission=submission)


@app.route('/admin/approve-trackingagreement/<int:submission_id>', methods=['POST'])
@require_admin_or_superadmin
def process_approval_trackingagreement(submission_id):
    """Process approval for tracking agreement"""
    submission = FormSubmission.query.get_or_404(submission_id)
    if submission.form_type != 'trackingagreement' or submission.status not in ('submitted', 'pending_approval'):
        flash('This agreement cannot be approved at this stage.', 'danger')
        return redirect(url_for('view_admin_submission', submission_id=submission_id))

    approver_name = request.form.get('approver_name', '').strip()
    approver_email = request.form.get('approver_email', '').strip()
    approver_position = request.form.get('approver_position', '').strip()
    signature_data = request.form.get('signature_data', '').strip()
    signature_data_drawn = request.form.get('signature_data_drawn', '').strip()

    if not approver_name:
        flash('Approver name is required.', 'danger')
        return redirect(url_for('show_approval_form_trackingagreement', submission_id=submission_id))
    if not approver_email or not validate_email(approver_email):
        flash('Valid approver email is required.', 'danger')
        return redirect(url_for('show_approval_form_trackingagreement', submission_id=submission_id))
    if not approver_position:
        flash('Approver position is required.', 'danger')
        return redirect(url_for('show_approval_form_trackingagreement', submission_id=submission_id))
    if not signature_data and not signature_data_drawn:
        flash('Approval signature is required.', 'danger')
        return redirect(url_for('show_approval_form_trackingagreement', submission_id=submission_id))

    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        stamp_filepath = None
        stamp_drawn_filepath = None
        filename = None

        if signature_data:
            sig_bytes = base64.b64decode(signature_data.split(',')[1] if ',' in signature_data else signature_data)
            filename = secure_filename(f'tracking_approval_{submission_id}_{timestamp}.png')
            stamp_filepath = os.path.join(app.config['STAMPS_FOLDER'], filename)
            with open(stamp_filepath, 'wb') as f:
                f.write(sig_bytes)

        if signature_data_drawn:
            sig_bytes_drawn = base64.b64decode(signature_data_drawn.split(',')[1] if ',' in signature_data_drawn else signature_data_drawn)
            filename_drawn = secure_filename(f'tracking_approval_drawn_{submission_id}_{timestamp}.png')
            stamp_drawn_filepath = os.path.join(app.config['STAMPS_FOLDER'], filename_drawn)
            with open(stamp_drawn_filepath, 'wb') as f:
                f.write(sig_bytes_drawn)
            if not filename:
                filename = filename_drawn

        submission.status = 'approved'
        submission.approved_at = datetime.now()
        submission.approver_position = approver_position
        if filename:
            submission.stamp_filename = filename
        # Store drawn stamp filename so PDF regeneration can show both signatures
        new_data = dict(submission.submitted_data) if submission.submitted_data else {}
        if stamp_drawn_filepath and stamp_filepath and stamp_drawn_filepath != stamp_filepath:
            # Both uploaded and drawn were provided — save drawn filename separately
            new_data['approver_stamp_drawn_filename'] = os.path.basename(stamp_drawn_filepath)
        else:
            new_data.pop('approver_stamp_drawn_filename', None)
        submission.submitted_data = new_data
        db.session.commit()

        # Generate final PDF
        pdf_path = generate_signed_pdf(
            submission,
            submission.client_signature_data,
            approver_name=approver_name,
            approver_email=approver_email,
            approver_position=approver_position
        )

        client_email = submission.user_email
        client_name = submission.submitted_data.get('client_name', 'Valued Client')

        client_html = f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Poppins', 'Segoe UI', sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background-color: #27ae60; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .footer {{ background-color: #f5f5f5; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class='header'><h2>&#10003; Your Agreement Has Been Approved</h2></div>
    <div class='content'>
        <p>Dear {client_name},</p>
        <p>Your Investigative Service Agreement has been reviewed and approved by {approver_name}, {approver_position}.</p>
        <p><strong>Approval Date:</strong> {datetime.now().strftime('%d %B %Y')}</p>
        <p>Please find the final signed agreement attached. Keep this for your records.</p>
        <p>Best regards,<br>Phemedia Onguard Services Ltd</p>
    </div>
    <div class='footer'><p>&copy; 2026 Phemedia Onguard Services Ltd. All rights reserved.</p></div>
</body>
</html>"""

        approver_html = f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Poppins', 'Segoe UI', sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background-color: #2980b9; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
    </style>
</head>
<body>
    <div class='header'><h2>Tracking Agreement Approval Confirmation</h2></div>
    <div class='content'>
        <p>Dear {approver_name},</p>
        <p>You have approved the Tracking Agreement for <strong>{client_name}</strong> (#{submission_id}).</p>
        <p><strong>Client Email:</strong> {client_email}</p>
        <p><strong>Approval Date:</strong> {datetime.now().strftime('%d %B %Y at %H:%M:%S')}</p>
    </div>
</body>
</html>"""

        if pdf_path and os.path.exists(pdf_path):
            pdf_filename = os.path.basename(pdf_path)
            send_email_with_attachment(client_email, 'Your Approved Investigative Service Agreement', client_html, pdf_path, pdf_filename)
            send_email_with_attachment(approver_email, f'Tracking Agreement Approved – #{submission_id}', approver_html, pdf_path, pdf_filename)
            flash('Agreement approved successfully! PDF sent to client and approver.', 'success')
        else:
            send_email(client_email, 'Your Investigative Service Agreement Has Been Approved', client_html)
            flash('Agreement approved. PDF generation encountered an issue.', 'warning')

        return redirect(url_for('view_admin_submission', submission_id=submission_id))

    except Exception as e:
        print(f"Error approving tracking agreement: {str(e)}")
        import traceback; traceback.print_exc()
        db.session.rollback()
        flash(f'Error approving agreement: {str(e)}', 'danger')
        return redirect(url_for('show_approval_form_trackingagreement', submission_id=submission_id))


@app.route('/admin/resend-acceptance-link/<int:submission_id>', methods=['POST'])
@require_admin_or_superadmin
def resend_acceptance_link(submission_id):
    """Resend client acceptance link"""
    try:
        submission = FormSubmission.query.get(submission_id)
        
        if not submission or submission.form_type != 'trackingagreement':
            return jsonify({'success': False, 'message': 'Agreement not found'}), 404
        
        if submission.client_acceptance_completed:
            return jsonify({'success': False, 'message': 'Client has already signed this agreement'}), 400
        
        # Resend acceptance link email
        if submission.user_email and submission.client_acceptance_link:
            success = send_client_acceptance_email(submission, submission.user_email, submission.client_acceptance_link)
            if success:
                return jsonify({'success': True, 'message': f'Acceptance link has been resent to {submission.user_email}'})
            else:
                return jsonify({'success': False, 'message': 'Failed to send email'}), 500
        else:
            return jsonify({'success': False, 'message': 'No email address on file'}), 400
    except Exception as e:
        print(f"Error resending acceptance link: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@app.route('/superadmin/resend-acceptance-link/<int:submission_id>', methods=['POST'])
@require_superadmin
def superadmin_resend_acceptance_link(submission_id):
    """Superadmin: Resend client acceptance link"""
    try:
        submission = FormSubmission.query.get(submission_id)
        
        if not submission or submission.form_type != 'trackingagreement':
            return jsonify({'success': False, 'message': 'Agreement not found'}), 404
        
        if submission.client_acceptance_completed:
            return jsonify({'success': False, 'message': 'Client has already signed this agreement'}), 400
        
        # Resend acceptance link email
        if submission.user_email and submission.client_acceptance_link:
            success = send_client_acceptance_email(submission, submission.user_email, submission.client_acceptance_link)
            if success:
                return jsonify({'success': True, 'message': f'Acceptance link has been resent to {submission.user_email}'})
            else:
                return jsonify({'success': False, 'message': 'Failed to send email'}), 500
        else:
            return jsonify({'success': False, 'message': 'No email address on file'}), 400
    except Exception as e:
        print(f"Error resending acceptance link: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


if __name__ == '__main__':
    # Email configuration
    ADMIN_EMAIL = 'info@phemediaa.com'
    FROM_EMAIL = 'femioluwole1@gmail.com'
    
    # For development
    app.run(debug=True, host='127.0.0.1', port=5000)
