#!/usr/bin/env python3
"""Comprehensive test for oil & gas form with Flask request context"""
import requests
import json
from app import app, db, FormSubmission
import sys

# Start Flask app context
app.app_context().push()

print("=" * 60)
print("COMPREHENSIVE OIL & GAS FORM SUBMISSION TEST")
print("=" * 60)

# Test 1: Direct function call
print("\n[TEST 1] Direct process_form_submission call")
print("-" * 60)
from app import process_form_submission
from werkzeug.test import EnvironBuilder

builder = EnvironBuilder(method='POST', path='/submit-form')
env = builder.get_environ()

with app.request_context(env):
    form_data = {
        'company_name': 'Global Oil Corporation',
        'client_email': 'security@globaloil.com',
        'contact_person': 'Margaret Smith',
        'phone': '08012345678',
        'service_required': 'Personnel Security',
        'location': 'Port Harcourt, Nigeria',
        'estimated_duration': 'Q2 2026',
        'budget_range': '500,000 - 1,000,000 NGN',
        'contract_terms': 'Flexible',
        'service_details': 'High-level personnel protection and facility security',
        'clientSignatureData': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
    }
    
    result = process_form_submission('oilgasservicerequest', form_data)
    print(f"Status: {'✓ SUCCESS' if result.get('success') else '✗ FAILED'}")
    print(f"Message: {result.get('message')}")
    if result.get('submission_id'):
        print(f"Submission ID: {result.get('submission_id')}")

# Test 2: Verify database entry
print("\n[TEST 2] Verify database entry")
print("-" * 60)
submission = FormSubmission.query.filter_by(form_type='oilgasservicerequest').order_by(FormSubmission.id.desc()).first()

if submission:
    print(f"Submission ID: {submission.id}")
    print(f"Form Type: {submission.form_type}")
    print(f"Status: {submission.status}")
    print(f"User Email: {submission.user_email}")
    print(f"Company Name: {submission.submitted_data.get('company_name')}")
    print(f"Contact Person: {submission.submitted_data.get('contact_person')}")
    
    # Verify email
    if submission.user_email == 'security@globaloil.com':
        print("\n✓ Email correctly captured from client_email field")
    else:
        print(f"\n✗ Email NOT captured correctly. Expected: security@globaloil.com, Got: {submission.user_email}")
        sys.exit(1)
    
    # Verify status
    if submission.status == 'pending_approval':
        print("✓ Status correctly set to pending_approval")
    else:
        print(f"✗ Status incorrect. Expected: pending_approval, Got: {submission.status}")
        sys.exit(1)
else:
    print("✗ No submission found in database!")
    sys.exit(1)

# Test 3: Verify all required fields saved
print("\n[TEST 3] Verify form fields saved")
print("-" * 60)
required_fields = ['company_name', 'client_email', 'contact_person', 'phone', 'service_required', 'location']
missing_fields = []

for field in required_fields:
    if field in submission.submitted_data:
        print(f"✓ {field}: {submission.submitted_data.get(field)}")
    else:
        print(f"✗ {field}: MISSING")
        missing_fields.append(field)

if missing_fields:
    print(f"\n✗ Missing fields: {missing_fields}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ ALL TESTS PASSED - OIL & GAS FORM IS WORKING CORRECTLY")
print("=" * 60)
