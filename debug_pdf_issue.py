#!/usr/bin/env python3
"""Debug PDF generation issue"""

from app import app, db, FormSubmission, generate_oilgasservicerequest_approval_pdf
import os

with app.app_context():
    sub29 = FormSubmission.query.get(29)
    if sub29:
        print('Submission 29 Data:')
        print(f'  Status: {sub29.status}')
        print(f'  Form Type: {sub29.form_type}')
        print()
        print('Form data keys:', list(sub29.submitted_data.keys()))
        print()
        print('All submitted data:')
        for key, value in sub29.submitted_data.items():
            if isinstance(value, str):
                print(f'  {key}: {value[:100] if len(str(value)) > 100 else value}')
            else:
                print(f'  {key}: {value}')
        print()
        
        # Now test PDF generation with debug output
        print('Testing PDF generation with debug:')
        form_data = sub29.submitted_data
        
        # Check what values we're getting
        print(f'  client_phone: {form_data.get("client_phone", "MISSING")}')
        print(f'  phone: {form_data.get("phone", "MISSING")}')
        print(f'  service_required: {form_data.get("service_required", "MISSING")}')
        print(f'  location: {form_data.get("location", "MISSING")}')
        print(f'  vessel_destination: {form_data.get("vessel_destination", "MISSING")}')
        print(f'  kickoff_point: {form_data.get("kickoff_point", "MISSING")}')
        print(f'  rig_requirements: {form_data.get("rig_requirements", "MISSING")}')
        print(f'  vessel_rental: {form_data.get("vessel_rental", "MISSING")}')
        print(f'  crew_security_boat: {form_data.get("crew_security_boat", "MISSING")}')
        print()
        
        # Generate PDF
        pdf_file = generate_oilgasservicerequest_approval_pdf(29, 'Test Admin', 'Manager')
        print(f'  Generated: {pdf_file}')
        
        if pdf_file:
            pdf_path = os.path.join('uploads', 'agreements', pdf_file)
            print(f'  Path: {pdf_path}')
            print(f'  Exists: {os.path.exists(pdf_path)}')
