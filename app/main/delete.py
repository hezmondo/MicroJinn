from flask import redirect, request, url_for
from app import db
from app.main.functions import commit_to_database
from app.models import Agent, Charge, Digfile, Docfile, Extmanager, Extrent, Formletter, Income, Incomealloc, \
    Landlord, Lease, Loan, Manager, Money_item, Property, Rent, Rental, Template, \
    Typeactype, Typeadvarr, Money_account, Typedeed, Typefreq, Typedoc, \
    Typemailto, Typepayment, Typeproperty, Typesalegrade, Typestatus, Typetenure, User, Emailaccount


def delete_record(id):
    item = request.args.get('item', "view", type=str)
    rentid = int(request.args.get('rentid', "0", type=str))
    d_item = None
    d_item_1 = None
    if item == "agent":
        d_item = Agent.query.get(id)
    elif item == "bankitem":
        d_item = Money_item.query.get(id)
    elif item == "charge":
        d_item = Charge.query.get(id)
    elif item == "dig":
        d_item = Digfile.query.get(id)
    elif item == "emailacc":
        d_item = Emailaccount.query.get(id)
    elif item == "formletter":
        d_item = Formletter.query.get(id)
    elif item == "incomealloc":
        d_item = Incomealloc.query.get(id)
    elif item == "landlord":
        d_item = Landlord.query.get(id)
    elif item == "loan":
        d_item = Loan.query.get(id)
        # delete_loan_trans = Loan_trans.query.filter(Loan_trans.loan_id == id).all()
        # delete_loan_interest_rate = Loan_interest_rate.query.filter(Loan_interest_rate.loan_id == id).all()
        # db.session.delete(delete_loan_interest_rate)
        # db.session.delete(delete_loan_trans)
    elif item == "moneyacc":
        d_item = Money_account.query.get(id)
    elif item == "rentprop":
        d_item = Rent.query.get(id)
        d_item_1 = Property.query.filter(Property.rent_id == id).first()
    if d_item:
        db.session.delete(d_item)
        if d_item_1:
            db.session.delete(d_item_1)
        commit_to_database()
    return rentid
