import os

from flask import Flask, redirect, render_template, request, session, url_for, flash, current_app, \
    send_from_directory
from flask_dropzone import Dropzone
from werkzeug.utils import secure_filename

from logic import start_swapping

app = Flask(__name__)
dropzone = Dropzone(app)

app.config['SECRET_KEY'] = 'supersecretkeygoeshere'

# Dropzone settings
app.config['DROPZONE_ALLOWED_FILE_CUSTOM'] = True
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = 'image/*'
app.config['DROPZONE_MAX_FILES'] = 1
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():
    # set session for image results
    if "file_names" not in session:
        session['file_names'] = []

    file_names = session['file_names']

    # handle image upload from Dropszone
    if request.method == 'POST':
        file = request.files['file']

        filename = secure_filename(file.filename)
        if not allowed_file(filename):
            return render_template('index.html', error=True,
                                   message='File should be one of the following formats: jpeg, jpg, png.')
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        file_names.append(filename)

        if len(file_names) % 2 == 0:
            try:
                first_img = file_names[len(file_names) - 2]
                second_img = file_names[len(file_names) - 1]
                result_name = start_swapping(first_img, second_img)
                file_names.append(result_name)
                session['file_names'] = file_names
                return render_template('index.html')
            except IndexError:
                session.pop('file_names', None)
                return render_template('index.html', error=True,
                                       message='Upload image with face')

        session['file_names'] = file_names
        return "uploading..."

    return render_template('index.html')


@app.route('/result', methods=['GET', 'POST'])
def return_result():
    if "file_names" not in session or session['file_names'] == []:
        return redirect(url_for('index'))

    file_names = session['file_names']
    first_img = file_names[len(file_names) - 3]
    second_img = file_names[len(file_names) - 2]
    result_img = file_names[len(file_names) - 1]
    session.pop('file_names', None)
    # uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    # return send_from_directory(directory=uploads, filename='result.jpg')
    return render_template('result.html',
                           first_file=url_for('static', filename='uploads/' + first_img)
                           , second_file=url_for('static', filename='uploads/' + second_img)
                           , result_image=url_for('static', filename='uploads/' + result_img))


if __name__ == '__main__':
    app.run(debug=True)
