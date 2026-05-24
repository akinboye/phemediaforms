#!/usr/bin/env python
"""Direct test of approval route"""

import sys
sys.path.insert(0, '.')

from app import app, db, FormSubmission

# Create test context
with app.test_request_context():
    # Check submission 2
    sub = FormSubmission.query.get(2)
    if sub:
        print(f"Submission #2 found:")
        print(f"  Form type: {sub.form_type}")
        print(f"  Status: {sub.status}")
        print(f"  PDF filename: {sub.pdf_filename}")
    else:
        print("Submission #2 not found")
