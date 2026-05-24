#!/usr/bin/env python
"""Test approval with response inspection"""

import requests
import os

BASE_URL = "http://127.0.0.1:5000"
session = requests.Session()

# Login
print("1. Logging in...")
session.post(
    f"{BASE_URL}/admin_login",
    data={'username': 'admin', 'password': 'admin123'},
    allow_redirects=False
)

# Try to approve 
print("\n2. Attempting approval...")
sig = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

resp = session.post(
    f"{BASE_URL}/admin/approve-agreement/2",
    data={
        'approver_name': 'Jane Approver',
        'approver_email': 'jane@phemedia.com',
        'approver_position': 'Director',
        'signature_data': sig,
        'upload_method': 'draw'
    },
    allow_redirects=False
)

print(f"Status code: {resp.status_code}")
print(f"Location header: {resp.headers.get('Location', 'No redirect')}")
print(f"Response text (first 200 chars): {resp.text[:200]}")
