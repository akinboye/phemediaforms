#!/usr/bin/env python3
"""Test oil & gas service request form submission"""
from app import app, db, process_form_submission
from flask import Request
from werkzeug.test import EnvironBuilder

app.app_context().push()

# Create a mock request context
builder = EnvironBuilder(method='POST', path='/submit-form')
env = builder.get_environ()

with app.request_context(env):
    form_data = {
        'company_name': 'Oil Company Ltd',
        'client_email': 'client@oilcompany.com',
        'contact_person': 'John Manager',
        'phone': '08099180391',
        'service_required': 'Security Services',
        'location': 'Lagos, Nigeria',
        'estimated_duration': 'Q1 2026',
        'budget_range': '100,000 - 500,000 NGN',
        'contract_terms': 'Standard',
        'service_details': 'Comprehensive security coverage',
        'clientSignatureData': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA'
    }
    
    print("Testing oil & gas service request form submission...")
    try:
        result = process_form_submission('oilgasservicerequest', form_data)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()
