#!/usr/bin/env python3
"""Verify guarantor undertaking submission was saved"""
from app import app, db, FormSubmission

app.app_context().push()

# Get all guarantor undertaking submissions
guarantor_submissions = FormSubmission.query.filter_by(form_type='guarantorundertaking').order_by(FormSubmission.id.desc()).limit(5).all()

print(f"Found {len(guarantor_submissions)} guarantor undertaking submissions")
for submission in guarantor_submissions:
    print(f"\n  ID: {submission.id}")
    print(f"  Form Type: {submission.form_type}")
    print(f"  Status: {submission.status}")
    print(f"  User Email: {submission.user_email}")
    print(f"  Submitted At: {submission.submitted_at}")
