import os
from flask import Flask, render_template, send_from_directory, redirect, url_for

HTML_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, template_folder=HTML_DIR)

STATIC_DIR = os.path.join(HTML_DIR, 'static')

@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/chat.html')
def chat():
    return render_template('chat.html')

@app.route('/dashboard.html')
def dashboard():
    return render_template('dashboard.html')

@app.route('/login.html')
def login():
    return render_template('login.html')

@app.route('/logout.html')
def logout():
    return render_template('logout.html')

@app.route('/signup.html')
def signup():
    return render_template('signup.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    try:
        return send_from_directory(STATIC_DIR, filename)
    except FileNotFoundError:
        print(f"Error: Static file not found: {filename}")
        return "File Not Found", 404

if __name__ == '__main__':
    app.run(debug=True)
