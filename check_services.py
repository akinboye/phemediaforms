#!/usr/bin/env python3
"""Check service fields in submission 29"""

from app import app, db, FormSubmission

with app.app_context():
    sub29 = FormSubmission.query.get(29)
    if sub29:
        print('Service-related fields in submission 29:')
        print(f'  rig_requirements: "{sub29.submitted_data.get("rig_requirements")}"')
        print(f'  vessel_rental: "{sub29.submitted_data.get("vessel_rental")}"')
        print(f'  crew_security_boat: "{sub29.submitted_data.get("crew_security_boat")}"')
        print(f'  service_required: "{sub29.submitted_data.get("service_required")}"')
        print()
        print('All other potentially useful fields:')
        print(f'  contract_duration: {sub29.submitted_data.get("contract_duration")}')
        print(f'  additional_info: {sub29.submitted_data.get("additional_info")}')
