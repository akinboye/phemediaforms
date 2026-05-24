#!/usr/bin/env python3
"""Check what PDF is stored for submission 29"""

from app import app, db, FormSubmission

with app.app_context():
    sub29 = FormSubmission.query.get(29)
    if sub29:
        print(f'Submission 29:')
        print(f'  Status: {sub29.status}')
        print(f'  PDF Filename: {sub29.pdf_filename}')
        print(f'  Approver Name: {sub29.approver_name}')
        print(f'  Approver Email: {sub29.approver_email}')
        
        # List all PDFs for this submission
        import os
        pdf_dir = 'uploads/agreements'
        matching_pdfs = [f for f in os.listdir(pdf_dir) if 'oilgas_approval_29' in f]
        print(f'\n  Available PDFs:')
        for pdf in sorted(matching_pdfs, reverse=True):
            full_path = os.path.join(pdf_dir, pdf)
            size = os.path.getsize(full_path)
            mtime = os.path.getmtime(full_path)
            from datetime import datetime
            dt = datetime.fromtimestamp(mtime)
            print(f'    {pdf} ({size} bytes, {dt})')
