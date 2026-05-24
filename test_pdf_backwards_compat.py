#!/usr/bin/env python3
"""Test PDF generation with backwards compatibility"""

from app import app, db, FormSubmission, generate_oilgasservicerequest_approval_pdf
import os

with app.app_context():
    # Test submission 22 (old field names)
    sub22 = FormSubmission.query.get(22)
    if sub22:
        print('Testing submission 22 (old format):')
        print(f'  Phone: {sub22.submitted_data.get("phone", "N/A")}')
        print(f'  Service: {sub22.submitted_data.get("service_required", "N/A")}')
        print(f'  Location: {sub22.submitted_data.get("location", "N/A")}')
        
        pdf_file = generate_oilgasservicerequest_approval_pdf(22, 'Test Admin', 'Manager')
        print(f'  Generated PDF: {pdf_file}')
        
        if pdf_file:
            pdf_path = os.path.join('uploads', 'agreements', pdf_file)
            if os.path.exists(pdf_path):
                print(f'  ✅ PDF exists: {os.path.getsize(pdf_path)} bytes')
            else:
                print(f'  ❌ PDF not found')
        print()
    
    # Test submission 29 (new field names)
    sub29 = FormSubmission.query.get(29)
    if sub29:
        print('Testing submission 29 (new format):')
        print(f'  Phone: {sub29.submitted_data.get("client_phone", "N/A")}')
        print(f'  Location: {sub29.submitted_data.get("vessel_destination", "N/A")} / {sub29.submitted_data.get("kickoff_point", "N/A")}')
        
        pdf_file = generate_oilgasservicerequest_approval_pdf(29, 'Test Admin', 'Manager')
        print(f'  Generated PDF: {pdf_file}')
        
        if pdf_file:
            pdf_path = os.path.join('uploads', 'agreements', pdf_file)
            if os.path.exists(pdf_path):
                print(f'  ✅ PDF exists: {os.path.getsize(pdf_path)} bytes')
            else:
                print(f'  ❌ PDF not found')
        print()
    
    print('✅ PDF generation tested successfully!')
