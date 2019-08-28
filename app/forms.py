from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, IntegerField, DecimalField, DateField
from wtforms.validators import DataRequired


class JinnForm(FlaskForm):
    rentcode = TextAreaField('Enter RentCode')
    tenantname = TextAreaField('Enter Tenant Name')
    propaddr = TextAreaField('Enter Propaddr')
    submit = SubmitField('Submit')


class RentForm(FlaskForm):
    rentcode = TextAreaField('RentCode', validators=[DataRequired()])
    tenantname = TextAreaField('Tenant Name')
    mailto = TextAreaField('Mailto')
    rentpa = DecimalField('Annual Rent')
    arrears = DecimalField('Arrears')
    advarr = TextAreaField('AdvArr')
    lastrentdate = DateField('Last rent date')
    frequency = IntegerField('Frequency')
    datecode = TextAreaField('Date code')
    actype = TextAreaField('AcType')
    tenure = TextAreaField('Tenure')
    source = TextAreaField('Source')
    deedtype = TextAreaField('Deed type')
    status = TextAreaField('Status')
    salegrade_id = IntegerField('Sale grade')
    price = DecimalField('Price')
    email = TextAreaField('Email')
    note = TextAreaField('Note')
    landlord = TextAreaField('Landlord')
    propaddr = TextAreaField('Propaddr')
    agent = TextAreaField('Agent')
    submit = SubmitField('Submit')
