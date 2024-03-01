from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
import os
import shutil
import socket
import qrcode
from PIL import Image

app = Flask(__name__)
# Securely configure the secret key
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')

IMAGE_EXTENSIONS = ['.jpg', '.png']
image_files = []
selected_directory = None

def generate_qr_code(local_ip):
    """
    Generates a QR code for the given local IP address with customized colors.
    The QR code has a transparent background and black data points.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(f'http://{local_ip}:5000')
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
    # Make white parts of the QR code transparent
    datas = img.getdata()
    newData = []
    for item in datas:
        if item[0] == 255 and item[1] == 255 and item[2] == 255:  # Finding white parts of the image
            newData.append((255, 255, 255, 0))  # Making white parts transparent
        else:
            newData.append(item)
    img.putdata(newData)
    img_path = os.path.join(app.static_folder, 'qr_code.png')
    img.save(img_path)

@app.route('/')
def index():
    session['tags'] = []
    global selected_directory
    selected_directory = None
    local_ip = socket.gethostbyname(socket.gethostname())
    generate_qr_code(local_ip)  # Generate QR code dynamically
    return render_template('index.html', local_ip=local_ip)

@app.route('/select_folder', methods=['POST'])
def select_folder():
    global selected_directory, image_files
    selected_directory = request.form.get('folder_path')
    
    # Ensure temp_Descriptions directory exists
    temp_dir = os.path.join(selected_directory, 'temp_Descriptions')
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    image_files = sorted([f for f in os.listdir(selected_directory) if any(f.endswith(ext) for ext in IMAGE_EXTENSIONS)])
    if not image_files:
        return "No image files found in the selected directory. <a href='/'>Go back</a>."
    return redirect(url_for('describe_image'))

@app.route('/image/<path:filename>')
def serve_image(filename):
    return send_from_directory(selected_directory, filename)

@app.route('/describe_image', methods=['GET', 'POST'])
def describe_image():
    global selected_directory, image_files
    
    if 'tags' not in session:
        session['tags'] = []

    if request.method == 'POST':
        description = request.form.get('description')
        img_name = os.path.basename(request.form.get('img_name'))
        
        new_tags = set(tag.strip() for tag in description.split(",") if tag.strip())
        combined_tags = set(session['tags']).union(new_tags)
        session['tags'] = list(combined_tags)
        
        txt_filename = os.path.join(selected_directory, 'temp_Descriptions', os.path.splitext(img_name)[0] + '.txt')
        
        with open(txt_filename, 'w') as f:
            f.write(description)
        
        image_files.remove(img_name)

    if not image_files:
        return render_template('commit.html')

    # Define local_ip within this function
    local_ip = socket.gethostbyname(socket.gethostname())
    img_path = os.path.join('/image', image_files[0])
    return render_template('describe.html', img_path=img_path, local_ip=local_ip)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')