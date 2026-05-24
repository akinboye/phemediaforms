#!/usr/bin/env python
"""Test approval with weasyprint installed - fixed version"""

import requests
import os

BASE_URL = "http://127.0.0.1:5000"
session = requests.Session()

# Login as admin
print("1. Logging in...")
resp = session.post(
    f"{BASE_URL}/admin_login",
    data={'username': 'admin', 'password': 'admin123'},
    allow_redirects=True
)
print(f"   Login status: {resp.status_code}")

# Get approval form to verify it loads
print("\n2. Loading approval form...")
resp = session.get(f"{BASE_URL}/approve/serviceagreement/1")
print(f"   Form load status: {resp.status_code}")

# Try to approve submission 1
print("\n3. Approving submission #1...")
sig = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

approval_resp = session.post(
    f"{BASE_URL}/process_approval_admin",
    json={
        'submission_id': 1,
        'approver_name': 'John Approver',
        'approver_email': 'approver@phemedia.com',
        'approver_position': 'Manager',
        'signature': sig,
        'upload_method': 'draw'
    }
)

print(f"   Approval response status: {approval_resp.status_code}")
print(f"   Approval response: {approval_resp.text[:200]}")

# Check file system
print("\n" + "="*70)
print("FILE SYSTEM CHECK (checking for PDF files)")
print("="*70)

pdf_dir = './uploads/agreements'
if os.path.exists(pdf_dir):
    files = sorted(os.listdir(pdf_dir))
    print(f"\nFiles in {pdf_dir}:")
    for f in files:
        fpath = os.path.join(pdf_dir, f)
        size = os.path.getsize(fpath)
        ext = os.path.splitext(f)[1]
        status = "✓" if size > 1000 and ext == '.pdf' else "✗"
        print(f"  {status} {f}: {size:,} bytes")
else:
    print(f"{pdf_dir} does not exist")

# Check database using shell
print("\n" + "="*70)
print("DATABASE CHECK")
print("="*70)

check_resp = session.get(f"{BASE_URL}/admin/submissions/serviceagreement")
if check_resp.status_code == 200:
    data = check_resp.json()
    if data['submissions']:
        for sub in data['submissions'][:2]:  # Show first 2
            print(f"\nSubmission #{sub['id']}:")
            print(f"  Status: {sub['status']}")
            print(f"  PDF: {sub['pdf_filename']}")
    else:
        print("No submissions found")
else:
    print(f"Failed to check submissions: {check_resp.status_code}")
