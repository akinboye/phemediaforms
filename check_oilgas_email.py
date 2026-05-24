#!/usr/bin/env python3
"""Check oil & gas submission details"""
from app import app, db, FormSubmission

app.app_context().push()

# Get the latest oil & gas submission
submission = FormSubmission.query.filter_by(form_type='oilgasservicerequest').order_by(FormSubmission.id.desc()).first()

if submission:
    print(f"Submission ID: {submission.id}")
    print(f"Form Type: {submission.form_type}")
    print(f"Status: {submission.status}")
    print(f"User Email: {submission.user_email}")
    print(f"User Email is None/Empty: {not submission.user_email}")
    print(f"\nForm Data Keys: {list(submission.submitted_data.keys())}")
    print(f"\nForm Data (first 500 chars):")
    print(str(submission.submitted_data)[:500])
else:
    print("No oil & gas submission found")
