from flask import current_app
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timezone
from . import db 

# ---- Modelo de Usuario ----
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, server_default='default.jpg')
    purchases = db.relationship('Purchase', backref='buyer', lazy='dynamic', cascade="all, delete-orphan")

    # Método para Token
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})
    
    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=expires_sec)['user_id']
        except:
            return None
        return User.query.get(user_id)

    # Método para definir a senha(HASH)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Método para verificar a senha
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'
    
# ---- Modelo de Produtos (Compras) ----
class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    purchase_date = db.Column(db.Date, nullable=False, default=date.today)
    value = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=True)
    brand = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    @property
    def total_value(self):
        value = self.value or 0
        quantity = self.quantity or 0
        return value * quantity

    def __repr__(self):
        return f'<Purchase {self.product_name} -R${self.total_value:.2f}>'