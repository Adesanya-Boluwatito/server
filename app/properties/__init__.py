from flask import Blueprint

bp = Blueprint("properties", __name__)


from app.properties import routes