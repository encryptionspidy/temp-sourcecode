from flask import Flask, request, render_template, redirect, url_for, flash, send_from_directory
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
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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

    # Get noise level from user input
    noise_level = request.form.get('noise_level', 'medium')  # Default to 'medium'

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)  # Save the uploaded file
        
        # Apply the invisible layer (image processing)
        processed_image_path = apply_invisible_layer(file_path, noise_level)
        
        # Return the processed image path to the template
        return render_template('upload.html', processed_image=os.path.basename(processed_image_path))
    else:
        flash('Invalid file type! Only PNG, JPG, and JPEG are allowed.', 'error')
        return redirect(url_for('upload_image'))

# Function to apply the noise layer to the uploaded image
def apply_invisible_layer(image_path, noise_level):
    image = Image.open(image_path)
    
    # Convert the image to a NumPy array
    data = np.array(image)

    # Map noise level to standard deviation
    noise_std_map = {'low': 10, 'medium': 25, 'high': 50}
    noise_std = noise_std_map.get(noise_level, 25)  # Default to 'medium'

    # Generate Gaussian noise
    noise = np.random.normal(0, noise_std, data.shape)

    # Apply the noise and clip values to be in a valid range
    noisy_image = np.clip(data + noise, 0, 255).astype(np.uint8)

    # Convert the noisy array back to an image
    output_image = Image.fromarray(noisy_image)
    
    # Save the processed image in the uploads folder
    processed_image_name = f"{os.path.splitext(os.path.basename(image_path))[0]}_processed{os.path.splitext(image_path)[1]}"
    processed_image_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_image_name)
    
    # Ensure the uploads directory exists before saving the processed image
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    output_image.save(processed_image_path)

    return processed_image_path

# Endpoint to serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)

