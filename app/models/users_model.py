from flask_login import UserMixin

from config import db



user_favorite_properties = db.Table(
    'user_favorite_properties',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('property_id', db.String(255), db.ForeignKey('property.id'), primary_key=True)
)

favorite_properties = db.relationship('Property', secondary=user_favorite_properties, backref='favorited_by')

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    otp_secret = db.Column(db.String(16))
    favorite_properties = db.relationship('Property', secondary=user_favorite_properties, backref='favorited_by')

    @property
    def is_realtor(self):
        return hasattr(self, 'realtor') and self.realtor is not None