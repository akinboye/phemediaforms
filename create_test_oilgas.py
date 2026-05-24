from app import app, db, FormSubmission
from datetime import datetime
import uuid

with app.app_context():
    # Create a test oil & gas submission as if an admin submitted it
    test_data = {
        'csrf_token': 'test_token',
        'company_name': 'Test Oil Company Ltd',
        'contact_person': 'John Smith',
        'position_title': 'Operations Manager',
        'client_email': 'test.client@oilcompany.com',
        'client_phone': '+234 800 1234 567',
        'proof_of_product': 'POL-2026-001',
        'bill_of_lading': 'BOL-2026-5432',
        'charterer_background': 'Verified',
        'swamp_drilling_rig': 'yes',
        'rig_requirements': 'Standard drilling rig with capacity for 100+ personnel',
        'vessel_rental': 'Fast Attack Vessel (FAV), 20 personnel capacity',
        'crew_security_boat': 'yes',
        'security_crew_count': '25',
        'contract_duration': '30 days',
        'vessel_destination': 'Lagos Port, Nigeria',
        'kickoff_point': 'Warri Port, Nigeria',
        'additional_info': 'High security requirement due to sensitive cargo',
        'estimated_timeline': '3-5_days'
    }
    
    token = str(uuid.uuid4())
    link = f'http://127.0.0.1:5000/oilgasservicerequest/sign/{token}'
    
    submission = FormSubmission(
        form_type='oilgasservicerequest',
        submitted_data=test_data,
        user_email='admin@phemedia.com',
        status='pending_approval',
        client_acceptance_token=token,
        client_acceptance_link=link
    )
    
    db.session.add(submission)
    db.session.commit()
    
    print('Test submission created:')
    print('  ID: {}'.format(submission.id))
    print('  Token: {}'.format(token))
    print('  Link: {}'.format(link))
