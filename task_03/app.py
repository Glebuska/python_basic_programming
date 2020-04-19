from flask import Flask, redirect, render_template, request, session, url_for, flash, send_file, current_app, \
    send_from_directory
from flask_dropzone import Dropzone
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from logic import start_swaping

import os

app = Flask(__name__)
dropzone = Dropzone(app)

app.config['SECRET_KEY'] = 'supersecretkeygoeshere'

# Dropzone settings
# app.config['DROPZONE_UPLOAD_MULTIPLE'] = False
app.config['DROPZONE_ALLOWED_FILE_CUSTOM'] = True
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = 'image/*'
app.config['DROPZONE_MAX_FILES'] = 1
app.config['UPLOAD_FOLDER'] = "uploads"

# Uploads settings
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd() + '/uploads'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # set maximum file size, default is 16MB


@app.route('/', methods=['GET', 'POST'])
def index():
    # set session for image results
    if "file_urls" not in session:
        session['file_urls'] = []
        session['file_names'] = []

    # list to hold our uploaded image urls
    file_urls = session['file_urls']
    file_names = session['file_names']

    # handle image upload from Dropszone
    if request.method == 'POST':
        file_obj = request.files
        for f in file_obj:
            file = request.files.get(f)

            # save the file with to our photos folder
            filename = photos.save(
                file,
                name=file.filename
            )
            file_names.append(filename)
            # append image urls
            file_urls.append(photos.url(filename))
        if len(file_urls) % 2 == 0:
            try:
                start_swaping(file_names[len(file_names) - 2], file_names[len(file_names) - 1])
                session['file_urls'] = file_urls
                return redirect(url_for('return_result'))
            except:
                session.pop('file_urls', None)
                session.pop('file_names', None)
                flash("No face detection. Please upload image with face")
                return render_template('index.html')

        session['file_urls'] = file_urls
        session['file_names'] = file_names
        return "uploading..."

    return render_template('index.html')


@app.route('/return_result')
def return_result():
    uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(directory=uploads, filename='result.jpg')


@app.route('/results', methods=['GET', 'POST'])
def results():
    # redirect to home if no images to display

    if "file_urls" not in session or session['file_urls'] == []:
        return redirect(url_for('index'))

    file_urls = session['file_urls']
    # set the file_urls and remove the session variable
    session.pop('file_urls', None)
    session.pop('file_names', None)

    return render_template('result.html', file_urls=file_urls)


if __name__ == '__main__':
    app.run(debug=True)
