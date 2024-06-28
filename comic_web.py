from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from comic_app.settings_manager import SettingsManager, SETTINGS_FILE
from comic_app.comic_manager import ComicManager

app = Flask(__name__)

# Initialize settings manager and comic manager
settings_manager = SettingsManager(SETTINGS_FILE)
settings = settings_manager.settings
comic_manager = ComicManager(settings["comics"], lambda: None)

@app.route('/', methods=['GET', 'POST'])
def comic_viewer():
    if request.method == 'POST':
        selected_comic = request.form.get('comic')
        selected_date = request.form.get('date')
        # Update settings with the selected comic and date
        settings['selected_comic'] = selected_comic
        settings['date'] = selected_date
        settings_manager.save_settings(settings)
        return redirect(url_for('comic_viewer'))

    selected_comic = settings.get('selected_comic', comic_manager.comics[0]['name'])
    selected_date = settings.get('date', datetime.now().strftime("%Y-%m-%d"))

    return render_template('index.html', 
                           comics=comic_manager.comics, 
                           selected_comic=selected_comic, 
                           selected_date=selected_date)

if __name__ == '__main__':
    app.run(debug=True)
