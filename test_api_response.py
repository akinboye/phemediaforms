import requests
import json

# Test the endpoint
response = requests.get('http://127.0.0.1:5000/admin/submissions/trackingagreement', 
                       cookies={'admin_logged_in': 'true'})

print("Status Code:", response.status_code)
print("\nResponse JSON:")
data = response.json()
print(json.dumps(data, indent=2))

if data['submissions']:
    sub = data['submissions'][0]
    print("\n\nFirst submission details:")
    for key in sub:
        print(f"  {key}: {sub[key]}")
