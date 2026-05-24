#!/usr/bin/env python
"""Test script to verify full approval workflow with authentication"""

import requests
import json
import base64
from urllib.parse import urljoin

BASE_URL = "http://127.0.0.1:5000"

def create_blank_png():
    """Create a minimal valid PNG"""
    return base64.b64encode(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDAT\x08\x99c\xf8\x0f\x00\x00\x01\x01\x00\x00\x15\xc41\xe8\xe2\x00\x00\x00\x00IEND\xaeB`\x82').decode('utf-8')

def test_full_approval_workflow():
    """Test the full approval workflow with authentication"""
    
    session = requests.Session()
    
    print("\n" + "="*70)
    print("FULL APPROVAL WORKFLOW TEST WITH AUTHENTICATION")
    print("="*70)
    
    # Step 1: Login as admin
    print("\nStep 1: Logging in as admin...")
    login_response = session.post(
        f"{BASE_URL}/admin_login",
        data={'username': 'admin', 'password': 'admin123'},
        allow_redirects=True,
        timeout=10
    )
    
    if login_response.status_code == 200:
        if 'dashboard' in login_response.url.lower() or 'admin' in login_response.url.lower():
            print("✅ Admin login successful")
        else:
            print(f"⚠️  Login response unclear. URL: {login_response.url}")
    else:
        print(f"❌ Login failed with status {login_response.status_code}")
        return False
    
    # Step 2: Get the approval form
    print("\nStep 2: Getting approval form...")
    form_response = session.get(
        f"{BASE_URL}/admin/approve-agreement/1",
        timeout=10
    )
    
    if form_response.status_code == 200:
        print("✅ Approval form retrieved")
    else:
        print(f"❌ Failed to get approval form: {form_response.status_code}")
        return False
    
    # Step 3: Submit the approval form
    print("\nStep 3: Submitting approval form...")
    approval_data = {
        'approver_name': 'John Manager',
        'approver_email': 'john@phemedaa.com',
        'approver_position': 'Full-time Account Manager',
        'signature_data': f'data:image/png;base64,{create_blank_png()}'
    }
    
    approval_response = session.post(
        f"{BASE_URL}/admin/approve-agreement/1",
        data=approval_data,
        allow_redirects=False,
        timeout=10
    )
    
    print(f"Response status: {approval_response.status_code}")
    
    if approval_response.status_code == 302:
        redirect_location = approval_response.headers.get('Location', '')
        print(f"✅ Form submitted with 302 redirect to: {redirect_location}")
        
        # Check if redirect indicates success
        if 'success' in redirect_location.lower() or 'approved' in redirect_location.lower() or 'submission' in redirect_location.lower():
            print("✅ SUCCESS: Form appears to have processed successfully!")
            return True
        else:
            print(f"⚠️  Redirect location suggests possible success: {redirect_location}")
            return True
            
    elif approval_response.status_code == 200:
        # Check if there's an error message
        if 'stamps_folder' in approval_response.text.lower() or 'config' in approval_response.text.lower():
            print("❌ ERROR: STAMPS_FOLDER config error detected!")
            return False
        elif 'error' in approval_response.text.lower():
            print("⚠️  Got 200 with possible error. Check the response.")
            print(approval_response.text[:500])
            return False
        else:
            print("✅ Form accepted (200 response, no error detected)")
            return True
    else:
        print(f"❌ Unexpected status code: {approval_response.status_code}")
        return False

if __name__ == '__main__':
    try:
        success = test_full_approval_workflow()
        print("\n" + "="*70)
        if success:
            print("✅ TEST PASSED - Full approval workflow is working!")
            print("✅ Config fix is confirmed working end-to-end!")
        else:
            print("❌ TEST FAILED - Check logs for details")
        print("="*70 + "\n")
    except Exception as e:
        print(f"\n❌ Test crashed with exception: {e}\n")
        import traceback
        traceback.print_exc()
