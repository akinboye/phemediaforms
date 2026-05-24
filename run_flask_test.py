#!/usr/bin/env python
"""Test the approval flow by running app in foreground briefly"""

import subprocess
import time
import requests

# Start Flask in a subprocess
proc = subprocess.Popen(['python', 'app.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, bufsize=1)

# Give Flask time to start
time.sleep(3)

# Run approval test
session = requests.Session()

# Login
session.post(
    "http://127.0.0.1:5000/admin_login",
    data={'username': 'admin', 'password': 'admin123'},
    allow_redirects=False
)

# Approve
resp = session.post(
    "http://127.0.0.1:5000/admin/approve-agreement/1",
    data={
        'approver_name': 'Test',
        'approver_email': 'test@example.com',
        'approver_position': 'Manager',
        'signature_data': "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
        'upload_method': 'draw'
    },
    allow_redirects=False
)

print(f"Approval response: {resp.status_code}")

# Terminate Flask and collect output
proc.terminate()
output, _ = proc.communicate(timeout=5)

print("\n=== Flask Output ===")
print(output)
