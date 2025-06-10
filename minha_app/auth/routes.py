from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import auth_bp
from ..models import User
from .. import db


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

        user = User.query.filter_by(username=username).first()

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
