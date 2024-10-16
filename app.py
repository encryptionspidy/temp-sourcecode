from flask import Flask, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
from PIL import Image
import numpy as np

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'  # Upload folder path
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max upload size: 16MB
app.secret_key = 'supersecretkey'  # For flash messages

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Create the uploads directory if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Function to check if the file is allowed
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

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)  # Save the uploaded file
        
        # Apply the invisible layer (image processing)
        processed_image_path = apply_invisible_layer(file_path)
        
        flash(f'Image uploaded and processed successfully! Saved at {processed_image_path}', 'success')
        return redirect(url_for('upload_image'))
    else:
        flash('Invalid file type! Only PNG, JPG, and JPEG are allowed.', 'error')
        return redirect(url_for('upload_image'))

# Function to apply the noise layer to the uploaded image
def apply_invisible_layer(image_path):
    image = Image.open(image_path)
    
    # Convert the image to a NumPy array
    data = np.array(image)

    # Generate Gaussian noise
    noise = np.random.normal(0, 25, data.shape)

    # Apply the noise and clip values to be in a valid range
    noisy_image = np.clip(data + noise, 0, 255).astype(np.uint8)

    # Convert the noisy array back to an image
    output_image = Image.fromarray(noisy_image)
    
    # Save the processed image
    processed_image_path = f"{image_path.rsplit('.', 1)[0]}_processed.{image_path.rsplit('.', 1)[1]}"
    output_image.save(processed_image_path)

    return processed_image_path

if __name__ == '__main__':
    app.run(debug=True)

