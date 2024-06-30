from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
import threading
import requests
import secrets

from comic_app.settings_manager import SettingsManager, SETTINGS_FILE
from comic_app.comic_manager import ComicManager

try:
    from comic_app.image_url_parser import Image_URL_Parser
    parser_available = True
except ImportError:
    parser_available = False

app = Flask(__name__)

# Initialize settings manager and comic manager
settings_manager = SettingsManager(SETTINGS_FILE)
settings = settings_manager.settings
comic_manager = ComicManager(settings["comics"], lambda: None)

# Global variable to hold image loading status
image_status = {"status": "waiting", "file_path": ""}

if "SECRET_KEY" in settings:
    app.config['SECRET_KEY'] = settings["SECRET_KEY"]
else:
    app.config['SECRET_KEY'] = secrets.token_hex(16)
    settings["SECRET_KEY"] = app.config['SECRET_KEY']
    settings_manager.save_settings(settings)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
bcrypt = Bcrypt(app)

# User model for the database
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Initialize the database and create an admin user if necessary
with app.app_context():
    db.create_all()
    admin_username = 'admin'
    if not User.query.first():
        admin_password = secrets.token_urlsafe(16)
        hashed_password = bcrypt.generate_password_hash(admin_password).decode('utf-8')
        admin_user = User(username=admin_username, password=hashed_password)
        db.session.add(admin_user)
        db.session.commit()
        settings["admin_password"] = admin_password
        settings_manager.save_settings(settings)
    else:
        admin_user = User.query.first()
        if "admin_password" not in settings:
            admin_password = secrets.token_urlsafe(16)
            hashed_password = bcrypt.generate_password_hash(admin_password).decode('utf-8')
            admin_user.password = hashed_password
            db.session.commit()
            settings["admin_password"] = admin_password
            settings_manager.save_settings(settings)
        else:
            admin_password = settings["admin_password"]
        
        # Check if the hash of the stored password matches the hash in the database
        if bcrypt.check_password_hash(admin_user.password, admin_password):
            print(f'Username: {admin_username}, Password: {admin_password}')
            print(f'Please change the default password!')

def download_and_save_comic_image(date_str, folder_path, file_path_jpg):
    global image_status
    if parser_available:
        #print("Downloading comic image...")
        image_status["status"] = "Downloading comic image..."
        comic_name = comic_manager.selected_comic["url"]
        parser = Image_URL_Parser(comic_name)
        image_url = parser.get_comic_image_url(
            int(date_str[:2]) + 2000,  # year
            date_str[2:4],            # month
            date_str[4:]              # day
        )
        if image_url:
            #print("Parse success, fetch image to save.")
            fetch_image(image_url, file_path_jpg)
            return
    image_status["status"] = "failure"

def fetch_image(image_url, file_path_jpg):
    global image_status
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        save_image(response, file_path_jpg)
    except requests.RequestException as e:
        image_status["status"] = "failure"

def save_image(response, file_path_jpg):
    global image_status
    with open(file_path_jpg, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
        image_status["file_path"] = file_path_jpg
        image_status["status"] = "success"  # "Downloaded and saved comic to {file_path_jpg}"

def load_comic_image(selected_comic, selected_date, folder_path):
    global image_status
    image_status["status"] = f"Loading comic image: {selected_comic} for {selected_date} from {folder_path}."
    
    if selected_comic != comic_manager.selected_comic['name']:
        image_status["status"] = "Comic change in progress"
        comic_manager.load_comic_details(selected_comic)
    
    date_str = datetime.strptime(selected_date, "%Y-%m-%d").strftime("%y%m%d")
    file_path_jpg = os.path.join(folder_path, f"{comic_manager.selected_comic['short_code']}{date_str}.jpg")
    file_path_bmp = os.path.join(folder_path, f"{comic_manager.selected_comic['short_code']}{date_str}.bmp")

    if os.path.exists(file_path_jpg):
        #print(f"Path exists: {file_path_jpg}")
        image_status["file_path"] = file_path_jpg
        image_status["status"] = "success"  # f"Loaded comic from {file_path_jpg}"
    elif os.path.exists(file_path_bmp):
        #print(f"Path exists: {file_path_bmp}")
        image_status["file_path"] = file_path_bmp
        image_status["status"] = "success"  # f"Loaded comic from {file_path_bmp}"
    else:
        #print(f"No image found, attempt to download")
        download_and_save_comic_image(date_str, folder_path, file_path_jpg)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('comic_viewer'))
        else:
            flash('Login unsuccessful. Please check username and password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if not bcrypt.check_password_hash(current_user.password, current_password):
            flash('Current password is incorrect.', 'danger')
        elif new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
        else:
            hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            current_user.password = hashed_password
            db.session.commit()
            flash('Password changed successfully.', 'success')
            return redirect(url_for('comic_viewer'))
    
    return render_template('change_password.html')

@app.route('/', methods=['GET', 'POST'])
@login_required
def comic_viewer():
    if request.method == 'POST':
        settings_manager.save_settings(settings)
        return redirect(url_for('comic_viewer'))

    return render_template('index.html', comics=comic_manager.comics)

@app.route('/request_image', methods=['POST'])
@login_required
def request_image():
    global image_status
    image_status["status"] = "waiting"
    selected_comic = request.json.get('comic')
    selected_date = request.json.get('date')
    
    folder_path = settings.get("folder_path", os.path.join(os.path.expanduser("~"), "Pictures", "comics"))
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # Start a new thread to load the comic image
    threading.Thread(target=load_comic_image, args=(selected_comic, selected_date, folder_path)).start()
    
    return jsonify({"status": "loading"}), 202

@app.route('/status', methods=['GET'])
@login_required
def status():
    global image_status
    if image_status["status"] == "success":
        return jsonify({"status": "success", "file_path": url_for('serve_image', filename=os.path.basename(image_status["file_path"]))})
    return jsonify({"status": image_status["status"]})

@app.route('/image/<path:filename>', methods=['GET'])
@login_required
def serve_image(filename):
    folder_path = settings.get("folder_path", os.path.join(os.path.expanduser("~"), "Pictures", "comics"))
    #print(f"Sending {os.path.join(folder_path, filename)}")
    return send_file(os.path.join(folder_path, filename))

if __name__ == '__main__':
    app.run(debug=True)
