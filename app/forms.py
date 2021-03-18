from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, TextAreaField, IntegerField, DecimalField, DateField, validators
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


# TODO: We may or may nood need this form depending on how we handle sending emails
class PrEmailForm(FlaskForm):
    email = StringField('email', [validators.Email(message='Include an email address'), DataRequired()],
                        render_kw={"placeholder": "enter email to"})
    subject = StringField('subject', [validators.DataRequired(message='Include an email subject')],
                          render_kw={"placeholder": "enter email subject"})
    submit = SubmitField('save and send payrequest', id='savehtml')


class PrPostForm(FlaskForm):
    mailaddr = SelectField('mailaddr')
    submit = SubmitField('save and send payrequest', id='savehtml')

