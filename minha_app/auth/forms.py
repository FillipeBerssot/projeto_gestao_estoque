from sqlalchemy import func
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_login import current_user
from ..models import User

class UpdateAccountForm(FlaskForm):
    username = StringField('Nome de Usuário',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Atualizar Foto de Perfil',
                        validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit_update = SubmitField('Atualizar Dados')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter(func.lower(User.username) == func.lower(username.data)).first()
            if user:
                raise ValidationError('Este nome de usuário já está em uso. Por favor, escolha outro.')
        
    def validate_email(self, email):
        if email.data.lower() != current_user.email.lower():
            user = User.query.filter(func.lower(User.email) == func.lower(email.data)).first()
            if user:
                raise ValidationError('Este email já está em uso. Por favor, escolha outro.')
            
class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Senha Atual', validators=[DataRequired()])
    new_password = PasswordField('Nova Senha', validators=[DataRequired(), Length(min=6)])
    confirm_new_password = PasswordField('Confirmar Nova Senha',
                                         validators=[DataRequired(), EqualTo('new_password', message='As senhas não coincidem.')])
    submit_password = SubmitField('Alterar Senha')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Solicitar Redefinição de Senha')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Não existe uma conta com este email. Você pode se registrar primeiro.')
        
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nova Senha', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Nova Senha',
                                     validators=[DataRequired(), EqualTo('password', message='As senhas não coincidem.')])
    submit = SubmitField('Redefinir Senha')