from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app, json
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import app, db, login, cache


class Action(db.Model):
    __tablename__ = 'action'

    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime)
    actiontype_id = db.Column(db.Integer())
    detail = db.Column(db.String(180))
    link = db.Column(db.String(120))
    link_vars = db.Column(db.String(120))
    alert = db.Column(db.Boolean, nullable=True)


class Agent(db.Model):
    __tablename__ = 'agent'

    id = db.Column(db.Integer, primary_key=True)
    detail = db.Column(db.String(180))
    email = db.Column(db.String(90))
    note = db.Column(db.String(90))
    code = db.Column(db.String(15))

    headrent_agent = db.relationship('Headrent', backref='agent', lazy='dynamic')
    rent_agent = db.relationship('Rent', backref='agent', lazy='dynamic')


class Case(db.Model):
    __tablename__ = 'case'

    id = db.Column(db.Integer, db.ForeignKey('rent.id'), primary_key=True)
    case_details = db.Column(db.String(180))
    case_nad = db.Column(db.Date)


class Charge(db.Model):
    __tablename__ = 'charge'

    id = db.Column(db.Integer, primary_key=True)
    chargetype_id = db.Column(db.Integer, db.ForeignKey('chargetype.id'))
    chargestartdate = db.Column(db.Date)
    chargetotal = db.Column(db.Numeric(8, 2))
    chargedetail = db.Column(db.String(140))
    chargebalance = db.Column(db.Numeric(8, 2))
    rent_id = db.Column(db.Integer, db.ForeignKey('rent.id'))

    pr_charge = db.relationship('PrCharge', backref='charge', lazy='dynamic')


class ChargeType(db.Model):
    __tablename__ = 'chargetype'

    id = db.Column(db.Integer, primary_key=True)
    chargedesc = db.Column(db.String(60))

    charge_chargetype = db.relationship('Charge', backref='chargetype', lazy='dynamic')
    incomealloc_chargetype = db.relationship('IncomeAlloc', backref='chargetype', lazy='dynamic')

    @staticmethod
    @cache.cached(key_prefix='db_chargetype_chargedesc_all')
    def chargetypes():
        charge_types = [value for (value,) in ChargeType.query.with_entities(ChargeType.chargedesc).all()]
        return charge_types


class DigFile(db.Model):
    __tablename__ = 'digfile'

    id = db.Column(db.Integer, primary_key=True)
    doc_date = db.Column(db.Date)
    summary = db.Column(db.String(90))
    dig_data = db.Column(db.LargeBinary, nullable=True)
    doctype_id = db.Column(db.Integer, db.ForeignKey('typedoc.id'))
    rent_id = db.Column(db.Integer, db.ForeignKey('rent.id'))
    out_in = db.Column(db.SmallInteger, nullable=False)


class DocFile(db.Model):
    __tablename__ = 'docfile'

    id = db.Column(db.Integer, primary_key=True)
    doc_date = db.Column(db.Date)
    summary = db.Column(db.String(90))
    doc_text = db.Column(db.Text)
    doctype_id = db.Column(db.Integer, db.ForeignKey('typedoc.id'))
    rent_id = db.Column(db.Integer, db.ForeignKey('rent.id'))
    out_in = db.Column(db.SmallInteger, nullable=False)

    pr_history_docfile = db.relationship('PrHistory', backref='pr_history', lazy='dynamic')


class EmailAcc(db.Model):
    __tablename__ = 'email_acc'

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

    landlord_emailacc = db.relationship('Landlord', backref='email_acc', lazy='dynamic')


class EmailAddr(db.Model):
    __tablename__ = 'emailad'

    id = db.Column(db.Integer, primary_key=True)
    emailaddr = db.Column(db.String(90))


class Event(db.Model):
    __tablename__ = 'event'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    description = db.Column(db.String(90))
    rent_id = db.Column(db.Integer, db.ForeignKey('rent.id'))
    event_type_id = db.Column(db.Integer)


class FormLetter(db.Model):
    __tablename__ = 'form_letter'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30))
    description = db.Column(db.String(90))
    subject = db.Column(db.String(150))
    block = db.Column(db.Text, nullable=True)
    doctype_id = db.Column(db.Integer, db.ForeignKey('typedoc.id'))
    template = db.Column(db.String(30))


class Headrent(db.Model):
    __tablename__ = 'headrent'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(15), index=True, unique=True)
    rentpa = db.Column(db.Numeric(8, 2))
    advarr_id = db.Column(db.Integer)
    arrears = db.Column(db.Numeric(8, 2))
    lastrentdate = db.Column(db.Date)
    datecode_id = db.Column(db.Integer, default=0)
    source = db.Column(db.String(20))
    reference = db.Column(db.String(60))
    propaddr = db.Column(db.String(180))
    note = db.Column(db.String(120))
    landlord_id = db.Column(db.Integer, db.ForeignKey('landlord.id'))
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'))
    freq_id = db.Column(db.Integer)
    status_id = db.Column(db.Integer)
    tenure_id = db.Column(db.Integer)

    # @hybrid_property
    # def get_next_rent_date(self):
    #     from app.main.common import inc_date_m
    #     return inc_date_m(self.lastrentdate, self.freq_id, self.datecode_id, 1)
    #
    # Sam: I haven't been about to get the expression below to work to filter headrents by next_rent_date
    # @get_next_rent_date.expression
    # def get_next_rent_date(cls):
    #     from sqlalchemy import func
    #     return func.mjinn.next_rent_date(cls.id, 2)


class Income(db.Model):
    __tablename__ = 'income'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    payer = db.Column(db.String(90))
    amount = db.Column(db.Numeric(8, 2))
    paytype_id = db.Column(db.Integer)
    acc_id = db.Column(db.Integer, db.ForeignKey('money_account.id'))

    incomealloc_income = db.relationship('IncomeAlloc', backref='income', lazy='dynamic')


class IncomeAlloc(db.Model):
    __tablename__ = 'incomealloc'

    id = db.Column(db.Integer, primary_key=True)
    rentcode = db.Column(db.String(15))
    amount = db.Column(db.Numeric(8, 2))
    chargetype_id = db.Column(db.Integer, db.ForeignKey('chargetype.id'))
    income_id = db.Column(db.Integer, db.ForeignKey('income.id'))
    landlord_id = db.Column(db.Integer)
    rent_id = db.Column(db.Integer, db.ForeignKey('rent.id'))


class Jstore(db.Model):
    __tablename__ = 'jstore'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer)
    code = db.Column(db.String(30))
    description = db.Column(db.String(90), nullable=True)
    content = db.Column(db.Text)
    last_used = db.Column(db.DateTime)


class Landlord(db.Model):
    __tablename__ = 'landlord'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(90))
    address = db.Column(db.String(180))
    tax_date = db.Column(db.Date)
    manager_id = db.Column(db.Integer, db.ForeignKey('manager.id'))
    acc_id = db.Column(db.Integer, db.ForeignKey('money_account.id'))
    email_acc_id = db.Column(db.Integer, db.ForeignKey('email_acc.id'))

    rent_landlord = db.relationship('Rent', backref='landlord', lazy='dynamic')
    headrent_landlord = db.relationship('Headrent', backref='landlord', lazy='dynamic')

    def __repr__(self):
        return '<Landlord {}>'.format(self.name)

    @staticmethod
    @cache.cached(key_prefix='db_landlord_names_all')
    def names():
        landlord_names = [value for (value,) in Landlord.query.with_entities(Landlord.name).all()]
        return landlord_names


class Lease(db.Model):
    __tablename__ = 'lease'

    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.Integer)
    start_date = db.Column(db.Date)
    start_rent = db.Column(db.Numeric(8, 2))
    info = db.Column(db.String(180))
    uplift_date = db.Column(db.Date)
    sale_value_k = db.Column(db.Numeric(10, 2))
    uplift_type_id = db.Column(db.Integer, db.ForeignKey('lease_uplift_type.id'))
    rent_cap = db.Column(db.Numeric(8, 2))
    value = db.Column(db.Numeric(8, 2))
    value_date = db.Column(db.Date)
    rent_id = db.Column(db.Integer, db.ForeignKey('rent.id'))


class LeaseExt(db.Model):
    __tablename__ = 'lease_extension'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(15))
    date = db.Column(db.Date)
    value = db.Column(db.Integer)


class LeaseRel(db.Model):
    __tablename__ = 'lease_relativity'

    id = db.Column(db.Integer, primary_key=True)
    unexpired = db.Column(db.Integer)
    relativity = db.Column(db.Numeric(8, 2))


class LeaseUpType(db.Model):
    __tablename__ = 'lease_uplift_type'

    id = db.Column(db.Integer, primary_key=True)
    uplift_type = db.Column(db.String(15))
    years = db.Column(db.Integer)
    method = db.Column(db.String(15))
    uplift_value = db.Column(db.Numeric(8, 2))

    lease_uplift_type = db.relationship('Lease', backref='LeaseUpType', lazy='dynamic')


class Loan(db.Model):
    __tablename__ = 'loan'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30))
    interest_rate = db.Column(db.Numeric(8, 2))
    end_date = db.Column(db.Date)
    freq_id = db.Column(db.Integer)
    lender = db.Column(db.String(45))
    borrower = db.Column(db.String(45))
    notes = db.Column(db.String(45))
    val_date = db.Column(db.Date)
    valuation = db.Column(db.Numeric(8, 2))
    interestpa = db.Column(db.Numeric(8, 2))

    loan_trans_loan = db.relationship('LoanTran', backref='loan', lazy='dynamic')
    loan_interest_rate_loan = db.relationship('LoanIntRate', backref='loan', lazy='dynamic')


class LoanIntRate(db.Model):
    __tablename__ = 'loan_interest_rate'

    id = db.Column(db.Integer, primary_key=True)
    rate = db.Column(db.Numeric(8, 2))
    start_date = db.Column(db.Date)
    loan_id = db.Column(db.Integer, db.ForeignKey('loan.id'))


class LoanStat(db.Model):
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


class LoanTran(db.Model):
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


class ManagerExt(db.Model):
    __tablename__ = 'manager_external'

    id = db.Column(db.Integer, primary_key=True)
    codename = db.Column(db.String(15))
    detail = db.Column(db.String(180))

    rentext_managerext = db.relationship('RentExternal', backref='manager_external', lazy='dynamic')


class MoneyAcc(db.Model):
    __tablename__ = 'money_account'

    id = db.Column(db.Integer, primary_key=True)
    bank_name = db.Column(db.String(45))
    acc_name = db.Column(db.String(60))
    sort_code = db.Column(db.String(10))
    acc_num = db.Column(db.String(15))
    acc_desc = db.Column(db.String(30))

    income_moneyaccount = db.relationship('Income', backref='money_account', lazy='dynamic')
    money_item_moneyaccount = db.relationship('MoneyItem', backref='money_account', lazy='dynamic')
    landlord_moneyaccount = db.relationship('Landlord', backref='money_account', lazy='dynamic')


class MoneyCat(db.Model):
    __tablename__ = 'money_category'

    id = db.Column(db.Integer, primary_key=True)
    cat_name = db.Column(db.String(60))

    money_item_moneycategory = db.relationship('MoneyItem', backref='money_category', lazy='dynamic')


class MoneyItem(db.Model):
    __tablename__ = 'money_item'

    id = db.Column(db.Integer, primary_key=True)
    num = db.Column(db.Integer)
    date = db.Column(db.Date)
    payer = db.Column(db.String(60))
    amount = db.Column(db.Numeric(8, 2))
    memo = db.Column(db.String(90))
    cat_id = db.Column(db.Integer, db.ForeignKey('money_category.id'))
    cleared = db.Column(db.Integer)
    acc_id = db.Column(db.Integer, db.ForeignKey('money_account.id'))


class PrArrearsMatrix(db.Model):
    __tablename__ = 'pr_arrears_matrix'

    id = db.Column(db.Integer, primary_key=True)
    suffix = db.Column(db.String(30), nullable=True)
    description = db.Column(db.String(150), nullable=True)
    recovery_charge = db.Column(db.Numeric(8, 2))
    create_case = db.Column(db.Boolean, nullable=True)
    arrears_clause = db.Column(db.Text, nullable=True)
    force_mail = db.Column(db.Boolean, nullable=True)


class PrBatch(db.Model):
    __tablename__ = 'pr_batch'

    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime)
    code = db.Column(db.String(30))
    size = db.Column(db.Integer)
    status = db.Column(db.String(30))
    is_account = db.Column(db.Boolean)

    payrequests = db.relationship('PrHistory', backref='batch', lazy='dynamic')


class PrCharge(db.Model):
    __tablename__ = 'pr_charge'

    id = db.Column(db.Integer, db.ForeignKey('pr_history.id'), primary_key=True)
    charge_id = db.Column(db.Integer, db.ForeignKey('charge.id'))
    case_created = db.Column(db.Boolean)


class PrHistory(db.Model):
    __tablename__ = 'pr_history'

    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime)
    summary = db.Column(db.String(90))
    block = db.Column(db.Text)
    rent_id = db.Column(db.Integer, db.ForeignKey('rent.id'))
    batch_id = db.Column(db.Integer, db.ForeignKey('pr_batch.id'))
    rent_date = db.Column(db.Date)
    total_due = db.Column(db.Numeric(8, 2))
    arrears_level = db.Column(db.String(1))
    delivery_method = db.Column(db.Integer)
    delivered = db.Column(db.Boolean)
    docfile_id = db.Column(db.Integer, db.ForeignKey('docfile.id'))

    pr_charge_pr_history = db.relationship('PrCharge', backref='pr_history', lazy='dynamic')


class Property(db.Model):
    __tablename__ = 'property'

    id = db.Column(db.Integer, primary_key=True)
    propaddr = db.Column(db.String(180))
    rent_id = db.Column(db.Integer, db.ForeignKey('rent.id'))
    proptype_id = db.Column(db.Integer)


class Recent(db.Model):
    __tablename__ = 'recent'

    id = db.Column(db.Integer, primary_key=True)
    rent_id = db.Column(db.Integer)
    agent_id = db.Column(db.Integer)
    number = db.Column(db.Integer)


class RecentSearch(db.Model):
    __tablename__ = 'recent_search'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(45))
    desc = db.Column(db.String(90))
    dict = db.Column(db.Text)


class Rent(db.Model):
    __tablename__ = 'rent'

    id = db.Column(db.Integer, primary_key=True)
    rentcode = db.Column(db.String(15), index=True, unique=True)
    tenantname = db.Column(db.String(90))
    rentpa = db.Column(db.Numeric(8, 2))
    arrears = db.Column(db.Numeric(8, 2))
    lastrentdate = db.Column(db.Date)
    datecode_id = db.Column(db.Integer, default=0)
    source = db.Column(db.String(20))
    price = db.Column(db.Numeric(8, 2))
    email = db.Column(db.String(60))
    note = db.Column(db.String(120))
    landlord_id = db.Column(db.Integer, db.ForeignKey('landlord.id'))
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'))
    actype_id = db.Column(db.Integer)
    advarr_id = db.Column(db.Integer)
    deed_id = db.Column(db.Integer, db.ForeignKey('typedeed.id'))
    freq_id = db.Column(db.Integer)
    mailto_id = db.Column(db.Integer)
    prdelivery_id = db.Column(db.Integer)
    salegrade_id = db.Column(db.Integer)
    status_id = db.Column(db.Integer)
    tenure_id = db.Column(db.Integer)

    case_rent = db.relationship('Case', backref='rent', lazy='dynamic')
    charge_rent = db.relationship('Charge', backref='rent', lazy='dynamic')
    digfile_rent = db.relationship('DigFile', backref='rent', lazy='dynamic')
    docfile_rent = db.relationship('DocFile', backref='rent', lazy='dynamic')
    event_rent = db.relationship('Event', backref='rent', lazy='dynamic')
    incomealloc_rent = db.relationship('IncomeAlloc', backref='rent', lazy='dynamic')
    lease_rent = db.relationship('Lease', backref='rent', lazy='dynamic')
    prop_rent = db.relationship('Property', backref='rent')
    payrequest_rent = db.relationship('PrHistory', backref='rent', lazy='dynamic')

    def __repr__(self):
        return '{}'.format(self.rentcode)


class Rental(db.Model):
    __tablename__ = 'rental'

    id = db.Column(db.Integer, primary_key=True)
    rentalcode = db.Column(db.String(15), index=True, unique=True)
    propaddr = db.Column(db.String(120))
    tenantname = db.Column(db.String(90))
    rentpa = db.Column(db.Numeric(8, 2))
    advarr_id = db.Column(db.Integer)
    arrears = db.Column(db.Numeric(8, 2))
    startrentdate = db.Column(db.Date)
    note = db.Column(db.String(90))
    freq_id = db.Column(db.Integer)
    astdate = db.Column(db.Date)
    lastgastest = db.Column(db.Date)


class RentalStat(db.Model):
    __tablename__ = 'rental_statement'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    memo = db.Column(db.String(60))
    amount = db.Column(db.Numeric(8, 2))
    payer = db.Column(db.String(60))
    balance = db.Column(db.Numeric(8, 2))


class RentExternal(db.Model):
    __tablename__ = 'rent_external'

    id = db.Column(db.Integer, primary_key=True)
    rentcode = db.Column(db.String(20), index=True, unique=True)
    tenantname = db.Column(db.String(30))
    propaddr = db.Column(db.String(180))
    agentdetail = db.Column(db.String(45))
    rentpa = db.Column(db.Numeric(8, 2))
    arrears = db.Column(db.Numeric(8, 2))
    lastrentdate = db.Column(db.Date)
    tenure = db.Column(db.String(1))
    owner = db.Column(db.String(15))
    source = db.Column(db.String(15))
    status = db.Column(db.String(1))
    extmanager_id = db.Column(db.Integer, db.ForeignKey('manager_external.id'))
    datecode_id = db.Column(db.Integer, default=0)


class TypeDeed(db.Model):
    __tablename__ = 'typedeed'

    id = db.Column(db.Integer, primary_key=True)
    deedcode = db.Column(db.String(15))
    nfee = db.Column(db.Numeric(8, 2))
    nfeeindeed = db.Column(db.String(45))
    info = db.Column(db.String(90))

    rent_typedeed = db.relationship('Rent', backref='typedeed', lazy='dynamic')


class TypeDoc(db.Model):
    __tablename__ = 'typedoc'

    id = db.Column(db.Integer, primary_key=True)
    desc = db.Column(db.String(30))

    form_letter_typedoc = db.relationship('FormLetter', backref='typedoc', lazy='dynamic')
    digfile_typedoc = db.relationship('DigFile', backref='typedoc', lazy='dynamic')
    docfile_typedoc = db.relationship('DocFile', backref='typedoc', lazy='dynamic')


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
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


@app.context_processor
def inject_models():
    # this is called by Flask on every request
    # inject a dictionary of certain model types, so they are easily accessible in any template
    return {
        'Landlords': Landlord,
    }


@login.user_loader
def load_user(id):
    current_user = User.query.get(int(id))
    try:
        id_list = json.loads(getattr(current_user, "recent_rents"))
    except (AttributeError, TypeError, ValueError):
        id_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    current_user.most_recent_rent = id_list[0]

    return current_user
