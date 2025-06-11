from minha_app.models import Purchase, User, db
from datetime import date

def test_add_purchase_page_access(logged_in_client):
    response = logged_in_client.get('/purchases/add')

    assert response.status_code == 200
    assert b"Adicionar Nova Compra" in response.data

def test_add_purchase_success_and_redirect(logged_in_client, app):
    response = logged_in_client.post('/purchases/add', data={
        'product_name': 'Produto de Teste',
        'purchase_date': '2025-06-11',
        'value': 12.34,
        'quantity': 2.5,
        'unit': 'kg',
        'location': 'Mercado Teste',
        'brand': 'Marca Teste',
        'notes': 'Nota de Teste'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Nova compra adicionada com sucesso!" in response.data

    with app.app_context():
        purchase = Purchase.query.order_by(Purchase.id.desc()).first()

        assert purchase is not None
        assert purchase.product_name == 'Produto de Teste'
        assert purchase.value == 12.34

def test_add_purchase_shows_on_list(logged_in_client):
    nome_do_produto_teste = 'Leite Condensado Teste'

    logged_in_client.post('/purchases/add', data={
        'product_name': nome_do_produto_teste,
        'purchase_date': '2025-06-11',
        'value': 12.34,
        'quantity': 1,
        'unit': 'un'
    })

    response = logged_in_client.get('/purchases/list')

    assert response.status_code == 200
    assert bytes(nome_do_produto_teste, 'utf-8') in response.data

def test_edit_purchase(logged_in_client, app, test_user):
    with app.app_context():
        fresh_test_user = db.session.get(User, test_user.id)

        purchase = Purchase(product_name='Produto Original', value=10.0, quantity=1, unit='un', buyer=fresh_test_user)
        db.session.add(purchase)
        db.session.commit()
        purchase_id = purchase.id

    response = logged_in_client.post(f'/purchases/edit/{purchase_id}', data={
        'product_name': 'Produto Editado',
        'purchase_date': '2025-01-01',
        'value': 99.99,
        'quantity': 5,
        'unit': 'cx'
    }, follow_redirects=True)

    assert response.status_code == 200 
    assert b"Compra atualizada com sucesso!" in response.data

    with app.app_context():
        edited_purchase = db.session.get(Purchase, purchase_id)
        assert edited_purchase.product_name == 'Produto Editado'
        assert edited_purchase.value == 99.99

def test_delete_purchase(logged_in_client, app, test_user):
    with app.app_context():
        fresh_test_user = db.session.get(User, test_user.id)

        purchase_to_delete = Purchase(product_name='Produto a Deletar', value=5, quantity=1, unit='un', buyer=fresh_test_user)
        db.session.add(purchase_to_delete)
        db.session.commit()
        purchase_id = purchase_to_delete.id
      
        assert db.session.get(Purchase, purchase_id) is not None

    response = logged_in_client.post(f'/purchases/delete/{purchase_id}', follow_redirects=True)

    assert response.status_code == 200
    assert "Compra excluída com sucesso!" in response.data.decode('utf-8')

    with app.app_context():
        deleted_purchase = db.session.get(Purchase, purchase_id)
        assert deleted_purchase is None

def test_user_cannot_edit_other_user_purchase(client, app, test_user, test_user2):
    with app.app_context():
        fresh_test_user = db.session.get(User, test_user.id)
        
        purchase = Purchase(product_name='Compra Secreta', value=100, quantity=1, unit='un', buyer=fresh_test_user)
        db.session.add(purchase)
        db.session.commit()
        purchase_id = purchase.id
    
    client.post('/auth/login', data={'username': test_user2.username, 'password': 'password456'})

    response_edit = client.post(f'/purchases/edit/{purchase_id}', data={'product_name': 'Produto Hackeado'}, follow_redirects=True)
    assert response_edit.status_code == 200
    assert "Operação não permitida. Você só pode editar suas próprias compras." in response_edit.data.decode('utf-8')

    response_delete = client.post(f'/purchases/delete/{purchase_id}', follow_redirects=True)
    assert response_delete.status_code == 200
    assert "Operação não permitida. Você só pode excluir suas próprias compras." in response_delete.data.decode('utf-8')

    with app.app_context():
        p = db.session.get(Purchase, purchase_id)
        assert p is not None
        assert p.product_name == 'Compra Secreta'
