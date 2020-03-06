from datetime import datetime
from hashlib import md5
from time import time
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login


class Agent(db.Model):
    __tablename__ = 'agent'

    id = db.Column(db.Integer, primary_key=True)
    agdetails = db.Column(db.String(180))
    agemail = db.Column(db.String(60))
    agnotes = db.Column(db.String(60))

    rent_agent = db.relationship('Rent', backref='agent', lazy='dynamic')


class Charge(db.Model):
    __tablename__ = 'charge'

    id = db.Column(db.Integer, primary_key=True)
    chargetype_id = db.Column(db.Integer, db.ForeignKey('chargetype.id'))
    chargestartdate = db.Column(db.Date)
    chargetotal = db.Column(db.Numeric(8,2))
    chargedetails = db.Column(db.String(140))
    chargebalance = db.Column(db.Numeric(8,2))
    rent_id = db.Column(db.Integer, db.ForeignKey('rent.id'))

    
class Chargetype(db.Model):
    __tablename__ = 'chargetype'

    id = db.Column(db.Integer, primary_key=True)
    chargedesc = db.Column(db.String(60))

    charge_chargetype = db.relationship('Charge', backref='chargetype', lazy='dynamic')


class Datef2(db.Model):
    __tablename__ = 'datef2'

    code = db.Column(db.String(10), primary_key=True)
    date1 = db.Column(db.Date)
    date2 = db.Column(db.Date)


class Datef4(db.Model):
    __tablename__ = 'datef4'

    code = db.Column(db.String(10), primary_key=True)
    date1 = db.Column(db.Date)
    date2 = db.Column(db.Date)
    date3 = db.Column(db.Date)
    date4 = db.Column(db.Date)


class Emailaccount(db.Model):
    __tablename__ = 'emailaccount'

    id = db.Column(db.Integer, primary_key=True)
    smtp_server = db.Column(db.String(60))
    smtp_port = db.Column(db.Integer)
    smtp_timeout = db.Column(db.Integer)
    smtp_debug = db.Column(db.Integer)
    smtp_tls = db.Column(db.Integer)
    smtp_user = db.Column(db.String(60))
    smtp_password = db.Column(db.String(60))
    smtp_sendfrom = db.Column(db.String(60))
    imap_server = db.Column(db.String(60))
    imap_port = db.Column(db.Integer)
    imap_tls = db.Column(db.Integer)
    imap_user = db.Column(db.String(60))
    imap_password = db.Column(db.String(60))
    imap_sentfolder = db.Column(db.String(60))
    imap_draftfolder = db.Column(db.String(60))

    landlord_emailacc = db.relationship('Landlord', backref='emailaccount', lazy='dynamic')


class Extmanager(db.Model):
    __tablename__ = 'extmanager'

    id = db.Column(db.Integer, primary_key=True)
    codename = db.Column(db.String(15))
    details = db.Column(db.String(180))

    extrent_extmanager = db.relationship('Extrent', backref='extmanager', lazy='dynamic')

    def __repr__(self):
        return '<Extmanager {}>'.format(self.codename)


class Extrent(db.Model):
    __tablename__ = 'extrent'

    id = db.Column(db.Integer, primary_key=True)
    rentcode = db.Column(db.String(20), index=True)
    tenantname = db.Column(db.String(30))
    propaddr = db.Column(db.String(180))
    agentdetails = db.Column(db.String(45))
    rentpa = db.Column(db.Numeric(8,2))
    arrears = db.Column(db.Numeric(8,2))
    lastrentdate = db.Column(db.Date)
    tenure = db.Column(db.String(1))
    owner = db.Column(db.String(15))
    source = db.Column(db.String(15))
    status = db.Column(db.String(1))
    extmanager_id = db.Column(db.Integer, db.ForeignKey('extmanager.id'))

    def __repr__(self):
        return '<Extrent {}>'.format(self.rentcode)
        
        
class Income(db.Model):
    __tablename__ = 'income'

    id = db.Column(db.Integer, primary_key=True)
    paydate = db.Column(db.Date)
    total = db.Column(db.Numeric(8,2))
    payer = db.Column(db.String(90))
    typebankacc_id = db.Column(db.Integer, db.ForeignKey('typebankacc.id'))
    typepayment_id = db.Column(db.Integer, db.ForeignKey('typepayment.id'))

    incomealloc_income = db.relationship('Incomealloc', backref='income', lazy='dynamic')


class Incomealloc(db.Model):
    __tablename__ = 'incomealloc'

    id = db.Column(db.Integer, primary_key=True)
    alloc_id = db.Column(db.Integer)
    rentcode = db.Column(db.String(15))
    total = db.Column(db.Numeric(8,2))
    chargetype_id = db.Column(db.Integer, db.ForeignKey('chargetype.id'))
    income_id = db.Column(db.Integer, db.ForeignKey('income.id'))
    landlord_id = db.Column(db.Integer, db.ForeignKey('landlord.id'))

    
class Landlord(db.Model):
    __tablename__ = 'landlord'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(90))
    addr = db.Column(db.String(180))
    taxdate = db.Column(db.Date)
    manager_id = db.Column(db.Integer, db.ForeignKey('manager.id'))
    bankacc_id = db.Column(db.Integer, db.ForeignKey('typebankacc.id'))
    emailacc_id = db.Column(db.Integer, db.ForeignKey('emailaccount.id'))

    rent_landlord = db.relationship('Rent', backref='landlord', lazy='dynamic')
    incomealloc_landlord = db.relationship('Incomealloc', backref='landlord', lazy='dynamic')

    def __repr__(self):
        return '<Landlord {}>'.format(self.name)


class Loan(db.Model):
    __tablename__ = 'loan'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30))
    start_intrate = db.Column(db.Numeric(8,2))
    end_date = db.Column(db.Date)
    frequency = db.Column(db.Integer, db.ForeignKey('typefreq.id'))
    advarr_id = db.Column(db.Integer, db.ForeignKey('typeadvarr.id'))
    lender = db.Column(db.String(45))
    borrower = db.Column(db.String(45))
    notes = db.Column(db.String(45))
    val_date = db.Column(db.Date)
    valuation = db.Column(db.Numeric(8,2))

    loan_trans_loan = db.relationship('Loan_trans', backref='loan', lazy='dynamic')
    loan_uplift_loan = db.relationship('Loan_uplift', backref='loan', lazy='dynamic')


class Loan_trans(db.Model):
    __tablename__ = 'loan_trans'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    amount = db.Column(db.Numeric(8,2))
    memo = db.Column(db.String(60))
    loan_id = db.Column(db.Integer, db.ForeignKey('loan.id'))

    
class Loan_uplift(db.Model):
    __tablename__ = 'loan_uplift'

    id = db.Column(db.Integer, primary_key=True)
    intrate = db.Column(db.Numeric(8, 2))
    datestarts = db.Column(db.Date)
    loan_id = db.Column(db.Integer, db.ForeignKey('loan.id'))


class Manager(db.Model):
    __tablename__ = 'manager'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(90))
    addr1 = db.Column(db.String(180))
    addr2 = db.Column(db.String(180))

    landlord_manager = db.relationship('Landlord', backref='manager', lazy='dynamic')

    def __repr__(self):
        return '<Manager {}>'.format(self.name)

        
class Property(db.Model):
    __tablename__ = 'property'

    id = db.Column(db.Integer, primary_key=True)
    propaddr = db.Column(db.String(180))
    rent_id = db.Column(db.Integer, db.ForeignKey('rent.id'))
    typeprop_id = db.Column(db.Integer, db.ForeignKey('typeproperty.id'))

    def __repr__(self):
        return '<Property {}>'.format(self.propaddr)


class Rent(db.Model):
    __tablename__ = 'rent'

    id = db.Column(db.Integer, primary_key=True)
    rentcode = db.Column(db.String(15), index=True, unique=True)
    tenantname = db.Column(db.String(90))
    rentpa = db.Column(db.Numeric(8,2))
    arrears = db.Column(db.Numeric(8,2))
    lastrentdate = db.Column(db.Date)
    datecode = db.Column(db.String(10))
    source = db.Column(db.String(20))
    price = db.Column(db.Numeric(8,2))
    email = db.Column(db.String(60))
    note = db.Column(db.String(120))
    landlord_id = db.Column(db.Integer, db.ForeignKey('landlord.id'))
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'))
    actype_id = db.Column(db.Integer, db.ForeignKey('typeactype.id'))
    advarr_id = db.Column(db.Integer, db.ForeignKey('typeadvarr.id'))
    deed_id = db.Column(db.Integer, db.ForeignKey('typedeed.id'))
    freq_id = db.Column(db.Integer, db.ForeignKey('typefreq.id'))
    mailto_id = db.Column(db.Integer, db.ForeignKey('typemailto.id'))
    salegrade_id = db.Column(db.Integer, db.ForeignKey('typesalegrade.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('typestatus.id'))
    tenure_id = db.Column(db.Integer, db.ForeignKey('typetenure.id'))

    prop_rent = db.relationship('Property', backref='rent', lazy='dynamic')
    charge_rent = db.relationship('Charge', backref='rent', lazy='dynamic')

    def __repr__(self):
        return '<Rent {}>'.format(self.rentcode)

    # @classmethod
    # def totcharges(self):
    #     return sum of charges for this rent - is this possible?


class Rental(db.Model):
    __tablename__ = 'rental'

    id = db.Column(db.Integer, primary_key=True)
    rentalcode = db.Column(db.String(15), index=True, unique=True)
    propaddr = db.Column(db.String(120))
    tenantname = db.Column(db.String(90))
    rentpa = db.Column(db.Numeric(8,2))
    arrears = db.Column(db.Numeric(8,2))
    lastrentdate = db.Column(db.Date)
    note = db.Column(db.String(90))
    freq_id = db.Column(db.Integer, db.ForeignKey('typefreq.id'))
    advarr_id = db.Column(db.Integer, db.ForeignKey('typeadvarr.id'))

    rental_trans_rental = db.relationship('Rental_trans', backref='rental', lazy='dynamic')


class Rental_trans(db.Model):
    __tablename__ = 'rental_trans'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    amount = db.Column(db.Numeric(8, 2))
    payer = db.Column(db.String(60))
    memo = db.Column(db.String(60))
    rental_id = db.Column(db.Integer, db.ForeignKey('rental.id'))


class Typeactype(db.Model):
    __tablename__ = 'typeactype'

    id = db.Column(db.Integer, primary_key=True)
    actypedet = db.Column(db.String(45))

    rent_typeactype = db.relationship('Rent', backref='typeactype', lazy='dynamic')


class Typeadvarr(db.Model):
    __tablename__ = 'typeadvarr'

    id = db.Column(db.Integer, primary_key=True)
    advarrdet = db.Column(db.String(45))

    rent_typeadvarr = db.relationship('Rent', backref='typeadvarr', lazy='dynamic')
    loan_typeadvarr = db.relationship('Loan', backref='typeadvarr', lazy='dynamic')
    rental_typeadvarr = db.relationship('Rental', backref='typeadvarr', lazy='dynamic')


class Typebankacc(db.Model):
    __tablename__ = 'typebankacc'

    id = db.Column(db.Integer, primary_key=True)
    bankname = db.Column(db.String(45))
    accname = db.Column(db.String(60))
    sortcode = db.Column(db.String(10))
    accnum = db.Column(db.String(15))
    accdesc = db.Column(db.String(30))

    income_typebankacc = db.relationship('Income', backref='typebankacc', lazy='dynamic')
    landlord_typebankacc = db.relationship('Landlord', backref='typebankacc', lazy='dynamic')


class Typedeed(db.Model):
    __tablename__ = 'typedeed'

    id = db.Column(db.Integer, primary_key=True)
    deedcode = db.Column(db.String(15))
    nfee = db.Column(db.Numeric(8,2))
    nfeeindeed = db.Column(db.String(45))
    interest = db.Column(db.Numeric(8,2))
    dcov = db.Column(db.Boolean, default=False)
    licencetoassign = db.Column(db.Boolean, default=False)
    insapprove = db.Column(db.Boolean, default=False)
    insproduce = db.Column(db.Boolean, default=False)
    alterations = db.Column(db.Boolean, default=False)
    dwellingonly = db.Column(db.Boolean, default=False)
    sublet = db.Column(db.Boolean, default=False)
    info = db.Column(db.String(180))

    rent_typedeed = db.relationship('Rent', backref='typedeed', lazy='dynamic')


class Typefreq(db.Model):
    __tablename__ = 'typefreq'

    id = db.Column(db.Integer, primary_key=True)
    freqdet = db.Column(db.String(45))

    rent_typefreq = db.relationship('Rent', backref='typefreq', lazy='dynamic')
    loan_typefreq = db.relationship('Loan', backref='typefreq', lazy='dynamic')
    rental_typefreq = db.relationship('Rental', backref='typefreq', lazy='dynamic')

    
class Typemailto(db.Model):
    __tablename__ = 'typemailto'

    id = db.Column(db.Integer, primary_key=True)
    mailtodet = db.Column(db.String(45))

    rent_typemailto = db.relationship('Rent', backref='typemailto', lazy='dynamic')


class Typepayment(db.Model):
    __tablename__ = 'typepayment'

    id = db.Column(db.Integer, primary_key=True)
    paytypedet = db.Column(db.String(45))

    income_typepayment = db.relationship('Income', backref='typepayment', lazy='dynamic')


class Typeproperty(db.Model):
    __tablename__ = 'typeproperty'

    id = db.Column(db.Integer, primary_key=True)
    proptypedet = db.Column(db.String(45))

    property_typeproperty = db.relationship('Property', backref='typeproperty', lazy='dynamic')


class Typesalegrade(db.Model):
    __tablename__ = 'typesalegrade'

    id = db.Column(db.Integer, primary_key=True)
    salegradedet = db.Column(db.String(45))

    rent_typesalegrade = db.relationship('Rent', backref='typesalegrade', lazy='dynamic')


class Typestatus(db.Model):
    __tablename__ = 'typestatus'

    id = db.Column(db.Integer, primary_key=True)
    statusdet = db.Column(db.String(45))

    rent_typestatus = db.relationship('Rent', backref='typestatus', lazy='dynamic')


class Typetenure(db.Model):
    __tablename__ = 'typetenure'

    id = db.Column(db.Integer, primary_key=True)
    tenuredet = db.Column(db.String(15))

    rent_typetenure = db.relationship('Rent', backref='typetenure', lazy='dynamic')

                
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
