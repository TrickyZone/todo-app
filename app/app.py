import os
from flask import Flask, request, redirect, session, render_template, jsonify
import psycopg2, redis
      

app = Flask(__name__)
app.secret_key = 'super-secret-keys'
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
r = redis.Redis(host='redis', port=6379)

def get_db():
    return psycopg2.connect(
        host='db',
        database=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD')
    )

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u, p = request.form['username'], request.form['password']
        conn = get_db()
        cur = conn.cursor()
        # cur.execute("SELECT id FROM users WHERE username=%s AND password=%s;", (u,p))
        cur.execute("SELECT id FROM users WHERE username='" + u + "' AND password='" + p + "';")
        user = cur.fetchone()
        conn.close()
        if user:
            session['user'] = user[0]
            return redirect('/')
        return "Login failed", 401
    return render_template('login.html')

@app.route('/')
def index():
    if 'user' not in session: return redirect('/login')
    return render_template('index.html')

@app.route('/api/todos', methods=['GET','POST','DELETE'])
def todos():
    if 'user' not in session: return jsonify({'error':'unauth'}), 403

    conn = get_db()
    cur = conn.cursor()
    user_id = session['user']

    if request.method == 'POST':
        text = request.json.get('text')
        cur.execute("INSERT INTO todos (user_id, text) VALUES (%s,%s) RETURNING id, text", (user_id,text))
        conn.commit()
        todo = cur.fetchone()
        # cache count
        r.incr(f"user:{user_id}:count")
        return jsonify({'id': todo[0], 'text': todo[1]}), 201

    if request.method == 'DELETE':
        todo_id = request.json.get('id')
        cur.execute("DELETE FROM todos WHERE id=%s AND user_id=%s", (todo_id,user_id))
        conn.commit()
        # update cache count
        r.decr(f"user:{user_id}:count")
        return '', 204

    # GET
    cur.execute("SELECT id, text FROM todos WHERE user_id=%s", (user_id,))
    items = [{'id':i,'text':t} for i,t in cur.fetchall()]
    count = r.get(f"user:{user_id}:count")
    count = int(count) if count else len(items)
    return jsonify({'todos': items, 'count': count})

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/signup', methods=['POST'])
def signup():
    u, p = request.form['username'], request.form['password']
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (username, password) VALUES (%s, %s) RETURNING id", (u, p))
    conn.commit()
    user = cur.fetchone()
    conn.close()
    session['user'] = user[0]
    return redirect('/')

@app.route('/db', methods=['GET'])
def view_db():
    if 'user' not in session:
        return jsonify({'error': 'unauth'}), 403

    conn = get_db()
    cur = conn.cursor()

    # fetch all users
    cur.execute("SELECT id, username FROM users;")
    users = [{'id': u, 'username': uname} for u, uname in cur.fetchall()]

    # fetch all todos
    cur.execute("SELECT id, user_id, text FROM todos;")
    todos = [{'id': i, 'user_id': uid, 'text': t} for i, uid, t in cur.fetchall()]

    conn.close()
    return jsonify({'users': users, 'todos': todos})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)


# from flask import Flask, request, session, redirect, render_template, jsonify
# import psycopg2
# import os
# from datetime import datetime

# app = Flask(__name__)
# app.secret_key = 'secret-key'

# def get_db():
#     return psycopg2.connect(
#         dbname=os.getenv("POSTGRES_DB"),
#         user=os.getenv("POSTGRES_USER"),
#         password=os.getenv("POSTGRES_PASSWORD"),
#         host=os.getenv("POSTGRES_HOST", "db"),
#     )

# @app.route('/')
# def dashboard():
#     if 'user' not in session:
#         return redirect('/login')
#     return render_template('index.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'GET':
#         return render_template('login.html')
#     u, p = request.form['username'], request.form['password']
#     conn = get_db()
#     cur = conn.cursor()
#     cur.execute("SELECT id FROM users WHERE username=%s AND password=%s", (u, p))
#     user = cur.fetchone()
#     conn.close()
#     if user:
#         session['user'] = user[0]
#         return redirect('/')
#     return "Login failed", 401

# @app.route('/signup', methods=['POST'])
# def signup():
#     u, p = request.form['username'], request.form['password']
#     conn = get_db()
#     cur = conn.cursor()
#     cur.execute("INSERT INTO users (username, password) VALUES (%s, %s) RETURNING id", (u, p))
#     conn.commit()
#     user = cur.fetchone()
#     conn.close()
#     session['user'] = user[0]
#     return redirect('/')

# @app.route('/logout')
# def logout():
#     session.clear()
#     return redirect('/login')

# # ----- To-Do APIs -----
# @app.route('/api/todos', methods=['GET'])
# def get_todos():
#     if 'user' not in session:
#         return redirect('/login')
#     conn = get_db()
#     cur = conn.cursor()
#     cur.execute("SELECT id, text FROM todos WHERE user_id = %s", (session['user'],))
#     todos = [{'id': row[0], 'text': row[1]} for row in cur.fetchall()]
#     conn.close()
#     return jsonify({'todos': todos, 'count': len(todos)})

# @app.route('/api/todos', methods=['POST', 'DELETE'])
# def modify_todo():
#     if 'user' not in session:
#         return redirect('/login')
#     conn = get_db()
#     cur = conn.cursor()
#     data = request.get_json()
#     if request.method == 'POST':
#         cur.execute("INSERT INTO todos (user_id, text) VALUES (%s, %s)", (session['user'], data['text']))
#     else:
#         cur.execute("DELETE FROM todos WHERE id = %s AND user_id = %s", (data['id'], session['user']))
#     conn.commit()
#     conn.close()
#     return '', 204

# # ----- Status Generation -----
# @app.route('/generate-status', methods=['POST'])
# def generate_status():
#     input_text = request.json.get('text')
#     # Very basic simulation of professional phrasing
#     phrases = {
#         "fixed": "resolved",
#         "bug": "issue",
#         "meeting": "project sync",
#         "worked on": "focused on",
#         "setup": "configured",
#         "done": "completed",
#         "trying to": "attempted to"
#     }
#     for word, replacement in phrases.items():
#         input_text = input_text.replace(word, replacement)
#     return jsonify({"rephrased": input_text})


# @app.route('/save-status', methods=['POST'])
# def save_status():
#     if 'user' not in session:
#         return redirect('/login')
#     status = request.json.get('text')
#     date = request.json.get('date', datetime.today().date())
#     conn = get_db()
#     cur = conn.cursor()
#     cur.execute("""
#         INSERT INTO status_updates (user_id, status_text, created_date)
#         VALUES (%s, %s, %s)
#     """, (session['user'], status, date))
#     conn.commit()
#     conn.close()
#     return '', 204

# @app.route('/calendar-data')
# def calendar_data():
#     if 'user' not in session:
#         return redirect('/login')
#     conn = get_db()
#     cur = conn.cursor()
#     cur.execute("""
#         SELECT created_date, status_text FROM status_updates WHERE user_id = %s
#     """, (session['user'],))
#     rows = cur.fetchall()
#     conn.close()
#     return jsonify([
#         {"date": str(row[0]), "status": row[1]} for row in rows
#     ])
