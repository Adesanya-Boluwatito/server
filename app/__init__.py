import os
from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS
from dotenv import load_dotenv


def create_app():
    load_dotenv()

    app = Flask(__name__)

    CORS(app, supports_credentials=True)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
    app.static_folder = 'static'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', '/default/path/to/uploads')


    from app.config import db
    db.init_app(app)

    login_manager = LoginManager(app)

    from app.user import bp as user_bp
    from app.properties import bp as properties_bp
    from app.realtors import bp as realtors_bp

    app.register_blueprint(user_bp)
    app.register_blueprint(properties_bp)
    app.register_blueprint(realtors_bp)

    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        from app.user.routes import User
        return User.query.get(int(user_id))

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(debug=True)
