#!/usr/bin/env python3
"""Test script for declarationbyemployee form with file uploads"""
import requests
import json
import io
from datetime import datetime
from PIL import Image

BASE_URL = "http://127.0.0.1:5000"

def create_test_image():
    """Create a simple test image"""
    img = Image.new('RGB', (100, 100), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

def test_declaration_with_files():
    """Test employee declaration with file uploads"""
    print("\n" + "="*60)
    print("Testing Employee Declaration Form with Files")
    print("="*60)
    
    # Create test images
    print("\n1. Creating test files...")
    photo = create_test_image()
    nin_doc = create_test_image()
    print("✓ Test photo and NIN document created")
    
    # Form data
    form_data = {
        'form_type': 'declarationbyemployee',
        'employee_full_name': 'John Test Employee',
        'father_name': 'Test Father Name',
        'employee_dob': '1990-05-15',
        'employee_residential_address': '123 Test Street, Test City',
        'employee_phone': '08099180391',
        'position_applied': 'Security Officer',
        'employee_email': 'testemployee@test.com',
        'comply_rules': 'on',
        'punctuality': 'on',
        'good_conduct': 'on',
        'notice_period': 'on',
        'sabotage_prohibition': 'on',
        'confidentiality': 'on',
        'lawful_orders': 'on',
        'equipment_care': 'on',
        'clientSignatureData': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==',
        'declaration_date': datetime.now().strftime('%Y-%m-%d')
    }
    
    files = {
        'employee_photograph': ('test_photo.png', photo, 'image/png'),
        'employee_nin': ('test_nin.png', nin_doc, 'image/png')
    }
    
    print("\n2. Submitting form with files...")
    try:
        response = requests.post(
            f"{BASE_URL}/submit-form",
            data=form_data,
            files=files,
            headers={'X-CSRFToken': 'test'}
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response Message: {result.get('message')}")
            print(f"Full Response: {json.dumps(result, indent=2)}")
            if result.get('success'):
                submission_id = result.get('submission_id')
                print(f"✅ Form submitted successfully!")
                print(f"   Submission ID: {submission_id}")
                print(f"   Message: {result.get('message')}")
                return True, submission_id
            else:
                print(f"❌ Submission failed: {result.get('message')}")
                return False, None
        else:
            print(f"❌ Server error: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False, None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None

if __name__ == '__main__':
    success, submission_id = test_declaration_with_files()
    
    if success:
        print("\n" + "="*60)
        print("✅ SUCCESS - Form accepted by server!")
        print("="*60)
        print(f"\nNext: Check admin dashboard for submission #{submission_id}")
        print("Verify:")
        print("  ✓ Email is displayed correctly")
        print("  ✓ NIN download column is visible")
        print("  ✓ Photo download is available")
