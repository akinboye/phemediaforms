#!/usr/bin/env python3
"""Test guarantor undertaking form with new approval workflow"""
from app import app, db, process_form_submission, FormSubmission
from flask import Request

app.app_context().push()

# Create a test form submission for guarantor undertaking
form_data = {
    'guarantor_full_name': 'John Guarantor Test',
    'guarantor_phone': '08099180391',
    'guarantor_email': 'guarantor@example.com',
    'guarantor_address': '456 Guarantor Street, Lagos',
    'client_name': 'Client Test Corp',
    'client_email': 'client@test.com',
    'clientSignatureData': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA'  # Minimal base64 image
}

# Create a mock request context
from werkzeug.test import EnvironBuilder
builder = EnvironBuilder(method='POST', path='/submit-form')
env = builder.get_environ()

with app.request_context(env):
    print("Testing guarantor undertaking form submission with new approval workflow...")
    result = process_form_submission('guarantorundertaking', form_data)
    print(f"Result: {result}")
    
    # Check the latest submission
    latest = FormSubmission.query.filter_by(form_type='guarantorundertaking').order_by(FormSubmission.id.desc()).first()
    if latest:
        print(f"\nLatest submission created:")
        print(f"  ID: {latest.id}")
        print(f"  Status: {latest.status}")
        print(f"  User Email: {latest.user_email}")
        print(f"  Email captured correctly: {'YES' if latest.user_email == 'guarantor@example.com' else 'NO'}")
    else:
        print("No submission found!")
