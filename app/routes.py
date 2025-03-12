from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from app.models import User, Image
from app import db
from app.steganography import encode_image, decode_image
from datetime import datetime
from flask import render_template
from app.cloud_storage import CloudStorage
from app.forms import EncodeForm, DecodeForm

main = Blueprint('main', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

@main.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        current_app.logger.error(f"Error in index route: {str(e)}")
        return "An error occurred", 500

@main.route('/dashboard')
@login_required
def dashboard():
    # Import forms at the top of the file
    
    encode_form = EncodeForm()
    decode_form = DecodeForm()
    return render_template('dashboard.html', 
                         encode_form=encode_form, 
                         decode_form=decode_form)

@main.route('/encode', methods=['POST'])
@login_required
def encode():
    try:
        # Ensure upload directory exists
        if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
            os.makedirs(current_app.config['UPLOAD_FOLDER'])

        if 'image' not in request.files:
            flash('No image uploaded', 'danger')
            return redirect(url_for('main.dashboard'))

        file = request.files['image']
        message = request.form.get('message')

        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(url_for('main.dashboard'))

        if file and allowed_file(file.filename):
            if file.filename is None:
                flash('Invalid filename', 'danger')
                return redirect(url_for('main.dashboard'))
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                encoded_img = encode_image(filepath, message)
                encoded_filename = f'encoded_{filename}'
                encoded_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], encoded_filename)
                encoded_img.save(encoded_filepath)

                # Read the encoded image data
                with open(encoded_filepath, 'rb') as img_file:
                    img_data = img_file.read()

                # Save to database with image data
                image = Image()
                image.filename = encoded_filename  # Changed from filename to encoded_filename
                image.data = img_data
                image.operation = 'encode'
                image.user_id = current_user.id
                image.timestamp = datetime.utcnow()
                db.session.add(image)
                db.session.commit()

                # Clean up files
                if os.path.exists(filepath):
                    os.remove(filepath)
                if os.path.exists(encoded_filepath):
                    os.remove(encoded_filepath)

                return render_template('encode_result.html', filename=encoded_filename)

            except Exception as e:
                if os.path.exists(filepath):
                    os.remove(filepath)
                flash(f'Error encoding message: {str(e)}', 'danger')
                return redirect(url_for('main.dashboard'))

        flash('Invalid file type', 'danger')
        return redirect(url_for('main.dashboard'))

    except Exception as e:
        current_app.logger.error(f"Error in encode route: {str(e)}")
        flash('An error occurred during encoding', 'danger')
        return redirect(url_for('main.dashboard'))

@main.route('/decode', methods=['POST'])
@login_required
def decode():
    try:
        # Ensure upload directory exists
        if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
            os.makedirs(current_app.config['UPLOAD_FOLDER'])

        if 'image' not in request.files:  # Changed from 'encoded_image' to 'image'
            flash('No image uploaded', 'danger')
            return redirect(url_for('main.dashboard'))

        file = request.files['image']  # Changed from 'encoded_image' to 'image'

        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(url_for('main.dashboard'))

        if file and allowed_file(file.filename):
            if file.filename is None:
                raise ValueError("Filename cannot be None")
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                # Read the file data before decoding
                with open(filepath, 'rb') as img_file:
                    img_data = img_file.read()

                message = decode_image(filepath)
                
                # Save to database with image data
                image = Image()  # Create empty Image object first
                image.filename = filename  # Set attributes directly
                image.data = img_data
                image.operation = 'decode'
                image.user_id = current_user.id
                image.timestamp = datetime.utcnow()
                db.session.add(image)
                db.session.commit()

                # Clean up file
                if os.path.exists(filepath):
                    os.remove(filepath)

                return render_template('result.html', message=message)

            except Exception as e:
                if os.path.exists(filepath):
                    os.remove(filepath)
                flash(f'Error decoding message: {str(e)}', 'danger')
                return redirect(url_for('main.dashboard'))

        flash('Invalid file type', 'danger')
        return redirect(url_for('main.dashboard'))

    except Exception as e:
        current_app.logger.error(f"Error in decode route: {str(e)}")
        flash('An error occurred during decoding', 'danger')
        return redirect(url_for('main.dashboard'))

@main.route('/download/<filename>')
@login_required
def download(filename):
    try:
        # Get the image from database
        image = Image.query.filter_by(filename=filename, user_id=current_user.id).first()
        
        if not image:
            current_app.logger.error(f"Image not found in database: {filename}")
            flash('File not found in database', 'danger')
            return redirect(url_for('main.dashboard'))

        # Create upload folder if it doesn't exist
        upload_folder = current_app.config.get('UPLOAD_FOLDER')
        if not upload_folder:
            current_app.logger.error("UPLOAD_FOLDER not configured")
            flash('Server configuration error', 'danger')
            return redirect(url_for('main.dashboard'))

        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        # Write the file temporarily
        filepath = os.path.join(upload_folder, filename)
        try:
            with open(filepath, 'wb') as f:
                f.write(image.data)
            
            response = send_from_directory(upload_folder, filename, as_attachment=True)
            return response
        except Exception as e:
            current_app.logger.error(f"Error writing or sending file: {str(e)}")
            flash('Error processing file for download', 'danger')
            return redirect(url_for('main.dashboard'))
        finally:
            # Clean up the temporary file
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception as e:
                    current_app.logger.error(f"Error removing temporary file: {str(e)}")

    except Exception as e:
        current_app.logger.error(f"Error in download route: {str(e)}")
        flash('Error downloading file', 'danger')
        return redirect(url_for('main.dashboard'))

@main.route('/history')
@login_required
def history():
    try:
        images = Image.query.filter_by(user_id=current_user.id).order_by(Image.timestamp.desc()).all()
        return render_template('history.html', images=images)
        
    except Exception as e:
        current_app.logger.error(f"Error in history route: {str(e)}")
        return "An error occurred", 500

@main.route('/storage-status')
def storage_status():
    storage = CloudStorage()
    status = storage.check_storage_status()
    return render_template('storage_status.html', status=status)

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/contact')
def contact():
    return render_template('contact.html')
