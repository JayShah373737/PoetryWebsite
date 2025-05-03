from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import os

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'your-secret-key-here'  # Change this for production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///poetry.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Initialize database
db = SQLAlchemy(app)

# Categories configuration
CATEGORIES = {
    'life': {'name': 'Life', 'icon': 'leaf'},
    'love': {'name': 'Love', 'icon': 'heart'},
    'reality': {'name': 'Reality', 'icon': 'globe'},
    'thoughts': {'name': 'Thoughts', 'icon': 'brain'},
    'dedicated': {'name': 'Dedicated', 'icon': 'hand-holding-heart'},
    'articles': {'name': 'Articles', 'icon': 'hands-helping'},
    'stories': {'name': 'Stories', 'icon': 'book-open'},
    'ghazalein': {'name': 'Ghazalein', 'icon': 'music'},
    'others': {'name': 'Others', 'icon': 'ellipsis-h'}
}

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

class Poem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, server_default=db.func.now())

# Helper Functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please log in to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def home():
    return render_template('index.html', categories=CATEGORIES)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['logged_in'] = True
            flash('Logged in successfully!', 'success')
            return redirect(url_for('admin'))
        flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('home'))

@app.route('/admin')
@login_required
def admin():
    poems = Poem.query.order_by(Poem.created_at.desc()).all()
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin.html', poems=poems, messages=messages, categories=CATEGORIES)


@app.route('/add_poem', methods=['POST'])
@login_required
def add_poem():
    title = request.form['title']
    content = request.form['content']
    category = request.form['category']
    
    if category not in CATEGORIES:
        flash('Invalid category selected', 'error')
        return redirect(url_for('admin'))
    
    image_path = None
    if 'image' in request.files:
        file = request.files['image']
        if file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_path = filename
    
    poem = Poem(title=title, content=content, category=category, image_path=image_path)
    db.session.add(poem)
    db.session.commit()
    flash('Poem added successfully!', 'success')
    return redirect(url_for('admin'))

@app.route('/get_poems/<category>')
def get_poems(category):
    if category not in CATEGORIES:
        return render_template('poems.html', poems=[], category="Invalid Category", categories=CATEGORIES)
    
    poems = Poem.query.filter_by(category=category).order_by(Poem.created_at.desc()).all()
    return render_template('poems.html', 
                         poems=poems, 
                         category=CATEGORIES[category]['name'],
                         categories=CATEGORIES)  # Make sure to pass CATEGORIES

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Initial Setup
def create_admin_user():
    with app.app_context():
        if not User.query.filter_by(username='admin').first():
            hashed_password = generate_password_hash('admin123', method='sha256')
            admin = User(username='admin', password_hash=hashed_password)
            db.session.add(admin)
            db.session.commit()
            print("Admin user created - username: admin, password: admin123")

@app.route('/delete_poem/<int:poem_id>', methods=['POST'])
@login_required
def delete_poem(poem_id):
    poem = Poem.query.get_or_404(poem_id)
    
    # Delete associated image if exists
    if poem.image_path:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], poem.image_path))
        except:
            pass  # Skip if file doesn't exist
    
    db.session.delete(poem)
    db.session.commit()
    flash('Poem deleted successfully!', 'success')
    return redirect(url_for('admin'))
    

import sqlite3


# Database setup
@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    
    new_message = ContactMessage(name=name, email=email, message=message)
    db.session.add(new_message)
    db.session.commit()

    flash('Message submitted successfully!', 'success')
    return redirect(url_for('home'))

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

def init_db():
    conn = sqlite3.connect('contact_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    email TEXT,
                    message TEXT
                )''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')  # This should be your HTML page

@app.route('/submit_form', methods=['POST'])
def submit_form():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        new_msg = ContactMessage(name=name, email=email, message=message)
        db.session.add(new_msg)
        db.session.commit()
        flash("Your message has been sent successfully!", "success")
        return redirect(url_for('home'))

@app.route('/admin/messages')
@login_required
def view_messages():
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin_messages.html', messages=messages)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        os.makedirs('uploads', exist_ok=True)
        create_admin_user()
    app.run(debug=True)