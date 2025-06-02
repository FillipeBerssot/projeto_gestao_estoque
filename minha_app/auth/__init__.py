from flask import Blueprint

# Cria um objeto Blueprint.
# 'auth' é o nome do Blueprint.
# __name__ ajuda o Flask a localizar a raiz do Blueprint (para templates, etc.).
# url_prefix='/auth' (opcional): todas as rotas deste Blueprint começarão com /auth (ex: /auth/login)
auth_bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='../templates/auth')

# Importar as rotas no final para evitar importações circulares
from . import routes