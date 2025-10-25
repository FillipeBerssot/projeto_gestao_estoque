import csv
import io
from flask import abort, render_template, redirect, url_for, flash, request, Response, jsonify
from flask_login import login_required, current_user
from . import purchases_bp
from .forms import PurchaseForm
from ..models import Purchase
from .. import db
from datetime import date, datetime

def _get_filtered_purchases_query():
    search_term = request.args.get('search_product_name', None)
    filter_data_str = request.args.get('filter_date', None)

    query = Purchase.query.filter_by(buyer=current_user)

    if search_term:
        query = query.filter(Purchase.product_name.ilike(f'%{search_term}%'))

    if filter_data_str:
        try:
            specific_date_to_filter = datetime.strptime(filter_data_str, '%Y-%m-%d').date()
            query = query.filter(Purchase.purchase_date == specific_date_to_filter)
        except ValueError:
            flash('Formato de data para filtro inválido. Use AAAA-MM-DD', 'warning')

    return query

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

    query = _get_filtered_purchases_query()

    pagination = query.order_by(Purchase.purchase_date.desc()).paginate(
        page=page,
        per_page=PER_PAGE,
        error_out=False
    )

    user_purchases_on_page = pagination.items

    return render_template('list_purchases.html',
                           title='Minhas Compras',
                           purchases=user_purchases_on_page,
                           pagination=pagination,
                           search_term=request.args.get('search_product_name', ''),
                           filter_date_str=request.args.get('filter_date', ''))

@purchases_bp.route('/edit/<int:purchase_id>', methods=['GET', 'POST'])
@login_required
def edit_purchase(purchase_id):
    purchase_to_edit = db.get_or_404(Purchase, purchase_id)

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

@purchases_bp.route('/purchase/details/<int:purchase_id>')
@login_required
def purchase_details(purchase_id):
    purchase = db.get_or_404(Purchase, purchase_id)
    if purchase.buyer != current_user:
        abort(403)
    
    purchase_data = {
        'product_name': purchase.product_name,
        'purchase_date': purchase.purchase_date.strftime('%d/%m/%Y'),
        'value': f'R$ {purchase.total_value:.2f}',
        'unit_value': f'R$ {purchase.value:.2f}',
        'quantity': f'{purchase.quantity}',
        'unity': f'{purchase.unit}',
        'brand': purchase.brand if purchase.brand else 'Não informado',
        'location': purchase.location if purchase.location else 'Não informado',
        'notes': purchase.notes if purchase.notes else 'Nenhuma observação.'
    }
    
    return jsonify(purchase_data)

@purchases_bp.route('/delete/<int:purchase_id>', methods=['POST'])
@login_required
def delete_purchase(purchase_id):
    purchase_to_delete = db.get_or_404(Purchase, purchase_id)

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

@purchases_bp.route('/export')
@login_required
def export_csv():
    query = _get_filtered_purchases_query().order_by(Purchase.purchase_date.asc())
    results = query.all()

    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')

    header = [
        'ID', 'Data da Compra', 'Nome do Produto', 'Marca', 'Quantidade',
        'Unidade', 'Valor Total (R$)', 'Preço Unitário (R$)', 'Local', 'Observações'
    ]

    writer.writerow(header)

    for purchase in results:
        row = [
            purchase.id,
            purchase.purchase_date.strftime('%Y-%m-%d'),
            purchase.product_name,
            purchase.brand,
            purchase.quantity,
            purchase.unit,
            str(purchase.value).replace('.',','),
            purchase.location,
            purchase.notes
        ]
        writer.writerow(row)

    csv_data = output.getvalue()

    encoded_csv_data = csv_data.encode('utf-8-sig')

    return Response(
        encoded_csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=relatorio_compras.csv"}
    )