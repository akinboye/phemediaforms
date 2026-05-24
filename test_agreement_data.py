from app import app, db, FormSubmission

with app.app_context():
    # Find serviceagreement submissions
    submissions = FormSubmission.query.filter_by(form_type='serviceagreement').all()
    print('Total serviceagreement submissions: {}'.format(len(submissions)))
    
    # Print last 3
    for sub in submissions[-3:]:
        print('\nSubmission {}:'.format(sub.id))
        print('  Email: {}'.format(sub.user_email))
        print('  Token: {}'.format(sub.client_acceptance_token))
        print('  Has submitted_data: {}'.format(sub.submitted_data is not None))
        if sub.submitted_data:
            print('  Data keys: {}'.format(list(sub.submitted_data.keys())))
            if 'scope_of_services' in sub.submitted_data:
                scope = sub.submitted_data['scope_of_services']
                if scope:
                    print('  Scope of Services: {}...'.format(scope[:50]))
                else:
                    print('  Scope of Services: (empty)')
