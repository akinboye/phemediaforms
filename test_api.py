#!/usr/bin/env python
"""Test the updated submissions API"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

session = requests.Session()

# Login
session.post(
    f"{BASE_URL}/admin_login",
    data={'username': 'admin', 'password': 'admin123'},
    allow_redirects=True
)

# Get submissions
resp = session.get(f"{BASE_URL}/admin/submissions/serviceagreement")

print("\n" + "="*70)
print("SUBMISSIONS API RESPONSE")
print("="*70)

data = resp.json()
print(json.dumps(data, indent=2))

print("\n" + "="*70)
print("FIELDS CHECK")
print("="*70)

if data['submissions']:
    for sub in data['submissions']:
        print(f"\nSubmission #{sub['id']}:")
        print(f"  ✓ ID: {sub.get('id')}")
        print(f"  ✓ Email: {sub.get('user_email')}")
        print(f"  ✓ Status: {sub.get('status')} (NEW!)")
        print(f"  ✓ PDF: {sub.get('pdf_filename')} (NEW!)")
        print(f"  ✓ Submitted at: {sub.get('submitted_at')}")
