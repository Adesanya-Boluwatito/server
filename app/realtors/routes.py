from flask import jsonify, request, session
from urllib.parse import urlparse
from flask_login import login_required, current_user
from google.cloud import exceptions as google_exceptions
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.realtors_model import Realtor
from app.config import db
from app.realtors import bp
import uuid
from app.credentials import *





ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/realtor/register_profile', methods=['POST'])
@login_required
def register_realtor():

    # Check if the logged-in user is not a realtor

    request_data = None

    if request.headers['Content-Type'] == 'application/json':
        request_data = request.get_json()

    elif request.form:
        request_data = {key: request.form[key] for key in request.form}
    if request_data is None:
        # If not JSON, assume form-data
        return jsonify({"error": "Invalid request format"}), 400
    
    profile_picture = request.files.get('profile_picture')

    if 'profile_picture' not in request.files or not allowed_file(profile_picture.filename):
        return "Invalid file or missing file in the request", 400
    

    realtor = Realtor.query.filter_by(user_id=current_user.id).first()
    if realtor:
        return jsonify({"message": "Realtor already Exists"})

   



    new_realtor = Realtor(id=str(uuid.uuid4()),
                          realtor_id=request_data['realtor_id'],
                          company_name=request_data['company_name'],
                          description=request_data['description'],
                          profile_picture='',
                          company_mail=request_data['company_mail'],
                          website_url=request_data['website_url'],
                          contact=request_data['contact'],
                          user_id=current_user.id)

                           
    filename = secure_filename(profile_picture.filename)

        # Upload the file to Firebase Storage
    bucket = storage.bucket()
    blob = bucket.blob(f'realtor_images/{new_realtor.id}/{filename}')
    blob.upload_from_string(profile_picture.read(), content_type=profile_picture.content_type)

    # Get the public URL of the uploaded file
    file_url = blob.public_url

# Remove the full URL and keep only the relative path
    
    new_realtor.profile_picture = file_url


    try:
        db.session.add(new_realtor)
        db.session.commit()
        return jsonify(new_realtor.serialize()), 201
    except Exception as e:
        print(e)
        db.session.rollback()
        return "An error occured!", 500
    
    

@bp.route('/realtor/update_profile_picture', methods=['POST'])
@login_required
def update_profile_picture():
    try:
        # Fetch the logged-in realtor
        realtor = Realtor.query.filter_by(user_id=current_user.id).first()

        if not realtor:
            return jsonify({"error": "Realtor not found"}), 404

        # Check if a new profile picture is provided in the request
        if 'profile_picture' not in request.files:
            # If no new profile picture provided, update with a placeholder or keep it empty
            realtor.profile_picture = ''  # You can set it to a placeholder URL if needed

            # Commit changes to the database
            db.session.commit()

            return jsonify({"message": "Profile picture updated successfully"}), 200

        new_profile_picture = request.files['profile_picture']

        if not new_profile_picture or not allowed_file(new_profile_picture.filename):
            return jsonify({"error": "Invalid file or missing file in the request"}), 400

        # Delete the existing profile picture from Firebase Storage
        bucket = storage.bucket()
        if realtor.profile_picture:
            
            blob_path = urlparse(realtor.profile_picture).path[1:]
            existing_blob = bucket.blob(blob_path)
            existing_blob.delete()

        # Upload the new profile picture to Firebase Storage
        filename = secure_filename(new_profile_picture.filename)
        new_blob_path = f'realtor_images/{realtor.id}/{filename}'
        new_blob = bucket.blob(new_blob_path)
        new_blob.upload_from_string(new_profile_picture.read(), content_type=new_profile_picture.content_type)

        # Get the public URL of the uploaded file
        new_file_url = new_blob.public_url

        # Update the realtor's profile_picture field in the database
        realtor.profile_picture = new_file_url

        # Commit changes to the database
        db.session.commit()

        return jsonify({"message": "Profile picture updated successfully"}), 200

    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({"error": "An error occurred while updating the profile picture"}), 500




@bp.route('/realtor/delete_profile', methods=['POST'])
@login_required
def delete_realtor_profile():
    # Retrieve the Realtor associated with the current_user
    realtor_to_delete = Realtor.query.filter_by(user_id=current_user.id).first()

    if not realtor_to_delete:
        return jsonify({"error": "Realtor not found for the current user"}), 404

    # Extract the filename from the profile_picture URL
    filename = secure_filename(realtor_to_delete.profile_picture.rsplit('/', 1)[-1])

    # Construct the blob path for deletion (excluding the base URL)
    blob_path = f'realtor_images/{realtor_to_delete.id}/{filename}'

    # Construct the blob URL with the base URL included
    blob_url = f'https://storage.googleapis.com/{storage.bucket().name}/{blob_path}'

    try:
        # Delete the blob from Firebase Storage
        storage.bucket().blob(blob_path).delete()

        # Delete the Realtor profile from the database
        db.session.delete(realtor_to_delete)
        db.session.commit()

        return jsonify({"message": "Realtor profile deleted successfully"}), 200
    except google_exceptions.NotFound:
        # Handle the case where the blob is not found in Google Cloud Storage
        return jsonify({"error": f"Blob not found in Google Cloud Storage: {blob_url}"}), 404
    except Exception as e:
        # Log the detailed error on the server side for debugging
        print(f"An error occurred: {e}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while deleting the Realtor profile"}), 500



    

@bp.route('/realtor/get_all_realtors', methods=['GET'])
@login_required
def get_all_realtors():
    page_number = request.args.get('page', 1, type=int)

    # Assuming you have a 'active' field in your Realtor model
    pagination_realtors = Realtor.query.filter(Realtor.active == True).paginate(page=page_number, per_page=20)

    # If realtors is None return an empty list
    if pagination_realtors is None:
        return jsonify({"realtors": [], "pages": 0}), 200
    
    realtors = pagination_realtors.items
    number_of_pages = pagination_realtors.pages
    # Init an empty list
    list_realtors_with_images = []

    for realtor_item in realtors:
        listed_realtor = realtor_item.serialize()

        # Add Firebase storage URL for the realtor profile picture
        if realtor_item.profile_picture:
            bucket = storage.bucket()
            blob = bucket.blob(realtor_item.profile_picture)
            listed_realtor["profile_picture_url"] = blob.public_url

        list_realtors_with_images.append(listed_realtor)

    response_data = {
        "realtors": list_realtors_with_images,
        "pages": number_of_pages
    }
    return jsonify(response_data)



