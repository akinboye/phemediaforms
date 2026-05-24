#!/usr/bin/env python
"""Test to show the actual response content with error messages"""

import requests
import base64
import re

BASE_URL = "http://127.0.0.1:5000"

def test_with_response_body():
    """Test and print the actual response body"""
    
    session = requests.Session()
    
    # Login first
    session.post(
        f"{BASE_URL}/admin_login",
        data={'username': 'admin', 'password': 'admin123'},
        allow_redirects=True
    )
    
    png_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDAT\x08\x99c\xf8\x0f\x00\x00\x01\x01\x00\x00\x15\xc41\xe8\xe2\x00\x00\x00\x00IEND\xaeB`\x82'
    sig_base64 = base64.b64encode(png_bytes).decode('utf-8')
    sig_data_url = f'data:image/png;base64,{sig_base64}'
    
    print("\n" + "="*70)
    print("TESTING WITH FULL RESPONSE BODY")
    print("="*70)
    
    print("\nSubmitting with:")
    print(f"  name: 'Test Admin'")
    print(f"  email: 'test@phemedaa.com'")
    print(f"  position: 'Manager'")
    print(f"  signature_data: {sig_data_url[:60]}...")
    
    resp = session.post(
        f"{BASE_URL}/admin/approve-agreement/1",
        data={
            'approver_name': 'Test Admin',
            'approver_email': 'test@phemedaa.com',
            'approver_position': 'Manager',
            'signature_data': sig_data_url
        },
        allow_redirects=True
    )
    
    print(f"\nResponse status: {resp.status_code}")
    print(f"Final URL: {resp.url}")
    
    # Extract flash messages
    flash_pattern = r'<li[^>]*>([^<]+)</li>'
    flashes = re.findall(flash_pattern, resp.text)
    
    if flashes:
        print(f"\n⚠️  FLASH MESSAGES FOUND:")
        for msg in flashes:
            print(f"  - {msg}")
    else:
        print("\n✓ No flash messages found")
    
    # Look for error-related text in the response
    if 'error' in resp.text.lower():
        print("✓ 'error' text found in response")
    if 'required' in resp.text.lower():
        print("✓ 'required' text found in response")
    
    # Check if we're still on the approval form page
    if 'Approve Service Agreement' in resp.text or 'approver_name' in resp.text:
        print("\n✓ Still on approval form page (form not submitted)")
        
        # Print the HTML to understand the structure
        print("\nSearching for specific form validation errors...")
        
        # Get the form section
        form_start = resp.text.find('<form id="approvalForm"')
        if form_start > -1:
            form_end = resp.text.find('</form>', form_start)
            form_html = resp.text[form_start:form_end+7]
            
            # Look for any error messages in the form
            if '<li>' in form_html:
                print("✓ Found error list items in form")
            
            # Print a snippet of the response around error messages
            error_patterns = ['Approver name', 'approver email', 'position', 'signature', 'Error', 'error']
            for pattern in error_patterns:
                if pattern in resp.text:
                    idx = resp.text.find(pattern)
                    print(f"\nFound '{pattern}' at position {idx}")
                    print(f"  Context: ...{resp.text[max(0, idx-50):idx+100]}...")
    else:
        print("\n✓ Redirected away from form page (form may have been processed)")

if __name__ == '__main__':
    test_with_response_body()
