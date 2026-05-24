#!/usr/bin/env python3
"""Update PDF for submission 29 to the latest generated one"""

from app import app, db, FormSubmission, generate_oilgasservicerequest_approval_pdf
import os

with app.app_context():
    sub29 = FormSubmission.query.get(29)
    if sub29:
        old_pdf = sub29.pdf_filename
        print(f'Current PDF: {old_pdf}')
        
        # Regenerate the PDF with the fixed code
        print('\nRegenerating PDF...')
        new_pdf = generate_oilgasservicerequest_approval_pdf(29, 'Admin', 'Manager')
        
        if new_pdf:
            print(f'New PDF: {new_pdf}')
            
            # Update the database
            sub29.pdf_filename = new_pdf
            db.session.commit()
            
            print(f'\n✅ Updated database!')
            print(f'  Old: {old_pdf}')
            
            # Verify it was updated
            db.session.refresh(sub29)
            print(f'  Now: {sub29.pdf_filename}')
