import json
from TaskFlow import app as package
app = package.app
client = app.test_client()

endpoints = ['/', '/register', '/login', '/dashboard', '/tasks', '/api/tasks']
results = {}

def get_title(data):
    if not data:
        return None
    s = data.decode('utf-8', errors='replace')
    start = s.find('<title>')
    if start != -1:
        start += 7
        end = s.find('</title>', start)
        if end != -1:
            return s[start:end].strip()
    return None

for ep in endpoints:
    resp = client.get(ep, follow_redirects=False)
    item = {
        'status_code': resp.status_code,
        'headers': {k: v for k, v in resp.headers.items()},
        'title': get_title(resp.data),
        'snippet': resp.data.decode('utf-8', errors='replace')[:500]
    }
    results[ep] = item

with open('smoke_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

print('Smoke test written to smoke_results.json')
