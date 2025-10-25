from flask_wtf import FlaskForm
from wtforms import StringField, DateField, FloatField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange
from datetime import date

class PurchaseForm(FlaskForm):
    product_name = StringField('Nome do Produto',
                                validators=[DataRequired(message="O nome do produto é obrigatório."), Length(min=2, max=100)])
    purchase_date = DateField('Data da Compra',
                               default=date.today,
                               validators=[DataRequired(message="A data da compra é obrigatória.")])
    value = FloatField('Preço Unitário (R$)',
                       validators=[DataRequired(message="O valor deve conter somente números. Utilize ponto para diferenciar reais de centavos"), NumberRange(min=0.01, message='O valor deve ser positivo.')])
    quantity = FloatField('Quantidade',
                          validators=[DataRequired(message="A quantidade deve conter somente números."), NumberRange(min=0.001, message='A quantiadade deve ser positiva.')])
    unit = StringField('Unidade (ex: kg, g, un, L, cx...)',
                       validators=[DataRequired(message="A unidade é obrigatória."), Length(max=50)])
    location = StringField('Local da Compra (Opcional)',
                           validators=[Length(max=100)])
    brand = StringField('Marca (Opcional)',
                        validators=[Length(max=100)])
    notes = TextAreaField('Observações (Opcional)')
    submit = SubmitField('Registrar Compra')    
