from flask import Blueprint

bp = Blueprint("properties", __name__)


from properties import routes