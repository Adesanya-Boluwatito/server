from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS

def create_app():
    app = Flask(__name__)

    CORS(app, supports_credentials=True)

    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.static_folder = 'static'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Boluwatito@localhost/real_estate_app'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    UPLOAD_FOLDER = '/path/to/your/uploads'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
