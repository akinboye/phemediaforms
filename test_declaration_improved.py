#!/usr/bin/env python3
"""Test script for declarationbyemployee form with improvements"""
import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"

def test_declaration_submission():
    """Test employee declaration form submission"""
    print("\n" + "="*60)
    print("Testing Employee Declaration Form Submission")
    print("="*60)
    
    # First, get the CSRF token from the form page
    print("\n1. Fetching CSRF token...")
    try:
        response = requests.get(f"{BASE_URL}/declarationbyemployee")
        if response.status_code != 200:
            print(f"❌ Failed to get form page: {response.status_code}")
            return False
        
        # Extract CSRF token from HTML (simplified)
        csrf_token = "test_token"  # Will use the token from the session
        print(f"✓ Got page response (status: {response.status_code})")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    # Create test form data
    print("\n2. Creating test form data...")
    form_data = {
        'form_type': 'declarationbyemployee',
        'employee_full_name': 'John Test Employee',
        'father_name': 'Test Father Name',
        'employee_dob': '1990-05-15',
        'employee_residential_address': '123 Test Street, Test City',
        'employee_phone': '08099180391',
        'position_applied': 'Security Officer',
        'employee_email': 'testemployee@example.com',
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
    print(f"✓ Test data created with email: {form_data['employee_email']}")
    
    # Submit the form
    print("\n3. Submitting form to /submit-form...")
    try:
        files = {}
        response = requests.post(
            f"{BASE_URL}/submit-form",
            data=form_data,
            files=files,
            headers={'X-CSRFToken': 'test'}
        )
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            if result.get('success'):
                submission_id = result.get('submission_id')
                print(f"✓ Form submitted successfully! Submission ID: {submission_id}")
                return True, submission_id
            else:
                print(f"❌ Form submission failed: {result.get('message')}")
                return False, None
        else:
            print(f"❌ Server error: {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Error during submission: {str(e)}")
        return False, None

def check_admin_dashboard():
    """Check admin dashboard to verify improvements"""
    print("\n" + "="*60)
    print("Checking Admin Dashboard")
    print("="*60)
    
    try:
        # Get submissions API
        print("\n1. Fetching declarationbyemployee submissions...")
        response = requests.get(f"{BASE_URL}/admin/submissions/declarationbyemployee")
        
        if response.status_code == 401:
            print("⚠️  Need admin authentication to view submissions")
            print("   Please log in as admin and check the dashboard manually")
            print("   URL: http://127.0.0.1:5000/admin_dashboard")
            return
        
        if response.status_code != 200:
            print(f"❌ Failed to get submissions: {response.status_code}")
            return
        
        data = response.json()
        submissions = data.get('submissions', [])
        
        if submissions:
            print(f"\n✓ Found {len(submissions)} submission(s)")
            latest = submissions[-1]  # Get last submission
            
            print(f"\nLatest Submission Details:")
            print(f"  ID: {latest.get('id')}")
            print(f"  User Email: {latest.get('user_email')}")
            print(f"  Status: {latest.get('status')}")
            print(f"  PDF Filename: {latest.get('pdf_filename')}")
            print(f"  NIN Filename: {latest.get('nin_filename')}")
            print(f"  Photo Filename: {latest.get('photo_filename')}")
            
            # Check what we need
            print(f"\n✅ Email field present: {bool(latest.get('user_email'))}")
            print(f"✅ Can check for PDF after approval")
            print(f"✅ NIN filename tracking: {bool(latest.get('nin_filename'))}")
            print(f"✅ Photo filename tracking: {bool(latest.get('photo_filename'))}")
        else:
            print("⚠️  No submissions found")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == '__main__':
    print("Testing Employee Declaration Form Improvements")
    print(f"Base URL: {BASE_URL}")
    
    # Test submission
    success, submission_id = test_declaration_submission()
    
    if success:
        print("\n" + "="*60)
        print("✅ Form submission successful!")
        print("="*60)
        
        # Check admin dashboard
        check_admin_dashboard()
        
        print("\n" + "="*60)
        print("Next Steps:")
        print("="*60)
        print("1. Log in to admin dashboard: http://127.0.0.1:5000/admin_dashboard")
        print(f"2. Find submission #{submission_id}")
        print("3. Check that:")
        print("   - Employee email is displayed (not N/A)")
        print("   - NIN download column is visible")
        print("   - Can approve the submission")
        print("4. After approval, check:")
        print("   - PDF is generated and available for download")
        print("   - PDF contains the passport photo")
        print("   - Email notification was sent to employee")
    else:
        print("\n❌ Form submission failed. Check server logs.")
