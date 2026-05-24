import requests
from requests.cookies import RequestsCookieJar

# Create a cookie jar with admin session
cookies = RequestsCookieJar()
cookies.set('admin_logged_in', 'true')

try:
    response = requests.get('http://127.0.0.1:5000/admin/submissions/trackingagreement', 
                           cookies=cookies,
                           timeout=5)
    
    print("Status:", response.status_code)
    data = response.json()
    
    if data.get('submissions'):
        sub = data['submissions'][0]
        print("\nFirst submission fields:")
        for key in sorted(sub.keys()):
            value = sub[key]
            if key in ['client_acceptance_link', 'client_acceptance_token', 'client_acceptance_completed']:
                print(f"  {key}: {value}")
    else:
        print("No submissions found")
        
except Exception as e:
    print(f"Error: {e}")
