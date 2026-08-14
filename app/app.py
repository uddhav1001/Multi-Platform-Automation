from flask import Flask, request, jsonify, render_template_string, redirect
import uuid

app = Flask(__name__)
projects = {
    "company1": [{"id": "seed-c1", "name": "Company1 Demo Project", "description": "Seed project", "status": "active"}],
    "company2": [{"id": "seed-1", "name": "Company2 Demo Project", "description": "Seed project", "status": "active"}],
}
USERS = {
    "admin@company1.com": {"password": "AdminPass123", "tenant": "company1", "role": "Admin"},
    "tenant@company2.com": {"password": "TenantPass123", "tenant": "company2", "role": "Employee"},
}

LOGIN = '''<!doctype html><html><body><h1>WorkFlow Pro Login</h1>
<form method="post"><label>Email<input name="email" id="email"></label>
<label>Password<input name="password" id="password" type="password"></label>
<button id="login-btn" type="submit">Log in</button></form>
{% if error %}<p>{{error}}</p>{% endif %}</body></html>'''
DASH = '''<!doctype html><html><body><div class="welcome-message">Welcome {{email}}</div><h1>Dashboard</h1>
<a href="/projects">Projects</a></body></html>'''
PROJECTS = '''<!doctype html><html><body><h1>Projects</h1>
<form><input name="search" placeholder="Search projects" value="{{q}}"><button>Search</button></form>
{% for p in items %}<div class="project-card"><h2>{{p.name}}</h2><p>{{p.description}}</p><span>{{p.status}}</span></div>{% endfor %}</body></html>'''

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = USERS.get(request.form.get('email'))
        if u and u['password'] == request.form.get('password'):
            from flask import session
            session['email'] = request.form['email']; session['tenant'] = u['tenant']
            return redirect('/dashboard')
        return render_template_string(LOGIN, error='Invalid credentials')
    return render_template_string(LOGIN, error=None)

@app.route('/dashboard')
def dashboard():
    from flask import session
    if 'email' not in session: return redirect('/login')
    return render_template_string(DASH, email=session['email'])

@app.route('/projects')
def projects_page():
    from flask import session
    if 'email' not in session: return redirect('/login')
    q = request.args.get('search','').lower()
    items = [p for p in projects[session['tenant']] if q in p['name'].lower()]
    return render_template_string(PROJECTS, items=items, q=q)

@app.route('/api/v1/projects', methods=['POST'])
def create_project():
    tenant = request.headers.get('X-Tenant-ID')
    auth = request.headers.get('Authorization','')
    if not auth.startswith('Bearer '): return jsonify(error='Unauthorized'), 401
    if tenant not in projects: return jsonify(error='Unknown tenant'), 400
    data = request.get_json() or {}
    p = {'id': uuid.uuid4().hex, 'name': data.get('name',''), 'description': data.get('description',''), 'team_members': data.get('team_members',[]), 'status':'active'}
    projects[tenant].append(p)
    return jsonify(p), 201

@app.route('/api/v1/projects/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    tenant = request.headers.get('X-Tenant-ID')
    auth = request.headers.get('Authorization','')
    if not auth.startswith('Bearer '): return jsonify(error='Unauthorized'), 401
    if tenant not in projects: return jsonify(error='Unknown tenant'), 400
    before = len(projects[tenant]); projects[tenant] = [p for p in projects[tenant] if p['id'] != project_id]
    return ('',204) if len(projects[tenant]) < before else (jsonify(error='Not found'),404)

if __name__ == '__main__':
    app.secret_key='local-demo-only'
    app.run(host='127.0.0.1', port=5000, debug=False)
