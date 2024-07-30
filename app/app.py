# app.py
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from user import bp
from properties import bp as properties_bp
from realtors import bp as realtors_bp
from config import db
from user.routes import User




app = Flask(__name__)

###################
from flask import Flask
from flask_cors import CORS

# app = Flask(__name__)
CORS(app, supports_credentials=True)  # Enable CORS for all routes

# Your routes and other configurations...



app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.static_folder = 'static'

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Boluwatito@localhost/real_estate_app'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:malikahmed@localhost/real_estate_app'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
UPLOAD_FOLDER = 'C:\\Users\\user\\Desktop\\Hostel app\\server\\app\\uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER




db.init_app(app)
login_manager = LoginManager(app)




app.register_blueprint(bp)
app.register_blueprint(properties_bp)
app.register_blueprint(realtors_bp)



with app.app_context():
    db.create_all()

# Import routes, models, and utils



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == "__main__":
    app.run(debug=True)
