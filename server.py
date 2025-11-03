import io
import zipfile
from fileinput import filename

from flask import Flask, request, render_template, send_file
import os
from threading import Thread
import subprocess
import sys

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'

@app.route('/', methods=['POST', 'GET'])
def upload_file():
    if request.method == 'POST':
        folder = request.args.get("folder")
        if 'update_cfg' in request.values:
            logo_file = request.files['logo']
            if logo_file.filename != '':
                logo_path = os.path.join(dir, "images", "logo.png")
                logo_file.save(logo_path)
            bkg_file = request.files['bkg']
            if bkg_file.filename != '':
                bkg_path = os.path.join(dir, "images", "bkg.jpg")
                bkg_file.save(bkg_path)
            return 'Update config', 200
        if 'run' in request.values:
            print("Received Run back-end...")
            if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], folder)):
                return 'Not existing folder', 400
            t = Thread(target=run_reconstruction, args=[folder])
            t.start()
            return 'Run reconstruction', 200
        if 'uploaded_file' not in request.files:
            return 'No file part', 400
        if folder is None:
            return 'No file part', 400
        if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], folder)):
            os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], folder, "exterior"))
            os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], folder, "interior"))
            os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], folder, "misc"))

        file = request.files['uploaded_file']
        if file.filename == '':
            return 'No selected file', 400
        elif "Misc" in file.filename:
            type = "misc"
        elif "Interior" in file.filename:
            type = "interior"
        else:
            type = "exterior"

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], folder, type, file.filename)
        file.save(file_path)

        return f'File saved to {file_path}', 200
    elif request.method == 'GET':
        if request.args.get('console') == 'True':
            return render_template('index.html')
        folder = request.args.get("folder")
        imgs_folder = os.path.join(app.config['UPLOAD_FOLDER'], folder, "final_exterior")
        if not folder:
            return "Missing 'folder' parameter", 400

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zipf:
            for filename in os.listdir(imgs_folder):
                file_path = os.path.join(imgs_folder, filename)
                zipf.write(file_path, arcname=filename)
        zip_buffer.seek(0)
        return send_file(zip_buffer, mimetype='application/zip', download_name=f'images_{folder}.zip', as_attachment=True)
    else:
        return "Nor implemented", 400

def run_reconstruction(folder):
    print("Run back-end...")
    script = os.path.join(dir, "run_backend.sh")
    subprocess.run([f"{script} {folder} {dir}"], shell=True)

if __name__ == '__main__':
    dir = os.path.dirname(os.path.abspath(__file__))
    # arg parameter to know the Anaconda folder
    #conda_folder = sys.argv[1]
    os.makedirs(os.path.join(dir, UPLOAD_FOLDER), exist_ok=True)
    app.config['UPLOAD_FOLDER'] = os.path.join(dir, UPLOAD_FOLDER)
    app.run(host="0.0.0.0", ssl_context=(os.path.join(dir, 'cert.pem'), os.path.join(dir, 'key.pem')))
