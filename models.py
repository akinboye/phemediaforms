"""
Database models for PHEMEDAA Forms Portal
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

db = SQLAlchemy()

class SuperAdmin(db.Model):
    """Superadmin user"""
    __tablename__ = 'superadmin'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SuperAdmin {self.username}>'


class Admin(db.Model):
    """Admin user created by superadmin"""
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('superadmin.id'))
    
    def __repr__(self):
        return f'<Admin {self.username}>'


class NotificationEmail(db.Model):
    """Email addresses to receive form submissions"""
    __tablename__ = 'notification_emails'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    form_type = db.Column(db.String(50), nullable=False)  # 'all' or specific form type
    is_active = db.Column(db.Boolean, default=True)
    added_by_admin = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=True)
    added_by_superadmin = db.Column(db.Integer, db.ForeignKey('superadmin.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<NotificationEmail {self.email}>'


class FormSubmission(db.Model):
    """Store form submissions"""
    __tablename__ = 'form_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    form_type = db.Column(db.String(50), nullable=False)  # backgroundchecks, declarationbyemployee, etc
    submitted_data = db.Column(db.JSON, nullable=False)  # Store all form data as JSON
    user_email = db.Column(db.String(120), nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    
    # Service Agreement Approval Workflow
    status = db.Column(db.String(20), default='submitted')  # submitted, pending_approval, approved, rejected
    approved_by_admin = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=True)
    approved_by_superadmin = db.Column(db.Integer, db.ForeignKey('superadmin.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    approver_position = db.Column(db.String(255), nullable=True)  # Position/title of approver
    rejection_reason = db.Column(db.String(500), nullable=True)
    pdf_filename = db.Column(db.String(255), nullable=True)  # Generated PDF file
    stamp_filename = db.Column(db.String(255), nullable=True)  # Stamp used for approval
    
    # Employee Declaration form uploads
    photo_filename = db.Column(db.String(255), nullable=True)  # Employee passport photo
    nin_filename = db.Column(db.String(255), nullable=True)  # Employee NIN/ID document
    
    # Client Acceptance Tracking (for tracking agreements)
    client_acceptance_token = db.Column(db.String(255), unique=True, nullable=True)  # Unique token for client link
    client_acceptance_link = db.Column(db.String(500), nullable=True)  # Full URL for client
    client_acceptance_completed = db.Column(db.Boolean, default=False)  # Whether client completed
    client_acceptance_completed_at = db.Column(db.DateTime, nullable=True)  # When client completed
    client_signature_data = db.Column(db.Text, nullable=True)  # Client signature (base64 or image)
    final_pdf_filename = db.Column(db.String(255), nullable=True)  # Final signed PDF
    
    # Relationships for approval
    admin_approver = db.relationship('Admin', backref='approved_submissions')
    superadmin_approver = db.relationship('SuperAdmin', backref='approved_submissions')
    
    def __repr__(self):
        return f'<FormSubmission {self.form_type} - {self.submitted_at}>'
    
    def get_display_data(self):
        """Format submitted data for display"""
        result = {}
        for key, value in self.submitted_data.items():
            # Format field names nicely
            display_key = key.replace('_', ' ').title()
            result[display_key] = value
        return result


class CompanyAddress(db.Model):
    """Store company address information"""
    __tablename__ = 'company_address'
    
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(500), nullable=False)  # Full company address
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('superadmin.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to SuperAdmin
    created_by_admin = db.relationship('SuperAdmin', backref='company_addresses')
    
    def __repr__(self):
        return f'<CompanyAddress {self.address[:50]}>'


class ApprovalStamp(db.Model):
    """Store company approval stamps/seals for agreements"""
    __tablename__ = 'approval_stamps'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)  # Filename of stamp image
    uploaded_by_admin = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=True)
    uploaded_by_superadmin = db.Column(db.Integer, db.ForeignKey('superadmin.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)  # Only one active stamp at a time
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    admin_uploader = db.relationship('Admin', backref='uploaded_stamps')
    superadmin_uploader = db.relationship('SuperAdmin', backref='uploaded_stamps')
    
    def __repr__(self):
        return f'<ApprovalStamp {self.filename}>'
