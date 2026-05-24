#!/usr/bin/env python3
"""Regenerate PDFs for all other forms with fixed header"""

from app import app, db, FormSubmission
from app import (
    generate_service_agreement_pdf,
    generate_backgroundchecks_approval_pdf,
    generate_clientengagement_approval_pdf,
    generate_declarationbyemployee_approval_pdf,
    generate_guarantorundertaking_approval_pdf
)

with app.app_context():
    forms_to_update = {
        'serviceagreement': generate_service_agreement_pdf,
        'backgroundchecks': generate_backgroundchecks_approval_pdf,
        'clientengagement': generate_clientengagement_approval_pdf,
        'declarationbyemployee': generate_declarationbyemployee_approval_pdf,
        'guarantorundertaking': generate_guarantorundertaking_approval_pdf,
    }
    
    for form_type, pdf_func in forms_to_update.items():
        # Find an approved submission for this form type
        submission = FormSubmission.query.filter_by(
            form_type=form_type,
            status='approved'
        ).first()
        
        if submission:
            print(f"\n📝 {form_type}:")
            print(f"   Current PDF: {submission.pdf_filename}")
            
            try:
                # Regenerate PDF with default parameters based on form type
                if form_type == 'serviceagreement':
                    new_pdf = pdf_func(submission.id)
                elif form_type in ['declarationbyemployee', 'guarantorundertaking']:
                    new_pdf = pdf_func(submission.id, approver_name='Admin', approver_position='Manager')
                else:
                    new_pdf = pdf_func(submission.id, approver_name='Admin', 
                                      approver_email='admin@phemediaa.com',
                                      approver_position='Manager')
                
                if new_pdf:
                    submission.pdf_filename = new_pdf
                    db.session.commit()
                    print(f"   ✅ Updated: {new_pdf}")
                else:
                    print(f"   ❌ Failed to generate PDF")
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        else:
            print(f"\n⚠️  {form_type}: No approved submissions found")
    
    print("\n✅ PDF regeneration complete!")
