from config import db
from datetime import datetime


class Property(db.Model):
    id = db.Column(db.String(255), primary_key=True)
    owner_id = db.Column(db.String(255), db.ForeignKey('realtor.realtor_id'),
                         index=True, unique=False)
    location = db.Column(db.String(255), index=True, unique=False)
    description = db.Column(db.Text, index=False, unique=False)
    address = db.Column(db.String(255), index=False, unique=False)
    bedrooms = db.Column(db.Integer, index=False, unique=False)
    bathrooms = db.Column(db.Integer, index=False, unique=False)
    category = db.Column(db.String(255), index=False, unique=False)
    title= db.Column(db.String(255),index=False, unique=False, nullable=True)
    price = db.Column(db.Float, index=False, unique=False)
    property_type = db.Column(db.String(255), index=False, unique=False)
    active = db.Column(db.Boolean, index=False, default=True, unique=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    size = db.Column(db.String(255), index=False, unique=False)

    def get_property_images(self):
        return [image.serialize() for image in self.images]

    def __repr__(self):
        return f'<Property "{self.id}">'

    # Return all properties in dictionary
    def serialize(self):
        return {
            "id": self.id,
            "owner_id": self.owner_id,
            "location": self.location,
            "description": self.description,
            "address": self.address,
            "bedrooms": self.bedrooms,
            "bathrooms": self.bathrooms,
            "category": self.category,
            "price": self.price,
            "property_type": self.property_type,
            "active": self.active,
            "date_created": self.date_created,
            "size": self.size
        }


class Image(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.String(255), db.ForeignKey('property.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    storage_url=db.Column(db.String(255), nullable=False)
    expiration_time = db.Column(db.DateTime, nullable=True)

    property = db.relationship('Property', backref=db.backref('images', lazy=True))

    def serialize(self):
        return {
            'filename': self.filename,
            'storage_url': self.storage_url,
            'expiration_time': self.expiration_time.isoformat() if self.expiration_time else None

        }


