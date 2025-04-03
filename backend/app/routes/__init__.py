from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
evaluation_bp = Blueprint('evaluation', __name__, url_prefix='/evaluation')
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

from . import auth, evaluation, admin