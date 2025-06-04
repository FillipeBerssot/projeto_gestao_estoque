from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import purchases_bp
from .forms import PurchaseForm
from ..models import Purchase
from .. import db

@purchases_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_purchase():
    form = PurchaseForm()

    if form.validate_on_submit():
        new_purchase = Purchase(
            product_name=form.product_name.data,
            purchase_date=form.purchase_date.data,
            value=form.value.data,
            quantity=form.quantity.data,
            unit=form.unit.data,
            location=form.location.data,
            brand=form.brand.data,
            notes=form.notes.data,
            buyer=current_user
        )
        db.session.add(new_purchase)
        db.session.commit()

        flash('Nova compra adicionada com sucesso!', 'success')

        return redirect(url_for('purchases.add_purchase'))
    
    return render_template('add_purchase.html', title='Adicionar Nova Compra', form=form)

@purchases_bp.route('/list')
@login_required
def list_purchases():
    page = request.args.get('page', 1, type=int)
    PER_PAGE = 10

    search_term = request.args.get('search_product_name', None)

    query = current_user.purchases.order_by(Purchase.purchase_date.desc())

    if search_term:
        query = query.filter(Purchase.product_name.ilike(f'%{search_term}%'))

    pagination = query.paginate(
        page=page,
        per_page=PER_PAGE,
        error_out=False
    )

    user_purchases_on_page = pagination.items

    return render_template('list_purchases.html',
                           title='Minhas Compras',
                           purchases=user_purchases_on_page,
                           pagination=pagination,
                           search_term=search_term)