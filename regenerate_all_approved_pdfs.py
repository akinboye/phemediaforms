#!/usr/bin/env python3
"""Regenerate ALL approved submission PDFs with standardized header"""

from app import app, db, FormSubmission
from app import (
    generate_service_agreement_pdf,
    generate_backgroundchecks_approval_pdf,
    generate_clientengagement_approval_pdf,
    generate_declarationbyemployee_approval_pdf,
    generate_guarantorundertaking_approval_pdf,
    generate_oilgasservicerequest_approval_pdf
)

with app.app_context():
    # Map form types to their PDF generation functions
    pdf_generators = {
        'serviceagreement': generate_service_agreement_pdf,
        'backgroundchecks': generate_backgroundchecks_approval_pdf,
        'clientengagement': generate_clientengagement_approval_pdf,
        'declarationbyemployee': generate_declarationbyemployee_approval_pdf,
        'guarantorundertaking': generate_guarantorundertaking_approval_pdf,
        'oilgasservicerequest': generate_oilgasservicerequest_approval_pdf,
    }
    
    # Get all approved submissions
    all_submissions = FormSubmission.query.filter_by(status='approved').all()
    
    print(f"🔄 Found {len(all_submissions)} approved submissions to regenerate\n")
    print("=" * 80)
    
    updated_count = 0
    error_count = 0
    
    # Group by form type for summary
    by_form_type = {}
    
    for submission in all_submissions:
        form_type = submission.form_type
        if form_type not in by_form_type:
            by_form_type[form_type] = []
        by_form_type[form_type].append(submission)
    
    # Process each form type
    for form_type, submissions in sorted(by_form_type.items()):
        print(f"\n📋 {form_type.upper()}")
        print("-" * 80)
        
        if form_type not in pdf_generators:
            print(f"  ⚠️  No PDF generator found for {form_type}")
            continue
        
        pdf_func = pdf_generators[form_type]
        
        for submission in submissions:
            try:
                old_pdf = submission.pdf_filename or "N/A"
                
                # Call appropriate PDF generation function
                if form_type == 'serviceagreement':
                    new_pdf = pdf_func(submission.id)
                elif form_type in ['declarationbyemployee', 'guarantorundertaking', 'oilgasservicerequest']:
                    new_pdf = pdf_func(submission.id, approver_name='Admin', approver_position='Manager')
                else:
                    new_pdf = pdf_func(submission.id, approver_name='Admin', 
                                      approver_email='admin@phemediaa.com',
                                      approver_position='Manager')
                
                if new_pdf:
                    submission.pdf_filename = new_pdf
                    db.session.commit()
                    print(f"  ✅ Sub #{submission.id}: {old_pdf}")
                    print(f"     → {new_pdf}")
                    updated_count += 1
                else:
                    print(f"  ❌ Sub #{submission.id}: Failed to generate PDF")
                    error_count += 1
                    
            except Exception as e:
                print(f"  ❌ Sub #{submission.id}: Error - {str(e)[:60]}")
                error_count += 1
    
    print("\n" + "=" * 80)
    print(f"\n📊 SUMMARY:")
    print(f"   ✅ Updated: {updated_count} PDFs")
    print(f"   ❌ Errors: {error_count} PDFs")
    print(f"   📈 Total: {len(all_submissions)} approved submissions")
    print(f"\n✅ PDF regeneration complete!")
