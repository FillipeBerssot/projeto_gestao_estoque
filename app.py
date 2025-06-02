from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required


app = Flask(__name__)

#Chave secreta para proteger sessões e cookies "Lembrar de criar um arquivo de configuração separado para produção"
app.config['SECRET_KEY'] = 'minha_chave_secreta_muito_segura_12345'

# Configuração do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meu_controle_de_estoque.db'
# Configuração para não rastrear modificações de objetos
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ---- Configurações do Flask-login ----
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'info'
# ---------------------------------------


# ---- Modelo de Usuario ----
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    # Método para definir a senha(HASH)
    def set_passowrd(self, password):
        self.password_hash = generate_password_hash(password)
    
    # Método para verificar a senha
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'
# ----------------------------


# ---- User Loader para Flask-Login ----
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
# ---------------------------------------


# Rota Inicial
@app.route('/')
def ola_mundo():
    return 'Olá, Mundo com Flask e Poetry! Meu sistema de controle de estoque está no ar!'


if __name__ == '__main__':
    app.run(debug=True)