from flask_login import UserMixin
from datetime import datetime
from config import db

# Realtor model


class Realtor(db.Model, UserMixin):
    id = db.Column(db.String(255), primary_key=True)
    realtor_id = db.Column(db.String(255),index=True, unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('realtor', lazy=True))
    company_name = db.Column(db.String(255), index=False, unique=False, nullable=False)
    description = db.Column(db.Text(255), index=False, unique=False)
    profile_picture = db.Column(db.String(255), index=False, unique=False)
    company_mail = db.Column(db.String(255), index=False,
                             unique=False, nullable=True)
    website_url = db.Column(db.String(255), index=False,
                            unique=False, nullable=True)
    contact = db.Column(db.String(255), index=False, unique=False, nullable=True)
    active = db.Column(db.Boolean, index=False, default=True, unique=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    properties = db.relationship(
        'Property', backref='realtor', lazy='dynamic')
    # followers = db.relationship(
    #     'Realtor_follower', backref="realtor",  cascade='all, delete, delete-orphan')

    def __repr__(self):
        return f'<Realtor "{self.company_name}">'

    def serialize(self):
        return {
            "id": self.id,
            "realtor_id": self.realtor_id,
            "company_name": self.company_name,
            "description": self.description,
            "profile_picture": self.profile_picture,
            "date_created": self.date_created,
            "company_mail": self.company_mail,
            "active": self.active,
            "website_url": self.website_url,
            "contact": self.contact,
        }