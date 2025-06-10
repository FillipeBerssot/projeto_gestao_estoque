from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# Inicializa as extensões
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login' # Rota para login dentro do Blueprint 'auth'
login_manager.login_message = "Por favor, faça login para acessar esta página."
login_manager.login_message_category = "info"
migrate = Migrate()

def create_app():
    app = Flask(__name__, instance_relative_config=True) # instance_relative_config=True é importante

    # Configurações da aplicação (podemos mover para um config.py depois)
    app.config['SECRET_KEY'] = 'minha_chave_secreta_muito_segura_12345'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meu_controle_de_estoque.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializa as extensões com a aplicação
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

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