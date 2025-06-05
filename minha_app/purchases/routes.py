from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import purchases_bp
from .forms import PurchaseForm
from ..models import Purchase
from .. import db
from datetime import date, datetime

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
    filter_date_str = request.args.get('filter_date', None)

    specific_date_to_filter = None

    query = current_user.purchases.order_by(Purchase.purchase_date.desc())

    if search_term:
        query = query.filter(Purchase.product_name.ilike(f'%{search_term}%'))

    if filter_date_str:
        try:
            specific_date_to_filter = datetime.strptime(filter_date_str, '%Y-%m-%d').date()
            query = query.filter(Purchase.purchase_date == specific_date_to_filter)
        except ValueError:
            flash('Formato de data para filtro inválido. Use AAAA-MM-DD', 'warning')
            filter_date_str = None

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
                           search_term=search_term,
                           filter_date_str=filter_date_str)

@purchases_bp.route('/edit/<int:purchase_id>', methods=['GET', 'POST'])
@login_required
def edit_purchase(purchase_id):
    purchase_to_edit = Purchase.query.get_or_404(purchase_id)

    if purchase_to_edit.buyer != current_user:
        flash('Operação não permitida. Você só pode editar suas próprias compras.', 'danger')
        return redirect(url_for('purchases.list_purchases'))
    
    form = PurchaseForm(obj=purchase_to_edit if request.method == 'GET' else None)

    if form.validate_on_submit():
        purchase_to_edit.product_name = form.product_name.data
        purchase_to_edit.purchase_date = form.purchase_date.data
        purchase_to_edit.value = form.value.data
        purchase_to_edit.quantity = form.quantity.data
        purchase_to_edit.unit = form.unit.data
        purchase_to_edit.location = form.location.data
        purchase_to_edit.brand = form.brand.data
        purchase_to_edit.notes = form.notes.data

        db.session.commit()
        flash('Compra atualizada com sucesso!', 'success')
        return redirect(url_for('purchases.list_purchases'))
    
    return render_template('edit_purchase.html',
                           title='Editar Compra',
                           form=form,
                           purchase_id=purchase_id)

@purchases_bp.route('/delete/<int:purchase_id>', methods=['POST'])
@login_required
def delete_purchase(purchase_id):
    purchase_to_delete = Purchase.query.get_or_404(purchase_id)

    if purchase_to_delete.buyer != current_user:
        flash('Operação não permitida. Você só pode excluir suas próprias compras.', 'danger')
        return redirect(url_for('purchases.list_purchases'))
    
    try:
        db.session.delete(purchase_to_delete)
        db.session.commit()
        flash('Compra excluída com sucesso!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir a compra: {e}', 'danger')

    return redirect(url_for('purchases.list_purchases'))