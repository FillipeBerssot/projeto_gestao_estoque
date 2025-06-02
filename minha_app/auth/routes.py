from flask import render_template, redirect, url_for, flash 
from flask_login import login_user, logout_user, login_required
from . import auth_bp # Importa o Blueprint definido em auth/__init__.py
from ..models import User # Importa o modelo User de minha_app/models.py
from .. import db # Importa db de minha_app/__init__.py

# Exemplo de rota (vamos construir o login/registro aqui)
@auth_bp.route('/login_test')
def login_test():
    return "Página de login do Blueprint Auth!"