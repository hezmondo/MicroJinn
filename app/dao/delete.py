from flask import redirect, request, url_for
from app import db
from app.dao.functions import commit_to_database
from app.models import Agent, Charge, Digfile, Form_letter, Incomealloc, \
    Landlord, Loan, Money_item, Property, Rent, Money_account, Emailaccount


def delete_record(id):
    item = request.args.get('item', "view", type=str)
    id_2 = int(request.args.get('id_2', "0", type=str))
    if item == "agent":
        Agent.query.filter_by(id=id).delete()
        redir = "ag_bp.agents"
    elif item == "bankitem":
        Money_item.query.filter_by(id=id).delete()
    elif item == "charge":
        Charge.query.filter_by(id=id).delete()
        redir = "ro_bp.rent_object/{}".format(id_2)
    elif item == "dig":
        Digfile.query.filter_by(id=id).delete()
    elif item == "emailacc":
        Emailaccount.query.filter_by(id=id).delete()
    elif item == "formletter":
        Form_letter.query.filter_by(id=id).delete()
    elif item == "incomealloc":
        Incomealloc.query.filter_by(id=id).delete()
    elif item == "landlord":
        Landlord.query.filter_by(id=id).delete()
    elif item == "loan":
        Loan.query.filter_by(id=id).delete()
        # delete_loan_trans = Loan_trans.query.filter(Loan_trans.loan_id == id).all()
        # delete_loan_interest_rate = Loan_interest_rate.query.filter(Loan_interest_rate.loan_id == id).all()
        # db.session.delete(delete_loan_interest_rate)
        # db.session.delete(delete_loan_trans)
    elif item == "moneyacc":
        Money_account.query.filter_by(id=id).delete()
    elif item == "rentprop":
        Money_account.query.filter_by(id=id).delete()
    else:
        redir = "views/index"
    commit_to_database()

    return redir, id_2
