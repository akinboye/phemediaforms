#!/usr/bin/env python3
"""Test process_form_submission directly for guarantorundertaking"""
from app import app, db, process_form_submission
from flask import Request
from werkzeug.test import EnvironBuilder

app.app_context().push()

# Create a mock request context
builder = EnvironBuilder(method='POST', path='/submit-form')
env = builder.get_environ()

with app.request_context(env):
    form_data = {
        'guarantor_full_name': 'Test Guarantor',
        'guarantor_phone': '08099180391',
        'guarantor_email': 'guarantor@test.com',
        'guarantor_address': '123 Test Street',
        'client_name': 'Test Client',
        'client_email': 'client@test.com',
    }
    
    print("Calling process_form_submission for guarantorundertaking...")
    try:
        result = process_form_submission('guarantorundertaking', form_data)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()
