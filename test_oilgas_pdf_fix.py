#!/usr/bin/env python3
"""Test script to verify oil & gas PDF generation fix"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db, FormSubmission, generate_oilgasservicerequest_approval_pdf
from datetime import datetime

with app.app_context():
    # Find a pending approval submission
    submission = FormSubmission.query.filter_by(
        form_type='oilgasservicerequest',
        status='pending_approval'
    ).first()
    
    if not submission:
        print("❌ No pending oil & gas submissions found")
        # Try to find any oil & gas submission to test
        submission = FormSubmission.query.filter_by(
            form_type='oilgasservicerequest'
        ).first()
        
        if submission:
            print(f"📝 Found submission {submission.id} with status: {submission.status}")
            print("\n📋 Submitted Data:")
            print(f"  - company_name: {submission.submitted_data.get('company_name', 'N/A')}")
            print(f"  - contact_person: {submission.submitted_data.get('contact_person', 'N/A')}")
            print(f"  - client_email: {submission.submitted_data.get('client_email', 'N/A')}")
            print(f"  - client_phone: {submission.submitted_data.get('client_phone', 'N/A')}")
            print(f"  - vessel_destination: {submission.submitted_data.get('vessel_destination', 'N/A')}")
            print(f"  - kickoff_point: {submission.submitted_data.get('kickoff_point', 'N/A')}")
            print(f"  - rig_requirements: {submission.submitted_data.get('rig_requirements', 'N/A')}")
            print(f"  - vessel_rental: {submission.submitted_data.get('vessel_rental', 'N/A')}")
            print(f"  - crew_security_boat: {submission.submitted_data.get('crew_security_boat', 'N/A')}")
            
            # Test PDF generation
            print("\n🔄 Testing PDF generation...")
            try:
                pdf_filename = generate_oilgasservicerequest_approval_pdf(
                    submission.id,
                    approver_name='Test Admin',
                    approver_position='Manager'
                )
                if pdf_filename:
                    print(f"✅ PDF generated successfully: {pdf_filename}")
                    pdf_path = os.path.join('uploads', 'pdfs', pdf_filename)
                    if os.path.exists(pdf_path):
                        print(f"✅ PDF file exists at: {pdf_path}")
                        print(f"   File size: {os.path.getsize(pdf_path)} bytes")
                    else:
                        print(f"❌ PDF file not found at: {pdf_path}")
                else:
                    print("❌ PDF generation returned None")
            except Exception as e:
                print(f"❌ Error generating PDF: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            print("❌ No oil & gas submissions found at all")
    else:
        print(f"✅ Found pending submission {submission.id}")
        print(f"\n📋 Form data:")
        for key, value in submission.submitted_data.items():
            print(f"  - {key}: {value}")
        
        # Test PDF generation
        print("\n🔄 Testing PDF generation...")
        try:
            pdf_filename = generate_oilgasservicerequest_approval_pdf(
                submission.id,
                approver_name='Test Admin',
                approver_position='Manager'
            )
            if pdf_filename:
                print(f"✅ PDF generated successfully: {pdf_filename}")
                pdf_path = os.path.join('uploads', 'pdfs', pdf_filename)
                if os.path.exists(pdf_path):
                    print(f"✅ PDF file exists at: {pdf_path}")
                    print(f"   File size: {os.path.getsize(pdf_path)} bytes")
                else:
                    print(f"❌ PDF file not found at: {pdf_path}")
            else:
                print("❌ PDF generation returned None")
        except Exception as e:
            print(f"❌ Error generating PDF: {str(e)}")
            import traceback
            traceback.print_exc()
