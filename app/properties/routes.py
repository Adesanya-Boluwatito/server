from flask import  request, jsonify,current_app
from werkzeug.utils import secure_filename
from flask_login import login_required
from datetime import datetime, timedelta 
from app.models.properties_model import Property, Image
from app.models.realtors_model import Realtor
from app.config import db
from app.credentials import *
from app.properties import bp
from sqlalchemy import func
import uuid  # Import uuid






ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/property/new_property/<realtor_id>', methods=['POST'])
@login_required
def create_property(realtor_id):
    print(realtor_id)
    realtor_exists = Realtor.query.filter_by(realtor_id=realtor_id).first() is not None
    if not realtor_exists:
        print(realtor_id)
        return jsonify({"error": "Unauthorized user"}), 401


    request_data = None

    if request.headers['Content-Type'] == 'application/json':
        request_data = request.get_json()

    elif request.form:
        request_data = {key: request.form[key] for key in request.form}
    if request_data is None:
        # If not JSON, assume form-data
        return jsonify({"error": "Invalid request format"}), 400
    print(request_data)

    # Create a new property
    ownwer_id = realtor_id

    new_property = Property(
                            id=str(uuid.uuid4()),
                            owner_id= ownwer_id,
                            location=request_data.get('location'),
                            description=request_data.get('description'),
                            address=request_data.get('address'),
                            bedrooms=request_data.get('bedrooms'),
                            bathrooms=request_data.get('bathrooms'),
                            title=request_data.get('title'),
                            category=request_data.get('category'),
                            price=request_data.get('price'),
                            property_type=request_data.get('property_type'),
                            size=request_data.get('size'),
                            date_created=datetime.utcnow())
                            

    try:
        db.session.add(new_property)
        db.session.commit()

    # Handle file upload
        files = request.files.getlist('file')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                bucket = storage.bucket()
                blob = bucket.blob(f'property_images/{new_property.id}/{filename}')
                blob.upload_from_string(file.read(), content_type=file.content_type)

                image_url = blob.public_url

                new_image = Image(
                    property_id=new_property.id,
                    filename=filename,
                    storage_url=image_url
                )

                # Add the new_image object to the session
                db.session.add(new_image)

        # Commit the changes to the database
        db.session.commit()

        return jsonify({"message": "Property created successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    


# Get all properties
@bp.route('/property/all_properties', methods=['GET'])
def get_all_properties():
    page_number = request.args.get('page', 1, type=int)

    pagination_properties = Property.query.filter(Property.active == True).paginate(page=page_number, per_page=20)

    # If properties is None return a empty list
    if pagination_properties == None:
        return jsonify({"properties": [], "pages": 0}), 200
    
    properties = pagination_properties.items
    number_of_pages = pagination_properties.pages
    # init an empty list
    list_items_with_images = []


    for property_item in properties:
        listed_property = property_item.serialize()
        listed_property["property_images"] = [image.serialize() for image in property_item.images]

        # Add Firebase storage URLs for property images
        for image in listed_property["property_images"]:
            bucket = storage.bucket()
            blob = bucket.blob(f'property_images/{property_item.id}/{image["filename"]}')
            image["storage_url"] = blob.public_url

        list_items_with_images.append(listed_property)

    response_data = {
        "properties": list_items_with_images,
        "pages": number_of_pages
    }
    return jsonify(response_data)

# Get property by ID
@bp.route('/property/<property_id>', methods=['GET'])
def get_property(property_id):
    result = Property.query.get(property_id)

    if result == None:
        return jsonify({"msg":f"property of id{property_id} not found"}), 200
    
    if result.active == False:
        return jsonify("Property has been deactivated"), 200
    property_images = result.get_property_images()

    property_id_result = result.serialize()

    property_id_result['property_images'] = property_images
    return jsonify(property_id_result), 200

# Update a property availability
@bp.route('/property/update_property_availability/<realtor_id>/<property_id>', methods=['PATCH'])
def update_property_availability(realtor_id, property_id):
    property_details = Property.query.get(property_id)
    request_data = request.get_json()

    if property_details is None:
        return "Bad request", 404
    
    if str(property_details.owner_id) != str(realtor_id):
        return "Not owner", 403
    
    try:
        if request_data['action'] == "activate":
            property_details.active = True
            db.session.commit()
            return "Activated property!", 200
        elif request_data['action'] == 'deactivate':
            property_details.active = False
            db.session.commit()
            return "Deactivated property!", 200
        else:
            return "Bad request", 404
        
    except Exception as e:
        return "An error occured", 500


@bp.route('/property/update_property/<realtor_id>/<property_id>', methods=['PATCH'])
def update_property(realtor_id, property_id):
    property_details = Property.query.get(property_id)
    request_data = None

    if request.headers['Content-Type'] == 'application/json':
        request_data = request.get_json()

    elif request.form:
        request_data = {key: request.form[key] for key in request.form}
    if request_data is None:
        # If not JSON, assume form-data
        return jsonify({"error": "Invalid request format"}), 400
    print(request_data)

    if property_details is None:
        return jsonify({"error": "Property not found"}), 404
    if str(property_details.owner_id) !=str(realtor_id):
        return jsonify({"error": "Unauthorized"}), 403
    

    try: 
        allowed_fields = ['location', 'description', 'address', 'bedrooms', 'bathrooms',
                          'title', 'category', 'price', 'property_type', 'size']
        
        for field in allowed_fields:
            if field in request_data:
                setattr(property_details, field, request_data.get(field))
        db.session.commit()


       # Handle file upload
        files = request.files.getlist('file')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                bucket = storage.bucket()
                blob = bucket.blob(f'property_images/{property_details.id}/{filename}')
                blob.upload_from_string(file.read(), content_type=file.content_type)

                image_url = blob.public_url

                new_image = Image(
                    property_id=property_details.id,
                    filename=filename,
                    storage_url=image_url
                )

                # Add the new_image object to the session
                db.session.add(new_image)
            db.session.commit()

        return jsonify({"message":"Property Update successful"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
        



@bp.route('/property/delete_property/<realtor_id>/<property_id>', methods=['DELETE'])
def delete_property(realtor_id, property_id):
    property_details = Property.query.get(property_id)

    if property_details is None:
        return "Property not available", 404

    if str(property_details.owner_id) != str(realtor_id):
        return "Not owner", 403
    try:
        bucket = storage.bucket()
        blobs = bucket.list_blobs(prefix=f'property_images/{property_id}/')
        for blob in blobs:
            blob.delete()
        Image.query.filter_by(property_id=property_id).delete()

        db.session.delete(property_details)
        db.session.commit()
        return "Deleted successfully!", 200
    except Exception as e:
        print(e)
        db.session.rollback()
        return "An error occured", 500

        







@bp.get('/property/search_properties')
def search_properties():
    # Extract all arguments from request
    search_text = request.args.get('search_term')
    min_price = int(request.args.get('min_price', 0))
    max_price = int(request.args.get('max_price', 0))
    bedrooms = int(request.args.get('bedrooms', 0))
    bathrooms = int(request.args.get('bathrooms', 0))
    category = request.args.get('category', '').lower()
    property_type = request.args.get('property_type', '').lower()
    max_area = int(request.args.get("max_area", 0))
    page_number = request.args.get('page', 1, type=int)

    # define the base query with the search conditions
    query = Property.query.filter(
        func.lower(Property.location).like(f'%{search_text.lower()}%') |
        func.lower(Property.category).like(f'%{search_text.lower()}%') |
        func.lower(Property.description).like(f'%{search_text.lower()}%') |
        func.lower(Property.address).like(f'%{search_text.lower()}%')
    )

    # add additional filters based on the search criteria
    if category:
        query = query.filter(Property.category == category)
    if property_type:
        query = query.filter(Property.property_type == property_type)
    if min_price:
        query = query.filter(Property.price >= min_price)
    if max_price:
        query = query.filter(Property.price <= max_price)
    if bathrooms:
        query = query.filter(Property.bathrooms <= bathrooms)
    if bedrooms:
        query = query.filter(Property.bedrooms <= bedrooms)
    if max_area:
        query = query.filter(Property.size >= max_area)

    # query all searches
    results = query.paginate(page=page_number, per_page=20)

    if not results.items:
        return jsonify({"results": [], "pages": 0}), 200

    list_items_with_images = []

    # Iterate the properties while appending the list with images of the property
    for property_item in results.items:
        listed_property = property_item.serialize()
        # Get the property images
        property_images = [image.serialize() for image in property_item.images]
        # Add Firebase storage URLs for property images
        for image in property_images:
            blob_url = image["storage_url"]
            # You might need to adjust this part based on your image model structure
            # Ensure storage_url is a Firebase Storage URL
            image["storage_url"] = blob_url

        listed_property["property_images"] = property_images
        list_items_with_images.append(listed_property)

    return jsonify({"results": list_items_with_images, "pages": results.pages})



@bp.route('/property/recently_added', methods=['GET'])
def search_recently_added():
    results = Property.query.order_by(Property.date_created.desc()).limit(4)

    if results is None:
        return jsonify([]), 200

    recent_properties = []
    for item in results:
        recent_properties.append(item.serialize())

    return jsonify(recent_properties)
