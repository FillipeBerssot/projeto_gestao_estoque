from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Inicializa as extensões (sem passar a app ainda)
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login' # Note 'auth.login' - 'auth' é o nome do Blueprint
login_manager.login_message = "Por favor, faça login para acessar esta página."
login_manager.login_message_category = "info"

def create_app():
    app = Flask(__name__, instance_relative_config=True) # instance_relative_config=True é importante

    # Configurações da aplicação (podemos mover para um config.py depois)
    app.config['SECRET_KEY'] = 'minha_chave_secreta_muito_segura_12345'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meu_controle_de_estoque.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializa as extensões com a aplicação
    db.init_app(app)
    login_manager.init_app(app)

    # Importar modelos aqui é importante para o user_loader e para criar tabelas
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id)) # Ou db.session.get(User, int(user_id))

    # Registrar Blueprints
    from .auth import routes as auth_routes # Importa as rotas do Blueprint de autenticação
    app.register_blueprint(auth_routes.auth_bp) # Registra o Blueprint

    # (Opcional) Registrar um Blueprint 'main' para a rota ola_mundo
    # from .main import routes as main_routes
    # app.register_blueprint(main_routes.main_bp)

    # Rota de teste (pode ser movida para um Blueprint 'main' depois)
    @app.route('/hello')
    def hello():
        return 'Olá da Fábrica de Aplicação!'

    return app