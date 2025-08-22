from TaskFlow import app as package
app = package.app
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
        print(ep, resp.status_code, get_title(resp.data))
        print(resp.data.decode('utf-8', errors='replace')[:400])
        print('---')
