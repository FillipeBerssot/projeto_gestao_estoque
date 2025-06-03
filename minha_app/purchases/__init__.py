from flask import Blueprint

purchases_bp = Blueprint('purchases', __name__, url_prefix='/purchases', template_folder='../templates/purchases')

from . import routes, forms