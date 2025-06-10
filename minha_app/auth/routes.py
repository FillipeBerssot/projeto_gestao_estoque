import os
import secrets
from sqlalchemy import func
from PIL import Image
from flask import current_app
from .forms import UpdateAccountForm, ChangePasswordForm
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import auth_bp
from ..models import User
from .. import db


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    if current_user.image_file != 'default.jpg':
        old_picture_path = os.path.join(current_app.root_path, 'static/profile_pics', current_user.image_file)
        if os.path.exists(old_picture_path):
            os.remove(old_picture_path)

    return picture_fn

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        error = None
        if not username:
            error = 'Nome de usuário é obrigatório.'
        elif not email:
            error = 'Email é obrigatório.'
        elif not password:
            error = 'Senha é obrigatória.'
        elif password != confirm_password:
            error = 'As senhas não coincidem!'

        if error is None:
            user_by_username = User.query.filter_by(username=username).first()
            user_by_email = User.query.filter_by(email=email).first()

            if user_by_username:
                error = f"Usuário '{username}' já existe."
            elif user_by_email:
                error = f"Email '{email}' já está registrado."

        if error is None:
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registro bem-sucedido! Por favor, faça o login.', 'success')
            return redirect(url_for('auth.login'))
        
        if error:
            flash(error, 'danger')

    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter(func.lower(User.username) == func.lower(username)).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Login bem-sucedido!', 'success')

            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.view_dashboard'))
        else:
            flash('Nome de usuário ou senha inválidos. Tente novamente.', 'danger')

    return render_template('auth/login.html')

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

    if password_form.validate_on_submit() and 'submit_password' in request.form:
        if current_user.check_password(password_form.current_password.data):
            current_user.set_password(password_form.new_password.data)
            db.session.commit()
            flash('Sua senha foi alterada com sucesso!', 'success')
            return redirect(url_for('auth.profile'))
        else:
            flash('Senha atual incorreta. Por favor, tente novamente.', 'danger')
            
    elif update_form.validate_on_submit() and 'submit_update' in request.form:
        if update_form.picture.data:
            picture_file = save_picture(update_form.picture.data)
            current_user.image_file = picture_file
        
        current_user.username = update_form.username.data
        current_user.email = update_form.email.data
        db.session.commit()
        flash('Sua conta foi atualizada!', 'success')
        return redirect(url_for('auth.profile'))

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('profile.html', title='Perfil',
                           image_file=image_file,
                           update_form=update_form,
                           password_form=password_form)