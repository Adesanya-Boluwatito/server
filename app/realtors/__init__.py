from flask import Blueprint

bp = Blueprint("realtors", __name__)

from app.realtors import routes