#!/usr/bin/env python3
"""Test guarantor undertaking form submission"""
import requests
import re

BASE_URL = 'http://127.0.0.1:5000'

session = requests.Session()

# Step 1: Get CSRF token from form page
print("Getting form page...")
response = session.get(f'{BASE_URL}/guarantorundertaking')
if response.status_code != 200:
    print(f"ERROR: Could not get form page (status {response.status_code})")
    exit(1)

# Extract CSRF token using regex
csrf_match = re.search(r'name="csrf_token"\s+value="([^"]+)"', response.text)
if not csrf_match:
    print("ERROR: Could not find CSRF token in form")
    exit(1)

csrf_value = csrf_match.group(1)
print(f"✓ Got CSRF token: {csrf_value[:30]}...")

# Step 2: Submit form with test data
print("\nSubmitting guarantor undertaking form...")
form_data = {
    'form_type': 'guarantorundertaking',
    'csrf_token': csrf_value,
    'guarantor_full_name': 'Test Guarantor',
    'guarantor_phone': '08099180391',
    'guarantor_email': 'guarantor@test.com',
    'guarantor_address': '123 Test Street',
    'client_name': 'Test Client',
    'client_email': 'client@test.com',
    'clientSignatureData': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==',
}

response = session.post(
    f'{BASE_URL}/submit-form',
    data=form_data,
    files={}
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text[:500]}")

if response.status_code == 200:
    import json
    try:
        result = response.json()
        print(f"\n✓ Response JSON:")
        print(f"  Success: {result.get('success')}")
        print(f"  Message: {result.get('message')}")
    except:
        print(f"Could not parse JSON response")
else:
    print(f"ERROR: Unexpected status code {response.status_code}")
