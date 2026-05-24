from app import app, db, FormSubmission

ctx = app.app_context()
ctx.push()

subs = FormSubmission.query.filter_by(form_type='trackingagreement').all()
print(f"Total trackingagreement submissions: {len(subs)}")

for s in subs[:1]:
    print(f"\nID: {s.id}")
    print(f"Client Name: {s.submitted_data.get('client_name') if s.submitted_data else 'N/A'}")
    print(f"Client Email: {s.submitted_data.get('client_email') if s.submitted_data else 'N/A'}")
    print(f"client_acceptance_link: {getattr(s, 'client_acceptance_link', 'ATTR_MISSING')}")
    print(f"client_acceptance_token: {getattr(s, 'client_acceptance_token', 'ATTR_MISSING')}")
    print(f"client_acceptance_completed: {getattr(s, 'client_acceptance_completed', 'ATTR_MISSING')}")
