#!/usr/bin/env python
"""Check the submission status"""

import sys
sys.path.insert(0, '/c/Users/maila/Downloads/phemediaaforms/forms')

from app import app, db, FormSubmission

with app.app_context():
    submission = FormSubmission.query.get(1)
    if submission:
        print(f"\nSubmission #1 details:")
        print(f"  Form type: {submission.form_type}")
        print(f"  Status: {submission.status}")
        print(f"  User email: {submission.user_email}")
        print(f"  Approval details:")
        print(f"    - Approved by admin: {submission.approved_by_admin}")
        print(f"    - Approved by superadmin: {submission.approved_by_superadmin}")
        print(f"    - Approved at: {submission.approved_at}")
        print(f"    - Approver position: {submission.approver_position}")
        print(f"    - Stamp filename: {submission.stamp_filename}")
        print(f"    - PDF filename: {submission.pdf_filename}")
    else:
        print("\nSubmission #1 NOT FOUND")
    
    # List all submissions
    print(f"\nAll submissions:")
    all = FormSubmission.query.all()
    for sub in all:
        print(f"  ID: {sub.id}, Form: {sub.form_type}, Status: {sub.status}, Approved at: {sub.approved_at}")
