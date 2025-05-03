from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import os
from datetime import timedelta

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')

# Configuration - Use environment variables for production
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key'),  # Change in production
    SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///poetry.db').replace('postgres://', 'postgresql://', 1),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    UPLOAD_FOLDER=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads'),
    ALLOWED_EXTENSIONS={'png', 'jpg', 'jpeg', 'gif'},
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
    MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16MB upload limit
)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

# Helper Functions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in to access this page', 'error')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def home():
    return render_template('index.html', categories=CATEGORIES)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return redirect(url_for('login'))
            
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session.permanent = True
            session['logged_in'] = True
            session['username'] = username
            flash('Logged in successfully!', 'success')
            next_page = request.args.get('next', url_for('admin'))
            return redirect(next_page)
            
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
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    category = request.form.get('category', '').strip()
    
    if not title or not content or not category:
        flash('All fields are required', 'error')
        return redirect(url_for('admin'))
    
    if category not in CATEGORIES:
        flash('Invalid category selected', 'error')
        return redirect(url_for('admin'))
    
    image_path = None
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
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
                         categories=CATEGORIES)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/delete_poem/<int:poem_id>', methods=['POST'])
@login_required
def delete_poem(poem_id):
    poem = Poem.query.get_or_404(poem_id)
    
    if poem.image_path:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], poem.image_path))
        except OSError:
            pass
    
    db.session.delete(poem)
    db.session.commit()
    flash('Poem deleted successfully!', 'success')
    return redirect(url_for('admin'))

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    message = request.form.get('message', '').strip()
    
    if not name or not email or not message:
        flash('All fields are required', 'error')
        return redirect(url_for('home'))
    
    new_message = ContactMessage(name=name, email=email, message=message)
    db.session.add(new_message)
    db.session.commit()

    flash('Message submitted successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/admin/messages')
@login_required
def view_messages():
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin_messages.html', messages=messages)

# Initial Setup
def create_admin_user():
    with app.app_context():
        if not User.query.filter_by(username='admin').first():
            hashed_password = generate_password_hash(
                os.environ.get('ADMIN_PASSWORD', 'admin123'),  # Change in production
                method='pbkdf2:sha256'
            )
            admin = User(username='admin', password_hash=hashed_password)
            db.session.add(admin)
            db.session.commit()
            print("Admin user created - username: admin")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin_user()
    
    # For production, use a WSGI server like gunicorn instead
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)