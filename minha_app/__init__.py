import os
from config import config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from dotenv import load_dotenv

# Inicializa as extensões
load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login' # Rota para login dentro do Blueprint 'auth'
login_manager.login_message = "Por favor, faça login para acessar esta página."
login_manager.login_message_category = "info"
migrate = Migrate()
mail = Mail()

def create_app(config_name='default'):
    app = Flask(__name__, instance_relative_config=False)

    app.config.from_object(config[config_name])

    # Inicializa as extensões com a aplicação
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # Importar modelos aqui é importante para o user_loader e para criar tabelas
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Registrar Blueprints
    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    from .purchases import purchases_bp
    app.register_blueprint(purchases_bp)

    from .dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)

    return app