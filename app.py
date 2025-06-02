from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

#Chave secreta para proteger sessões e cookies "Lembrar de criar um arquivo de configuração separado para produção"
app.config['SECRET_KEY'] = 'minha_chave_secreta_muito_segura_12345'

# Configuração do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meu_controle_de_estoque.db'
# Configuração para não rastrear modificações de objetos
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---- Modelo de Usuario ----
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'
# ----------------------------

# Rota Inicial
@app.route('/')
def ola_mundo():
    return 'Olá, Mundo com Flask e Poetry! Meu sistema de controle de estoque está no ar!'


if __name__ == '__main__':
    app.run(debug=True)