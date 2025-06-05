from flask import render_template, current_app
from flask_login import login_required, current_user
from . import dashboard_bp
from ..models import Purchase
from .. import db
from datetime import date, datetime
import calendar

@dashboard_bp.route('/')
@login_required
def view_dashboard():
    hoje = date.today()
    primeiro_dia_mes_atual = hoje.replace(day=1)
    ultimo_dia_do_mes_atual_num = calendar.monthrange(hoje.year, hoje.month)[1]
    ultimo_dia_mes_atual = hoje.replace(day=ultimo_dia_do_mes_atual_num)

    compras_mes_atual = Purchase.query.with_parent(current_user).filter(
        Purchase.purchase_date >= primeiro_dia_mes_atual,
        Purchase.purchase_date <= ultimo_dia_mes_atual
    ).order_by(Purchase.purchase_date.desc()).all()

    total_gasto_mes_atual = 0
    for compra in compras_mes_atual:
        total_gasto_mes_atual += compra.value

    nome_mes_atual = hoje.strftime("%B de %Y")

    return render_template('dashboard.html',
                           title='Meu Dashboard',
                           nome_mes_atual=nome_mes_atual,
                           total_gasto_mes_atual=total_gasto_mes_atual,
                           compras_mes_atual=compras_mes_atual)