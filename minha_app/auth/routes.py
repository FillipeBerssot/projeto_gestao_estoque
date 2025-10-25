import os
import secrets
from sqlalchemy import func
from PIL import Image
from flask import current_app
from .forms import UpdateAccountForm, ChangePasswordForm, UpdatePictureForm
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from . import auth_bp
from ..models import User
from .. import db, mail
from .forms import RequestResetForm, ResetPasswordForm, RegistrationForm, LoginForm


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    output_size = (400, 400)
    i = Image.open(form_picture).convert("RGB")
    i.thumbnail(output_size)
    i.save(picture_path, format='JPEG', quality=85)

    if current_user.image_file != 'default.jpg':
        old_picture_path = os.path.join(current_app.root_path, 'static/profile_pics', current_user.image_file)
        if os.path.exists(old_picture_path):
            os.remove(old_picture_path)

    return picture_fn

def send_reset_email(user):
    token = user.get_reset_token()

    msg = Message('Redefinição de Senha - Controle de Estoque',
                  sender=os.environ.get('MAIL_USERNAME'),
                  recipients=[user.email])
    msg.body = render_template('email/reset_password.txt',
                               user=user,
                               token=token)
    mail.send(msg)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.view_dashboard'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Sua conta foi criada com sucesso! Você já pode fazer o login.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('auth/register.html', title='Registrar', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.view_dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter(func.lower(User.email) == func.lower(form.email.data)).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login bem-sucedido!', 'success')
            return redirect(next_page or url_for('dashboard.view_dashboard'))
        else:
            flash('Login inválido! Por favor, verifique o email e a senha.', 'danger')

    return render_template('auth/login.html', title='Login', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado com sucesso!', 'info')
    return redirect(url_for('dashboard.view_dashboard'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    update_form = UpdateAccountForm(obj=current_user)
    password_form = ChangePasswordForm()
    picture_form = UpdatePictureForm()

    if picture_form.picture.data and picture_form.validate_on_submit():
        picture_file = save_picture(picture_form.picture.data)
        current_user.image_file = picture_file
        db.session.commit()
        flash('Sua foto de perfil foi atualizada!', 'success')
        return redirect(url_for('auth.profile'))

    is_password_post = (
        request.method == 'POST' and (
            password_form.current_password.name in request.form or
            password_form.new_password.name in request.form or
            password_form.confirm_new_password.name in request.form or
            'submit_password' in request.form
        )
    )

    if is_password_post:
        is_valid = password_form.validate_on_submit()
        if is_valid and not current_user.check_password(password_form.current_password.data):
            password_form.current_password.errors.append('Senha atual incorreta.')
            is_valid = False
        if is_valid:
            current_user.set_password(password_form.new_password.data)
            db.session.commit()
            flash('Senha alterada com sucesso!', 'success')
            return redirect(url_for('auth.profile'))
        else:
            flash('Corrija os erros destacados abaixo.', 'danger')

    elif 'submit_update' in request.form and update_form.validate_on_submit():        
        current_user.username = update_form.username.data
        current_user.email = update_form.email.data
        db.session.commit()
        flash('Sua conta foi atualizada!', 'success')
        return redirect(url_for('auth.profile'))
    
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template(
        'auth/profile.html', 
        title='Perfil',
        image_file=image_file,
        update_form=update_form,
        password_form=password_form,
        picture_form=picture_form)

@auth_bp.route("/reset_password", methods=['GET', 'POST'])
def request_reset():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.view_dashboard'))
    form = RequestResetForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Um email com as instruções para redefinir sua senha foi enviado.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('request_reset.html', title='Redefinir Senha', form=form)

@auth_bp.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.view_dashboard'))
    
    user = User.verify_reset_token(token)
    if user is None:
        flash('O token é inválido ou expirou.', 'warning')
        return redirect(url_for('auth.request_reset'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Sua senha foi atualizada! Você já pode fazer o login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('reset_password.html', title='Redefinir Senha', form=form)