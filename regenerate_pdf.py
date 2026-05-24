#!/usr/bin/env python
"""
Script to regenerate PDFs for already-approved submissions
Usage: python regenerate_pdf.py [submission_id]
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db, FormSubmission
from datetime import datetime

def regenerate_pdf_for_submission(submission_id):
    """Regenerate PDF for a specific submission"""
    
    with app.app_context():
        submission = FormSubmission.query.get(submission_id)
        
        if not submission:
            print(f"❌ Submission #{submission_id} not found")
            return False
        
        if submission.form_type != 'backgroundchecks':
            print(f"❌ Submission #{submission_id} is not a backgroundchecks form")
            return False
        
        if submission.status != 'approved':
            print(f"⚠️  Submission #{submission_id} is not approved (Status: {submission.status})")
            return False
        
        print(f"\n📄 Regenerating PDF for Submission #{submission_id}")
        print(f"   Status: {submission.status}")
        print(f"   Approved By: {submission.approver_position if submission.approver_position else 'Unknown'}")
        print(f"   Stamp: {submission.stamp_filename}")
        
        # Import the PDF generation function
        from app import generate_backgroundchecks_approval_pdf
        
        # Build stamp path if it exists
        stamp_path = None
        if submission.stamp_filename:
            stamp_path = os.path.join(app.config['STAMPS_FOLDER'], submission.stamp_filename)
            if not os.path.exists(stamp_path):
                print(f"⚠️  Stamp file not found: {stamp_path}")
                stamp_path = None
        
        # Generate PDF
        pdf_filename = generate_backgroundchecks_approval_pdf(
            submission_id,
            stamp_path=stamp_path,
            approver_name=submission.approver_position or 'Admin',
            approver_email=submission.user_email or 'admin@phemediaa.com',
            approver_position=submission.approver_position or 'Administrator'
        )
        
        if pdf_filename:
            # Update database
            submission.pdf_filename = pdf_filename
            db.session.commit()
            
            pdf_path = os.path.join(app.config['PDFS_FOLDER'], pdf_filename)
            print(f"\n✅ PDF generated successfully!")
            print(f"   Filename: {pdf_filename}")
            print(f"   Path: {pdf_path}")
            print(f"   Size: {os.path.getsize(pdf_path) / 1024:.1f} KB")
            print(f"   Database updated: Yes")
            return True
        else:
            print(f"\n❌ PDF generation failed")
            return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python regenerate_pdf.py <submission_id>")
        print("\nExample: python regenerate_pdf.py 12")
        sys.exit(1)
    
    submission_id = int(sys.argv[1])
    success = regenerate_pdf_for_submission(submission_id)
    sys.exit(0 if success else 1)
