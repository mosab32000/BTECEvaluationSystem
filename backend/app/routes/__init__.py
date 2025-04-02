from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
evaluation_bp = Blueprint('evaluation', __name__, url_prefix='/evaluation')

from . import auth, evaluation