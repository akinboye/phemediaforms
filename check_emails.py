#!/usr/bin/env python3
"""Check notification emails configuration"""
from app import app, db
from models import NotificationEmail

app.app_context().push()

emails = NotificationEmail.query.filter(
    (NotificationEmail.form_type == 'guarantorundertaking') | (NotificationEmail.form_type == 'all'),
    NotificationEmail.is_active == True
).all()

print(f"Active notification emails for guarantorundertaking: {len(emails)}")
for e in emails:
    print(f"  - {e.email} (form_type: {e.form_type}, active: {e.is_active})")

if len(emails) == 0:
    print("\nNo notification emails configured. Will fall back to admin email.")
    from app import ADMIN_EMAIL
    print(f"ADMIN_EMAIL: {ADMIN_EMAIL}")
