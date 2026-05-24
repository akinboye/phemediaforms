#!/usr/bin/env python3
"""Check submission data for PDF generation"""

from app import app, db, FormSubmission

with app.app_context():
    # Check submission 22
    sub = FormSubmission.query.get(22)
    if sub:
        print('Submission 22:')
        print(f'  Form Type: {sub.form_type}')
        print(f'  Status: {sub.status}')
        print(f'  Company: {sub.submitted_data.get("company_name", "N/A")}')
        print(f'  Contact: {sub.submitted_data.get("contact_person", "N/A")}')
        print(f'  Email: {sub.submitted_data.get("client_email", "N/A")}')
        print(f'  Phone (client_phone): {sub.submitted_data.get("client_phone", "N/A")}')
        print(f'  Phone (phone): {sub.submitted_data.get("phone", "N/A")}')
        print(f'  Service: {sub.submitted_data.get("service_required", "N/A")}')
        print(f'  Location: {sub.submitted_data.get("location", "N/A")}')
        print(f'  Vessel Destination: {sub.submitted_data.get("vessel_destination", "N/A")}')
        print(f'  Kickoff Point: {sub.submitted_data.get("kickoff_point", "N/A")}')
        print(f'  PDF: {sub.pdf_filename}')
        print()
    
    # Also check submission 29
    sub29 = FormSubmission.query.get(29)
    if sub29:
        print('Submission 29:')
        print(f'  Form Type: {sub29.form_type}')
        print(f'  Status: {sub29.status}')
        print(f'  Company: {sub29.submitted_data.get("company_name", "N/A")}')
        print(f'  Contact: {sub29.submitted_data.get("contact_person", "N/A")}')
        print(f'  Email: {sub29.submitted_data.get("client_email", "N/A")}')
        print(f'  Phone (client_phone): {sub29.submitted_data.get("client_phone", "N/A")}')
        print(f'  Phone (phone): {sub29.submitted_data.get("phone", "N/A")}')
        print(f'  Service: {sub29.submitted_data.get("service_required", "N/A")}')
        print(f'  Location: {sub29.submitted_data.get("location", "N/A")}')
        print(f'  Vessel Destination: {sub29.submitted_data.get("vessel_destination", "N/A")}')
        print(f'  Kickoff Point: {sub29.submitted_data.get("kickoff_point", "N/A")}')
        print(f'  PDF: {sub29.pdf_filename}')
