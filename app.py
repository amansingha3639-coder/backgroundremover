import os
import sqlite3
from rembg import remove
from PIL import Image
from werkzeug.utils import secure_filename
from flask import Flask, request, render_template, redirect, url_for, session, g

# -------------------- Flask Config --------------------
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DATABASE'] = 'loginentry.db'
app.secret_key = "supersecretkey"   # change to something secure

# -------------------- Database Helpers --------------------
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

#@app.teardown_appcontext
#def close_db(error):
 #   db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS login (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    db.commit()

# -------------------- Helpers --------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def remove_background(input_path, output_path):
    input_img = Image.open(input_path)
    output = remove(input_img)
    output.save(output_path)

# -------------------- Routes --------------------
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/createaccount', methods=['GET', 'POST'])
def signup():
    db = get_db()
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = db.execute("SELECT name FROM login WHERE name = ?", (username,)).fetchone()
        if user:
            return render_template('cratenewaccount.html', error="Username already exists")

        db.execute("INSERT INTO login (name, password) VALUES (?, ?)", (username, password))
        db.commit()
        return redirect(url_for('login'))

    return render_template('cratenewaccount.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    db = get_db()
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        row = db.execute("SELECT password FROM login WHERE name = ?", (username,)).fetchone()

        if row and row["password"] == password:
            session["user"] = username
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error="Invalid username or password")

    return render_template('login.html')

@app.route('/home')
def home():
    if "user" not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(url_for('login'))

@app.route('/remback', methods=['POST'])
def remback():
    if "user" not in session:
        return redirect(url_for('login'))

    file = request.files.get('file')
    if not file or file.filename == "":
        return render_template('home.html', error="No file selected")

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        rembg_img_name = filename.rsplit('.', 1)[0] + "_rembg.png"
        remove_background(file_path, os.path.join(app.config['UPLOAD_FOLDER'], rembg_img_name))

        return render_template('home.html', org_img_name=filename, rembg_img_name=rembg_img_name)

    return render_template('home.html', error="Invalid file type. Allowed: png, jpg, jpeg, webp")

# -------------------- Run --------------------
if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)
