import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configurações base que se aplicam a todos os ambientes."""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'stmp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    MAIL_DEFAULT_SENDER = (
    os.environ.get('MAIL_FROM_NAME', 'Controle de Estoque'),
    os.environ.get('MAIL_FROM_EMAIL', os.environ.get('MAIL_USERNAME'))
)

class DevelopmentConfig(Config):
    """Configurações para o ambiente de Desenvolvimento."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')

class TestingConfig(Config):
    """Configurações para o ambiente de Teste."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # Usa banco de dados em memória
    WTF_CSRF_ENABLED = False # Desabilita CSRF para os testes

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}