from flask import Blueprint

bp = Blueprint("realtors", __name__)

from realtors import routes