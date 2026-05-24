#!/usr/bin/env python
"""Test to diagnose approval form submission issues"""

import requests
import json
import base64

BASE_URL = "http://127.0.0.1:5000"

def create_blank_png_raw():
    """Create a minimal valid PNG - returns the raw bytes"""
    return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDAT\x08\x99c\xf8\x0f\x00\x00\x01\x01\x00\x00\x15\xc41\xe8\xe2\x00\x00\x00\x00IEND\xaeB`\x82'

def diagnose_submission():
    """Diagnose why the form isn't submitting"""
    
    session = requests.Session()
    
    print("\n" + "="*70)
    print("APPROVAL FORM SUBMISSION DIAGNOSIS")
    print("="*70)
    
    # Step 1: Login
    print("\nStep 1: Logging in as admin...")
    login_resp = session.post(
        f"{BASE_URL}/admin_login",
        data={'username': 'admin', 'password': 'admin123'},
        allow_redirects=True
    )
    print(f"✓ Login response: {login_resp.status_code}")
    
    # Step 2: Get the form page to understand its structure
    print("\nStep 2: Getting approval form page...")
    form_page = session.get(f"{BASE_URL}/admin/approve-agreement/1")
    print(f"✓ Form page status: {form_page.status_code}")
    
    # Check form action URL and method
    if 'form' in form_page.text.lower():
        if 'action=' in form_page.text:
            import re
            action_match = re.search(r'action=["\']([^"\']*)["\']', form_page.text)
            method_match = re.search(r'method=["\']([^"\']*)["\']', form_page.text)
            form_action = action_match.group(1) if action_match else "NOT FOUND"
            form_method = method_match.group(1) if method_match else "NOT FOUND"
            print(f"✓ Form action: {form_action}")
            print(f"✓ Form method: {form_method}")
    
    # Step 3: Submit with different signature formats
    print("\nStep 3: Testing with base64-encoded PNG...")
    png_bytes = create_blank_png_raw()
    sig_base64 = base64.b64encode(png_bytes).decode('utf-8')
    
    # Try with data URL format
    sig_data_url = f'data:image/png;base64,{sig_base64}'
    
    approval_data = {
        'approver_name': 'Test Admin',
        'approver_email': 'test@phemedaa.com',
        'approver_position': 'Manager',
        'signature_data': sig_data_url
    }
    
    print(f"signature_data length: {len(sig_data_url)} chars")
    print(f"signature_data sample: {sig_data_url[:100]}...")
    
    submit_resp = session.post(
        f"{BASE_URL}/admin/approve-agreement/1",
        data=approval_data,
        allow_redirects=False
    )
    
    print(f"\n✓ Submit response status: {submit_resp.status_code}")
    print(f"✓ Location header: {submit_resp.headers.get('Location', 'NONE')}")
    
    # If it's a redirect, follow it to see what error message is shown
    if submit_resp.status_code in [301, 302, 303, 307, 308]:
        redirect_url = submit_resp.headers.get('Location')
        print(f"\n✓ Following redirect to: {redirect_url}")
        
        redirect_resp = session.get(redirect_url if redirect_url.startswith('http') else BASE_URL + redirect_url)
        print(f"✓ Redirect response status: {redirect_resp.status_code}")
        
        # Check for error messages
        if 'flash' in redirect_resp.text or 'alert' in redirect_resp.text:
            # Extract error messages
            import re
            errors = re.findall(r'<li>([^<]+)</li>', redirect_resp.text)
            if errors:
                print(f"\n⚠️  ERROR MESSAGES FOUND:")
                for error in errors:
                    print(f"  - {error}")
            
            # Look for any text that says "required", "invalid", "error"
            if 'required' in redirect_resp.text.lower():
                print(f"\n⚠️  Form validation error: Something is marked as REQUIRED")
            if 'invalid' in redirect_resp.text.lower():
                print(f"\n⚠️  Form validation error: Something is marked as INVALID")
    else:
        print(f"Response text (first 500 chars):\n{submit_resp.text[:500]}")

if __name__ == '__main__':
    try:
        diagnose_submission()
        print("\n" + "="*70 + "\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
