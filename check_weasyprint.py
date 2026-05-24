#!/usr/bin/env python
"""Check if weasyprint is detected by Flask app"""

import requests

BASE_URL = "http://127.0.0.1:5000"

# Call a route that will trigger print statements
resp = requests.get(f"{BASE_URL}/admin/dashboard")
print(f"Dashboard status: {resp.status_code}")
print("Check the Flask app terminal for HAS_WEASYPRINT detection...")
