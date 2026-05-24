#!/usr/bin/env python
"""Direct test of PDF generation with fpdf2"""

import sys
import os
sys.path.insert(0, '.')

# Set up Flask app for database access
from app import app, db, FormSubmission, CompanyAddress, generate_service_agreement_pdf

with app.app_context():
    # Test PDF generation directly
    submission_id = 1
    submission = FormSubmission.query.get(submission_id)
    
    if submission:
        print(f"Found submission #{submission_id}")
        
        # Create test directory if needed
        test_output = './test_pdf.pdf'
        
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Test PDF generation
        print("\nTesting PDF generation...")
        result = generate_service_agreement_pdf(
            submission_id,
            stamp_path=None,
            output_path=test_output,
            approver_name="Test Approver",
            approver_email="test@example.com",
            approver_position="Manager"
        )
        
        print(f"PDF generation result: {result}")
        
        if os.path.exists(test_output):
            size = os.path.getsize(test_output)
            print(f"✓ PDF file created: {test_output}")
            print(f"  File size: {size:,} bytes")
            if size > 0:
                print("  ✓ File is not empty!")
            else:
                print("  ✗ File is empty!")
        else:
            print(f"✗ PDF file not created at {test_output}")
    else:
        print(f"Submission #{submission_id} not found")
