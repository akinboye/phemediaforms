#!/usr/bin/env python
"""Test approval and capture debug output"""

import requests
import os
import time

BASE_URL = "http://127.0.0.1:5000"
session = requests.Session()

# Login
print("1. Logging in...")
session.post(
    f"{BASE_URL}/admin_login",
    data={'username': 'admin', 'password': 'admin123'},
    allow_redirects=True
)

# Approve submission 2 (fresh approval)
print("\n2. Approving submission #2...")
sig = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

resp = session.post(
    f"{BASE_URL}/admin/approve-agreement/2",
    data={
        'approver_name': 'Jane Approver',
        'approver_email': 'jane@phemedia.com',
        'approver_position': 'Director',
        'signature_data': sig,
        'upload_method': 'draw'
    }
)

print(f"Status: {resp.status_code}")

# Wait a bit for file system operations
time.sleep(2)

# Check files
print("\n" + "="*70)
print("CHECK PDF FILES")
print("="*70)

pdf_dir = './uploads/agreements'
if os.path.exists(pdf_dir):
    files = sorted(os.listdir(pdf_dir))
    if files:
        for f in files:
            fpath = os.path.join(pdf_dir, f)
            size = os.path.getsize(fpath)
            print(f"  {f}: {size:,} bytes")
    else:
        print("  (no files)")
else:
    print(f"  Directory doesn't exist: {pdf_dir}")

# Check database
print("\n" + "="*70)
print("CHECK DATABASE")
print("="*70)

check_resp = session.get(f"{BASE_URL}/admin/submissions/serviceagreement")
if check_resp.status_code == 200:
    data = check_resp.json()
    subs = sorted(data['submissions'], key=lambda x: x['id'], reverse=True)
    for sub in subs[:2]:  # Show last 2
        print(f"\nSubmission #{sub['id']}:")
        print(f"  Status: {sub['status']}")
        print(f"  PDF filename: {sub['pdf_filename']}")
