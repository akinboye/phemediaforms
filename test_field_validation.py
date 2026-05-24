#!/usr/bin/env python
"""Test to find which field is being rejected"""

import requests
import base64
import re

BASE_URL = "http://127.0.0.1:5000"

def test_field_validation():
    """Test each field to find which one is failing"""
    
    session = requests.Session()
    
    print("\n" + "="*70)
    print("FIELD-BY-FIELD VALIDATION TEST")
    print("="*70)
    
    # Login first
    session.post(
        f"{BASE_URL}/admin_login",
        data={'username': 'admin', 'password': 'admin123'},
        allow_redirects=True
    )
    
    png_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDAT\x08\x99c\xf8\x0f\x00\x00\x01\x01\x00\x00\x15\xc41\xe8\xe2\x00\x00\x00\x00IEND\xaeB`\x82'
    sig_base64 = base64.b64encode(png_bytes).decode('utf-8')
    sig_data_url = f'data:image/png;base64,{sig_base64}'
    
    # Test 1: All fields
    print("\n1️⃣  Testing with ALL fields supplied:")
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
    error_text = resp.text
    if 'Approver name is required' in error_text:
        print("   ❌ NAME field rejected")
    elif 'approver email' in error_text.lower():
        print("   ❌ EMAIL field rejected")
    elif 'position' in error_text.lower():
        print("   ❌ POSITION field rejected")
    elif 'signature' in error_text.lower():
        print("   ❌ SIGNATURE field rejected")
    else:
        print("   ✓ Some other error or success")
    
    # Test 2: Without name
    print("\n2️⃣  Testing WITHOUT name:")
    resp = session.post(
        f"{BASE_URL}/admin/approve-agreement/1",
        data={
            'approver_name': '',
            'approver_email': 'test@phemedaa.com',
            'approver_position': 'Manager',
            'signature_data': sig_data_url
        },
        allow_redirects=True
    )
    if 'Approver name is required' in resp.text:
        print("   ✓ NAME validation WORKING (correctly rejected empty name)")
    else:
        print("   ⚠️  NAME validation not triggering for empty name")
    
    # Test 3: Without email
    print("\n3️⃣  Testing WITHOUT email:")
    resp = session.post(
        f"{BASE_URL}/admin/approve-agreement/1",
        data={
            'approver_name': 'Test Admin',
            'approver_email': '',
            'approver_position': 'Manager',
            'signature_data': sig_data_url
        },
        allow_redirects=True
    )
    if 'email' in resp.text.lower():
        print("   ✓ EMAIL validation WORKING")
    else:
        print("   ⚠️  EMAIL validation needs checking")
    
    # Test 4: Without position
    print("\n4️⃣  Testing WITHOUT position:")
    resp = session.post(
        f"{BASE_URL}/admin/approve-agreement/1",
        data={
            'approver_name': 'Test Admin',
            'approver_email': 'test@phemedaa.com',
            'approver_position': '',
            'signature_data': sig_data_url
        },
        allow_redirects=True
    )
    if 'position' in resp.text.lower():
        print("   ✓ POSITION validation WORKING")
    else:
        print("   ⚠️  POSITION validation needs checking")
    
    # Test 5: Without signature
    print("\n5️⃣  Testing WITHOUT signature:")
    resp = session.post(
        f"{BASE_URL}/admin/approve-agreement/1",
        data={
            'approver_name': 'Test Admin',
            'approver_email': 'test@phemedaa.com',
            'approver_position': 'Manager',
            'signature_data': ''
        },
        allow_redirects=True
    )
    if 'signature' in resp.text.lower():
        print("   ✓ SIGNATURE validation WORKING")
    else:
        print("   ⚠️  SIGNATURE validation needs checking")
    
    # Test 6: All fields present - extract any error message
    print("\n6️⃣  Full submission - checking final response:")
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
    
    # Look for ANY flash message or error
    messages = re.findall(r'<li>([^<]+?)</li>', resp.text)
    if messages:
        print("   Flash messages found:")
        for msg in messages:
            print(f"     - {msg}")
    else:
        print("   No flash messages found")
    
    # Check if page contains error-related text
    if 'required' in resp.text.lower():
        print("   'required' text found in response")
    if 'error' in resp.text.lower():
        print("   'error' text found in response")

if __name__ == '__main__':
    test_field_validation()
