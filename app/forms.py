from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, IntegerField, DecimalField, DateField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, \
    Length
from app.models import User, Rent


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

                
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')


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
