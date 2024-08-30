from flask import Flask, render_template, request, redirect, url_for, session
from flask_elasticsearch import FlaskElasticsearch
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB

# Initialize Elasticsearch
es = FlaskElasticsearch(app)

# Create index for users
if not es.indices.exists('users'):
    es.indices.create(index='users')

@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        # Pretpostavimo da se korisnik validira
        session['username'] = username
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        # Logika za registraciju korisnika
        es.index(index='users', body={'username': username})
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'username' not in session:
        return redirect(url_for('login'))
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Čuvanje putanje u Elasticsearch
        es.update(index='users', id=session['username'], body={'doc': {'file_path': filename}})
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
