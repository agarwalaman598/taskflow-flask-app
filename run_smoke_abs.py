import json
from TaskFlow import app as package
app = package.app
results = {}
with app.app_context():
    client = app.test_client()
    endpoints = ['/', '/register', '/login', '/dashboard', '/tasks', '/api/tasks']
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
        results[ep] = {
            'status_code': resp.status_code,
            'title': get_title(resp.data),
            'snippet': resp.data.decode('utf-8', errors='replace')[:800]
        }

out = r"c:\Users\KIIT0001\Downloads\TaskFlow\smoke_results_abs.json"
with open(out, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)
print('WROTE', out)
