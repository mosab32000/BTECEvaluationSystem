from flask import Blueprint

castle_grok = Blueprint('castle_grok', __name__, 
                       template_folder='../templates/castle_grok',
                       static_folder='../static',
                       static_url_path='/castle_grok/static')

from . import routes