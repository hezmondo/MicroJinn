from flask import request
from app.dao.functions import commit_to_database
from app.models import Agent, Case, Charge, DocFile, DigFile, EmailAcc, FormLetter, Income, IncomeAlloc, Landlord, Loan, \
    MoneyItem, Property, PrCharge, PrHistory, Rent, RentExt, MoneyAcc, User


def delete_record(item_id, item):
    id_2 = request.args.get('id_2')
    id_dict = {}
    redir = "util_bp.home"
    if item == "agent":
        Agent.query.filter_by(id=item_id).delete()
        redir = "util_bp.agents"
    elif item == "case":
        Case.query.filter_by(id=item_id).delete()
        redir = "rent_bp.rent"
    elif item == "charge":
        Charge.query.filter_by(id=item_id).delete()
        redir = "rent_bp.rent"
        id_dict = {"id": id_2}
    elif item == "doc":
        DocFile.query.filter_by(id=item_id).delete()
        redir = "doc_bp.docfiles"
    elif item == "dig":
        DigFile.query.filter_by(id=item_id).delete()
        redir = "doc_bp.docfiles"
    elif item == "email_acc":
        EmailAcc.query.filter_by(id=item_id).delete()
        redir = "util_bp.email_accs"
    elif item == "formletter":
        FormLetter.query.filter_by(id=item_id).delete()
        redir = "formletter_bp.forms"
    elif item == "income":
        Income.query.filter_by(id=item_id).delete()
        redir = "income_bp.income"
    elif item == "incomealloc":
        IncomeAlloc.query.filter_by(id=item_id).delete()
        redir = "income_bp.income"
    elif item == "landlord":
        Landlord.query.filter_by(id=item_id).delete()
        redir = "landlord_bp.landlords"
    elif item == "loan":
        Loan.query.filter_by(id=item_id).delete()
        redir = "loan_bp.loans"
    elif item == "money_acc":
        MoneyAcc.query.filter_by(id=item_id).delete()
        redir = "money_bp.moneyaccs"
    elif item == "money_item":
        MoneyItem.query.filter_by(id=item_id).delete()
        redir = "money_bp.money_items"
        id_dict = {"id": id_2}
    elif item == "pr_charge":
        PrCharge.query.filter_by(id=item_id).delete()
        redir = "pr_bp.pr_history"
    elif item == "property":
        Property.query.filter_by(id=item_id).delete()
        redir = "properties"
    elif item == "pr_file":
        PrHistory.query.filter_by(id=item_id).delete()
        redir = "pr_bp.pr_history"
        id_dict = {"rent_id": id_2}
    elif item == "rent":
        Rent.query.filter_by(id=item_id).delete()
    elif item == "rent_ex":
        RentExt.query.filter_by(id=item_id).delete()
    commit_to_database()
    return redir, id_dict


def delete_record_basic(item_id, item):
    if item == "case":
        Case.query.filter_by(id=item_id).delete()
    elif item == "charge":
        Charge.query.filter_by(id=item_id).delete()
    elif item == "pr_charge":
        PrCharge.query.filter_by(id=item_id).delete()
    elif item == "pr_file":
        PrHistory.query.filter_by(id=item_id).delete()
