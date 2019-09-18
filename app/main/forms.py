from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, DecimalField, FieldList, FormField, IntegerField, \
    PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import Income, Incomealloc


class IncomeAllocForm(FlaskForm):
    incall_id = IntegerField('Incall_d')
    income_id = IntegerField('Income_id')
    alloc_id = IntegerField('Alloc_id')
    rentcode = StringField('Rentcode', validators=[DataRequired()])
    amount = DecimalField('Amount')
    name = StringField('Landlord')
    inc_type = StringField('Type of income')


class IncomeForm(FlaskForm):
    id = IntegerField('Id')
    paydate = DateField('Paydate')
    total = DecimalField('Total')
    payer = StringField('Payer')
    bankaccount = StringField('Bank account')
    typepayment = StringField('Payment type')
    incomeallocations = FieldList(FormField(IncomeAllocForm))
    submit = SubmitField('Save changes')

