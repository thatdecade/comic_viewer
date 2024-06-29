#comic_web.py
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import os
from datetime import datetime
import threading
import requests

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

def download_and_save_comic_image(date_str, folder_path, file_path_jpg):
    global image_status
    if parser_available:
        print("Downloading comic image...")
        image_status["status"] = "Downloading comic image..."
        comic_name = comic_manager.selected_comic["url"]
        parser = Image_URL_Parser(comic_name)
        image_url = parser.get_comic_image_url(
            int(date_str[:2]) + 2000,  # year
            date_str[2:4],            # month
            date_str[4:]              # day
        )
        if image_url:
            print("Parse success, fetch image to save.")
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
    image_status["status"] = "downloading"
    print(f"Loading comic image")
    
    date_str = datetime.strptime(selected_date, "%Y-%m-%d").strftime("%y%m%d")
    file_path_jpg = os.path.join(folder_path, f"{comic_manager.selected_comic['short_code']}{date_str}.jpg")
    file_path_bmp = os.path.join(folder_path, f"{comic_manager.selected_comic['short_code']}{date_str}.bmp")

    if os.path.exists(file_path_jpg):
        print(f"Path exists: {file_path_jpg}")
        image_status["file_path"] = file_path_jpg
        image_status["status"] = "success"  # f"Loaded comic from {file_path_jpg}"
    elif os.path.exists(file_path_bmp):
        print(f"Path exists: {file_path_bmp}")
        image_status["file_path"] = file_path_bmp
        image_status["status"] = "success"  # f"Loaded comic from {file_path_bmp}"
    else:
        print(f"No image found, attempt to download")
        download_and_save_comic_image(date_str, folder_path, file_path_jpg)

@app.route('/', methods=['GET', 'POST'])
def comic_viewer():
    if request.method == 'POST':
        settings_manager.save_settings(settings)
        return redirect(url_for('comic_viewer'))

    return render_template('index.html', comics=comic_manager.comics)

@app.route('/request_image', methods=['POST'])
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
def status():
    global image_status
    if image_status["status"] == "success":
        return jsonify({"status": "success", "file_path": url_for('serve_image', filename=os.path.basename(image_status["file_path"]))})
    return jsonify({"status": image_status["status"]})

@app.route('/image/<path:filename>', methods=['GET'])
def serve_image(filename):
    folder_path = settings.get("folder_path", os.path.join(os.path.expanduser("~"), "Pictures", "comics"))
    print(f"Sending {os.path.join(folder_path, filename)}")
    return send_file(os.path.join(folder_path, filename))

if __name__ == '__main__':
    app.run(debug=True)
