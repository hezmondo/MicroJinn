from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
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
    code = db.Column(db.String(15))

    emailad_agent = db.relationship('Emailad', backref='agent', lazy='dynamic')
    headrent_agent = db.relationship('Headrent', backref='agent', lazy='dynamic')
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
    incomealloc_chargetype = db.relationship('Incomealloc', backref='chargetype', lazy='dynamic')


class Dates(db.Model):
    __tablename__ = 'dates'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(15))
    month = db.Column(db.Integer)
    day = db.Column(db.Integer)


class Digfile(db.Model):
    __tablename__ = 'digfile'

    id = db.Column(db.Integer, primary_key=True)
    dig_date = db.Column(db.Date)
    summary = db.Column(db.String(90))
    dig_data = db.Column(db.LargeBinary, nullable=True)
    doctype_id = db.Column(db.Integer, db.ForeignKey('typedoc.id'))
    rent_id = db.Column(db.Integer, db.ForeignKey('rent.id'))
    out_in = db.Column(db.Integer, nullable=False)


class Docfile(db.Model):
    __tablename__ = 'docfile'

    id = db.Column(db.Integer, primary_key=True)
    doc_date = db.Column(db.Date)
    summary = db.Column(db.String(90))
    doc_text = db.Column(db.Text)
    doctype_id = db.Column(db.Integer, db.ForeignKey('typedoc.id'))
    rent_id = db.Column(db.Integer, db.ForeignKey('rent.id'))
    out_in = db.Column(db.Integer, nullable=False)


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


class Emailad(db.Model):
    __tablename__ = 'emailad'

    id = db.Column(db.Integer, primary_key=True)
    emailaddr = db.Column(db.String(90))
    rent_id = db.Column(db.Integer, db.ForeignKey('rent.id'))
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'))


class Event(db.Model):
    __tablename__ = 'event'

    id = db.Column(db.Integer, primary_key=True)
    event_date = db.Column(db.Date)
    summary = db.Column(db.String(90))
    rent_id = db.Column(db.Integer, db.ForeignKey('rent.id'))
    eventtype_id = db.Column(db.Integer, db.ForeignKey('typeevent.id'))


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
        
        
class Formletter(db.Model):
    __tablename__ = 'formletter'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30))
    summary = db.Column(db.String(60))
    subject = db.Column(db.String(150))
    block = db.Column(db.Text, nullable=True)
    bold = db.Column(db.String(900))
    doctype_id = db.Column(db.Integer, db.ForeignKey('typedoc.id'))
    template_id = db.Column(db.Integer, db.ForeignKey('template.id'))


class Headrent(db.Model):
    __tablename__ = 'headrent'

    id = db.Column(db.Integer, primary_key=True)
    hrcode = db.Column(db.String(15), index=True, unique=True)
    rentpa = db.Column(db.Numeric(8,2))
    arrears = db.Column(db.Numeric(8,2))
    lastrentdate = db.Column(db.Date)
    datecode = db.Column(db.String(10))
    source = db.Column(db.String(20))
    reference = db.Column(db.String(60))
    propaddr = db.Column(db.String(180))
    note = db.Column(db.String(120))
    landlord_id = db.Column(db.Integer, db.ForeignKey('landlord.id'))
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'))
    advarr_id = db.Column(db.Integer, db.ForeignKey('typeadvarr.id'))
    freq_id = db.Column(db.Integer, db.ForeignKey('typefreq.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('typestatus.id'))
    tenure_id = db.Column(db.Integer, db.ForeignKey('typetenure.id'))


class Income(db.Model):
    __tablename__ = 'income'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    payer = db.Column(db.String(90))
    amount = db.Column(db.Numeric(8,2))
    paytype_id = db.Column(db.Integer, db.ForeignKey('typepayment.id'))
    bankacc_id = db.Column(db.Integer, db.ForeignKey('money_account.id'))

    incomealloc_income = db.relationship('Incomealloc', backref='income', lazy='dynamic')


class Incomealloc(db.Model):
    __tablename__ = 'incomealloc'

    id = db.Column(db.Integer, primary_key=True)
    rentcode = db.Column(db.String(15))
    amount = db.Column(db.Numeric(8,2))
    chargetype_id = db.Column(db.Integer, db.ForeignKey('chargetype.id'))
    income_id = db.Column(db.Integer, db.ForeignKey('income.id'))
    landlord_id = db.Column(db.Integer)
    rent_id = db.Column(db.Integer, db.ForeignKey('rent.id'))

    
class Jstore(db.Model):
    __tablename__ = 'jstore'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    content = db.Column(db.String(900))


class Landlord(db.Model):
    __tablename__ = 'landlord'

    id = db.Column(db.Integer, primary_key=True)
    landlordname = db.Column(db.String(90))
    landlordaddr = db.Column(db.String(180))
    taxdate = db.Column(db.Date)
    manager_id = db.Column(db.Integer, db.ForeignKey('manager.id'))
    bankacc_id = db.Column(db.Integer, db.ForeignKey('money_account.id'))
    emailacc_id = db.Column(db.Integer, db.ForeignKey('emailaccount.id'))

    rent_landlord = db.relationship('Rent', backref='landlord', lazy='dynamic')
    headrent_landlord = db.relationship('Headrent', backref='landlord', lazy='dynamic')

    def __repr__(self):
        return '<Landlord {}>'.format(self.name)


class Lease(db.Model):
    __tablename__ = 'lease'

    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.Integer)
    startdate = db.Column(db.Date)
    startrent = db.Column(db.Numeric(8, 2))
    info = db.Column(db.String(180))
    upliftdate = db.Column(db.Date)
    impvaluek = db.Column(db.Numeric(10, 2))
    uplift_type_id = db.Column(db.Integer, db.ForeignKey('lease_uplift_type.id'))
    rentcap = db.Column(db.Numeric(8, 2))
    lastvalue = db.Column(db.Numeric(8, 2))
    last_value_date = db.Column(db.Date)
    rent_id = db.Column(db.Integer, db.ForeignKey('rent.id'))


class Lease_extension(db.Model):
    __tablename__ = 'lease_extension'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(15))
    date = db.Column(db.Date)
    value = db.Column(db.Integer)


class Lease_relativity(db.Model):
    __tablename__ = 'lease_relativity'

    id = db.Column(db.Integer, primary_key=True)
    unexpired = db.Column(db.Integer)
    relativity = db.Column(db.Numeric(8, 2))


class Lease_uplift_type(db.Model):
    __tablename__ = 'lease_uplift_type'

    id = db.Column(db.Integer, primary_key=True)
    uplift_type = db.Column(db.String(15))
    years = db.Column(db.Integer)
    method = db.Column(db.String(15))
    uplift_value = db.Column(db.Numeric(8, 2))

    lease_uplift_type = db.relationship('Lease', backref='Lease_uplift_type', lazy='dynamic')


class Loan(db.Model):
    __tablename__ = 'loan'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30))
    interest_rate = db.Column(db.Numeric(8,2))
    end_date = db.Column(db.Date)
    frequency = db.Column(db.Integer, db.ForeignKey('typefreq.id'))
    advarr_id = db.Column(db.Integer, db.ForeignKey('typeadvarr.id'))
    lender = db.Column(db.String(45))
    borrower = db.Column(db.String(45))
    notes = db.Column(db.String(45))
    val_date = db.Column(db.Date)
    valuation = db.Column(db.Numeric(8,2))
    interestpa = db.Column(db.Numeric(8,2))

    loan_trans_loan = db.relationship('Loan_trans', backref='loan', lazy='dynamic')
    loan_interest_rate_loan = db.relationship('Loan_interest_rate', backref='loan', lazy='dynamic')


class Loan_interest_rate(db.Model):
    __tablename__ = 'loan_interest_rate'

    id = db.Column(db.Integer, primary_key=True)
    intrate = db.Column(db.Numeric(8, 2))
    datestarts = db.Column(db.Date)
    loan_id = db.Column(db.Integer, db.ForeignKey('loan.id'))


class Loan_statement(db.Model):
    __tablename__ = 'loan_statement'

    id = db.Column(db.Integer, primary_key=True)
    ltid = db.Column(db.Integer)
    date = db.Column(db.Date)
    memo = db.Column(db.String(60))
    transaction = db.Column(db.Numeric(8, 2))
    rate = db.Column(db.Numeric(8, 2))
    interest = db.Column(db.Numeric(8, 2))
    add_interest = db.Column(db.String(10))
    balance = db.Column(db.Numeric(8, 2))


class Loan_trans(db.Model):
    __tablename__ = 'loan_trans'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    amount = db.Column(db.Numeric(8, 2))
    memo = db.Column(db.String(60))
    loan_id = db.Column(db.Integer, db.ForeignKey('loan.id'))


class Manager(db.Model):
    __tablename__ = 'manager'

    id = db.Column(db.Integer, primary_key=True)
    managername = db.Column(db.String(90))
    manageraddr = db.Column(db.String(180))
    manageraddr2 = db.Column(db.String(180))

    landlord_manager = db.relationship('Landlord', backref='manager', lazy='dynamic')

    def __repr__(self):
        return '<Manager {}>'.format(self.name)

        
class Money_account(db.Model):
    __tablename__ = 'money_account'

    id = db.Column(db.Integer, primary_key=True)
    bankname = db.Column(db.String(45))
    accname = db.Column(db.String(60))
    sortcode = db.Column(db.String(10))
    accnum = db.Column(db.String(15))
    accdesc = db.Column(db.String(30))

    income_moneyaccount = db.relationship('Income', backref='money_account', lazy='dynamic')
    moneyitem_moneyaccount = db.relationship('Money_item', backref='money_account', lazy='dynamic')
    landlord_moneyaccount = db.relationship('Landlord', backref='money_account', lazy='dynamic')


class Money_category(db.Model):
    __tablename__ = 'money_category'

    id = db.Column(db.Integer, primary_key=True)
    cat_name = db.Column(db.String(60))

    moneyitem_moneycategory = db.relationship('Money_item', backref='money_category', lazy='dynamic')


class Money_item(db.Model):
    __tablename__ = 'money_item'

    id = db.Column(db.Integer, primary_key=True)
    num = db.Column(db.Integer)
    date = db.Column(db.Date)
    payer = db.Column(db.String(60))
    amount = db.Column(db.Numeric(8, 2))
    memo = db.Column(db.String(90))
    cat_id = db.Column(db.Integer, db.ForeignKey('money_category.id'))
    cleared = db.Column(db.Integer)
    bankacc_id = db.Column(db.Integer, db.ForeignKey('money_account.id'))


class Property(db.Model):
    __tablename__ = 'property'

    id = db.Column(db.Integer, primary_key=True)
    propaddr = db.Column(db.String(180))
    rent_id = db.Column(db.Integer, db.ForeignKey('rent.id'))
    typeprop_id = db.Column(db.Integer, db.ForeignKey('typeproperty.id'))

    def __repr__(self):
        return '<Property {}>'.format(self.propaddr)


class Recent(db.Model):
    __tablename__ = 'recent'

    id = db.Column(db.Integer, primary_key=True)
    rent_id = db.Column(db.Integer)
    agent_id = db.Column(db.Integer)
    number = db.Column(db.Integer)


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
    prdelivery_id = db.Column(db.Integer, db.ForeignKey('typeprdelivery.id'))
    salegrade_id = db.Column(db.Integer, db.ForeignKey('typesalegrade.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('typestatus.id'))
    tenure_id = db.Column(db.Integer, db.ForeignKey('typetenure.id'))

    charge_rent = db.relationship('Charge', backref='rent', lazy='dynamic')
    digfile_rent = db.relationship('Digfile', backref='rent', lazy='dynamic')
    docfile_rent = db.relationship('Docfile', backref='rent', lazy='dynamic')
    emailad_rent = db.relationship('Emailad', backref='rent', lazy='dynamic')
    event_rent = db.relationship('Event', backref='rent', lazy='dynamic')
    incomealloc_rent = db.relationship('Incomealloc', backref='rent', lazy='dynamic')
    lease_rent = db.relationship('Lease', backref='rent', lazy='dynamic')
    prop_rent = db.relationship('Property', backref='rent', lazy='dynamic')

    def __repr__(self):
        return '<Rent {}>'.format(self.rentcode)


class Rental(db.Model):
    __tablename__ = 'rental'

    id = db.Column(db.Integer, primary_key=True)
    rentalcode = db.Column(db.String(15), index=True, unique=True)
    propaddr = db.Column(db.String(120))
    tenantname = db.Column(db.String(90))
    rentpa = db.Column(db.Numeric(8,2))
    arrears = db.Column(db.Numeric(8,2))
    startrentdate = db.Column(db.Date)
    note = db.Column(db.String(90))
    freq_id = db.Column(db.Integer, db.ForeignKey('typefreq.id'))
    advarr_id = db.Column(db.Integer, db.ForeignKey('typeadvarr.id'))
    astdate = db.Column(db.Date)
    lastgastest = db.Column(db.Date)


class Rental_statement(db.Model):
    __tablename__ = 'rental_statement'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    memo = db.Column(db.String(60))
    amount = db.Column(db.Numeric(8, 2))
    payer = db.Column(db.String(60))
    balance = db.Column(db.Numeric(8, 2))


class Template(db.Model):
    __tablename__ = 'template'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(15))
    desc = db.Column(db.String(60))

    formletter_template = db.relationship('Formletter', backref='template', lazy='dynamic')


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
    headrent_typeadvarr = db.relationship('Headrent', backref='typeadvarr', lazy='dynamic')
    loan_typeadvarr = db.relationship('Loan', backref='typeadvarr', lazy='dynamic')
    rental_typeadvarr = db.relationship('Rental', backref='typeadvarr', lazy='dynamic')


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


class Typedoc(db.Model):
    __tablename__ = 'typedoc'

    id = db.Column(db.Integer, primary_key=True)
    desc = db.Column(db.String(30))

    formletter_typedoc = db.relationship('Formletter', backref='typedoc', lazy='dynamic')
    digfile_typedoc = db.relationship('Digfile', backref='typedoc', lazy='dynamic')
    docfile_typedoc = db.relationship('Docfile', backref='typedoc', lazy='dynamic')


class Typeevent(db.Model):
    __tablename__ = 'typeevent'

    id = db.Column(db.Integer, primary_key=True)
    desc = db.Column(db.String(30))

    event_typedoc = db.relationship('Event', backref='typeevent', lazy='dynamic')


class Typefreq(db.Model):
    __tablename__ = 'typefreq'

    id = db.Column(db.Integer, primary_key=True)
    freqdet = db.Column(db.String(45))

    rent_typefreq = db.relationship('Rent', backref='typefreq', lazy='dynamic')
    headrent_typefreq = db.relationship('Headrent', backref='typefreq', lazy='dynamic')
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

    income_paytype = db.relationship('Income', backref='typepayment', lazy='dynamic')


class Typeprdelivery(db.Model):
    __tablename__ = 'typeprdelivery'

    id = db.Column(db.Integer, primary_key=True)
    prdeliverydet = db.Column(db.String(45))

    rent_typeprdelivery = db.relationship('Rent', backref='typeprdelivery', lazy='dynamic')


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
    headrent_typestatus = db.relationship('Headrent', backref='typestatus', lazy='dynamic')


class Typetenure(db.Model):
    __tablename__ = 'typetenure'

    id = db.Column(db.Integer, primary_key=True)
    tenuredet = db.Column(db.String(15))

    rent_typetenure = db.relationship('Rent', backref='typetenure', lazy='dynamic')
    headrent_typetenure = db.relationship('Headrent', backref='typetenure', lazy='dynamic')

                
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(90))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    recent_rents = db.Column(db.String(300))
    recent_agents = db.Column(db.String(300))

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
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
