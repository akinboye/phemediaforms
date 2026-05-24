#!/usr/bin/env python3
"""Verify PDF header layout"""

from pypdf import PdfReader
import os

pdf_path = "uploads/agreements/background_checks_approval_3_20260504_235510.pdf"

if os.path.exists(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        page = reader.pages[0]
        
        print("✅ PDF file verified!")
        print(f"📄 File: {pdf_path}")
        print(f"📏 Page count: {len(reader.pages)}")
        
        # Get page dimensions
        page_width = float(page.mediabox.width)
        page_height = float(page.mediabox.height)
        print(f"📐 Dimensions: {page_width} x {page_height} points")
        
        # Extract text
        text = page.extract_text()
        lines = text.split('\n')[:10]
        print(f"\n📝 First 10 lines of text:")
        for i, line in enumerate(lines, 1):
            print(f"   {i}. {line[:80]}")
            
        # Check for expected content
        if "PHEMEDIA ONGUARD SERVICES LTD" in text:
            print("\n✅ Company header found")
        if "BACKGROUND CHECK SERVICE AGREEMENT" in text:
            print("✅ Form title found")
        if "Approved & Certified Document" in text:
            print("✅ Subtitle found")
            
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")
else:
    print(f"❌ PDF not found: {pdf_path}")
