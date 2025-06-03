from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
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