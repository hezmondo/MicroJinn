from flask import redirect, url_for
from app import db
from app.main.functions import commit_to_database
from app.models import Agent, Charge, Doc_out, Extmanager, Extrent, Income, Incomealloc, \
    Landlord, Lease, Loan, Manager, Money_item, Property, Rent, Rental, Template, \
    Typeactype, Typeadvarr, Money_account, Typedeed, Typefreq, Typedoc, \
    Typemailto, Typepayment, Typeproperty, Typesalegrade, Typestatus, Typetenure, User, Emailaccount


def delete_record(id, item):
    if item == "agent":
        d_agent = Agent.query.get(id)
        db.session.delete(d_agent)
        db.session.commit()
        return redirect('/agents')
    elif item == "bankitem":
        d_bankitem = Money_item.query.get(id)
        if d_bankitem:
            db.session.delete(d_bankitem)
            db.session.commit()
            return redirect('/money')
    elif item == "charge":
        d_charge = Charge.query.get(id)
        if d_charge:
            db.session.delete(d_charge)
            db.session.commit()
            return redirect('/charges')
    elif item == "emailacc":
        d_emailacc = Emailaccount.query.get(id)
        if d_emailacc:
            db.session.delete(d_emailacc)
            db.session.commit()
            return redirect('/emailaccs')
    elif item == "incomealloc":
        d_alloc = Incomealloc.query.get(id)
        if d_alloc:
            db.session.delete(d_alloc)
            db.session.commit()
            return redirect('/income')
    elif item == "landlord":
        d_landlord = Landlord.query.get(id)
        if d_landlord:
            db.session.delete(d_landlord)
            db.session.commit()
            return redirect('/landlords')
    elif item == "loan":
        d_loan = Loan.query.get(id)
        # delete_loan_trans = Loan_trans.query.filter(Loan_trans.loan_id == id).all()
        # delete_loan_interest_rate = Loan_interest_rate.query.filter(Loan_interest_rate.loan_id == id).all()
        # db.session.delete(delete_loan_interest_rate)
        # db.session.delete(delete_loan_trans)
        db.session.delete(d_loan)
        db.session.commit()
        return redirect('/loans')
    elif item == "moneyacc":
        d_moneyacc = Money_account.query.get(id)
        if d_moneyacc:
            db.session.delete(d_moneyacc)
            db.session.commit()
            return redirect('/money_accounts')
    elif item == "rentprop":
        d_rent = Rent.query.get(id)
        d_property = Property.query.filter(Property.rent_id == id).first()
        if d_property:
            db.session.delete(d_property)
        db.session.delete(d_rent)
        db.session.commit()
        return redirect(url_for('main.index'))
