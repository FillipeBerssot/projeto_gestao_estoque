from flask import flash, render_template, current_app, request
from flask_login import login_required, current_user
from sqlalchemy import func
from . import dashboard_bp
from ..models import Purchase
from .. import db
from datetime import date, datetime
import calendar


MONTH_OPTIONS = {
    1:'Janeiro', 2:'Fevereiro', 3:'Março', 4:'Abril',
    5:'Maio', 6:'Junho', 7:'Julho', 8:'Agosto',
    9:'Setembro', 10:'Outubro', 11:'Novembro', 12:'Dezembro'
}

@dashboard_bp.route('/')
@login_required
def view_dashboard():
    hoje = date.today()

    try:
        selected_year = int(request.args.get('filter_year', hoje.year))
        selected_month = int(request.args.get('filter_month', hoje.month))
        if not (1 <= selected_month <= 12): raise ValueError('Mês inválido')
    except (ValueError, TypeError):
        flash('Mês ou ano de filtro inválido. Mostrando período atual.', 'warning')
        selected_year = hoje.year
        selected_month = hoje.month

    primeiro_dia_mes = date(selected_year, selected_month, 1)
    ultimo_dia_do_mes_num = calendar.monthrange(selected_year, selected_month)[1]
    ultimo_dia_mes = date(selected_year, selected_month, ultimo_dia_do_mes_num)

    query_base_periodo = Purchase.query.with_parent(current_user).filter(
        Purchase.purchase_date >= primeiro_dia_mes,
        Purchase.purchase_date <= ultimo_dia_mes
    )

    total_gasto_mes = db.session.query(db.func.sum(Purchase.value)).filter(
        Purchase.user_id == current_user.id,
        Purchase.purchase_date >= primeiro_dia_mes,
        Purchase.purchase_date <= ultimo_dia_mes
    ).scalar() or 0.0

    page = request.args.get('page', 1, type=int)
    PER_PAGE = 10
    pagination = query_base_periodo.order_by(Purchase.purchase_date.desc()).paginate(
        page=page,
        per_page=PER_PAGE,
        error_out=False
    )

    compras_do_periodo_paginadas = pagination.items

    nome_mes_selecionado = f'{MONTH_OPTIONS[selected_month]} de {selected_year}'

    return render_template('dashboard.html',
                           title='Meu Dashboard',
                           nome_mes_selecionado=nome_mes_selecionado,
                           total_gasto_mes=total_gasto_mes,
                           compras_mes_atual=compras_do_periodo_paginadas,
                           pagination=pagination,
                           month_options=MONTH_OPTIONS,
                           selected_month=selected_month,
                           selected_year=selected_year)