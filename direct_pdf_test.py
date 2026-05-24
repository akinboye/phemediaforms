#!/usr/bin/env python
"""Direct call to the PDF generation function"""

import sys
import os
sys.path.insert(0, '.')

from app import app, db, FormSubmission, generate_service_agreement_pdf
from datetime import datetime

with app.app_context():
    submission = FormSubmission.query.get(2)
    if submission:
        print(f"Testing PDF generation for submission #{submission.id}")
        
        # Create test output path
        output_path = f'./uploads/agreements/test_direct_{submission.id}.pdf'
        
        print(f"Output path: {output_path}")
        print(f"Directory exists: {os.path.exists(os.path.dirname(output_path))}")
        
        # Call generate_service_agreement_pdf directly
        result = generate_service_agreement_pdf(
            submission_id=submission.id,
            stamp_path=None,
            output_path=output_path,
            approver_name="Test Approver",
            approver_email="test@example.com",
            approver_position="Manager"
        )
        
        print(f"\nResult: {result}")
        print(f"File exists: {os.path.exists(output_path)}")
        if os.path.exists(output_path):
            size = os.path.getsize(output_path)
            print(f"File size: {size:,} bytes")
    else:
        print("Submission #2 not found")
