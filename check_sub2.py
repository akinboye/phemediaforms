#!/usr/bin/env python
"""Check submission 2 pdf_filename"""

from app import app, db, FormSubmission

with app.app_context():
    s = FormSubmission.query.get(2)
    if s:
        print(f"\nSubmission 2:")
        print(f"  Status: {s.status}")
        print(f"  PDF filename: {s.pdf_filename}")
    else:
        print("Submission 2 not found")
