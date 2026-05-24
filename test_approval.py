#!/usr/bin/env python
"""Test script to verify approval form submission works with config fix"""

import requests
import json
import base64

BASE_URL = "http://127.0.0.1:5000"

def test_approval_submission():
    """Test posting to the approval endpoint"""
    
    # First, create a blank signature (1x1 PNG)
    blank_png = base64.b64encode(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDAT\x08\x99c\xf8\x0f\x00\x00\x01\x01\x00\x00\x15\xc41\xe8\xe2\x00\x00\x00\x00IEND\xaeB`\x82').decode('utf-8')
    
    # Prepare form data
    form_data = {
        'approver_name': 'Test Admin',
        'approver_email': 'admin@phemedaa.com',
        'approver_position': 'Operations Manager',
        'approvalSignatureData': f'data:image/png;base64,{blank_png}'
    }
    
    try:
        # Submit the form
        print("Submitting approval form...")
        response = requests.post(
            f"{BASE_URL}/admin/approve-agreement/1",
            data=form_data,
            allow_redirects=False,
            timeout=10
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 302:
            print("✅ Form submitted successfully (got redirect 302)")
            print(f"Redirected to: {response.headers.get('Location')}")
            return True
        elif response.status_code == 200:
            print("❌ Got 200 instead of redirect - form may have re-displayed with error")
            if 'error' in response.text.lower() or 'stamps_folder' in response.text.lower():
                print("❌ ERROR: STAMPS_FOLDER error still present!")
                return False
            return True
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return False

if __name__ == '__main__':
    print("Testing approval form submission...")
    print("=" * 60)
    success = test_approval_submission()
    print("=" * 60)
    if success:
        print("✅ TEST PASSED - Config fix appears to be working!")
    else:
        print("❌ TEST FAILED - Check Flask logs for details")
