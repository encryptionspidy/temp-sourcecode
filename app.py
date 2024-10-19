from flask import Flask, request, render_template, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
import os
from PIL import Image
import numpy as np

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'  
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 
app.secret_key = 'supersecretkey'


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def upload_image():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        flash('No file part in the request!', 'error')
        return redirect(url_for('upload_image'))
    
    file = request.files['image']
    
    if file.filename == '':
        flash('No file selected!', 'error')
        return redirect(url_for('upload_image'))

    
    noise_level = request.form.get('noise_level', 'medium')  

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)  
        
        
        processed_image_path = apply_invisible_layer(file_path, noise_level)
        
        
        return render_template('upload.html', processed_image=os.path.basename(processed_image_path))
    else:
        flash('Invalid file type! Only PNG, JPG, and JPEG are allowed.', 'error')
        return redirect(url_for('upload_image'))


def apply_invisible_layer(image_path, noise_level):
    image = Image.open(image_path)
    
    
    data = np.array(image)

    
    noise_std_map = {'low': 10, 'medium': 25, 'high': 50}
    noise_std = noise_std_map.get(noise_level, 25)

    
    noise = np.random.normal(0, noise_std, data.shape)

    
    noisy_image = np.clip(data + noise, 0, 255).astype(np.uint8)

    
    output_image = Image.fromarray(noisy_image)
    
    
    processed_image_name = f"{os.path.splitext(os.path.basename(image_path))[0]}_processed{os.path.splitext(image_path)[1]}"
    processed_image_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_image_name)
    
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    output_image.save(processed_image_path)

    return processed_image_path


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)

