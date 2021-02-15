from app import db
from flask import flash, redirect, url_for, request
from sqlalchemy import func
from app.dao.common import get_postvals_id, pop_idlist_recent
from app.dao.functions import strToDec

from app.models import Agent, Landlord, Manager, MoneyAcc, Rent, TypeAcType, TypeAdvArr, TypeDeed, TypeFreq, \
    TypeMailTo, TypeSaleGrade, TypeStatus, TypeTenure


def create_new_rent():
    # create new rent and property function not yet built, so return id for dummy rent:

    return 23


def get_rent(rent_id):
    if rent_id == 0:
        # take the user to create new rent function:
        rent_id = create_new_rent()
    rent_ = \
        Rent.query \
            .join(Landlord) \
            .join(Manager) \
            .outerjoin(Agent) \
            .join(TypeAcType) \
            .join(TypeAdvArr) \
            .join(TypeDeed) \
            .join(TypeFreq) \
            .join(TypeMailTo) \
            .join(TypeSaleGrade) \
            .join(TypeStatus) \
            .join(TypeTenure) \
            .with_entities(Rent.id, Rent.rentcode, Rent.arrears, Rent.datecode, Rent.email, Rent.lastrentdate,
                           # the following function takes id, rentype (1 for Rent or 2 for Headrent) and periods
                           func.mjinn.next_rent_date(Rent.id, 1, 1).label('nextrentdate'),
                           func.mjinn.prop_addr(Rent.id).label('propaddr'),
                           func.mjinn.tot_charges(Rent.id).label('totcharges'),
                           Rent.note, Rent.price, Rent.rentpa, Rent.source, Rent.tenantname, Rent.freq_id,
                           Agent.id.label("agent_id"), Agent.detail, Landlord.name, Manager.managername,
                           TypeAcType.actypedet, TypeAdvArr.advarrdet, TypeDeed.deedcode, TypeFreq.freqdet,
                           TypeMailTo.mailtodet, TypeSaleGrade.salegradedet,
                           TypeStatus.statusdet, TypeTenure.tenuredet) \
            .filter(Rent.id == rent_id) \
            .one_or_none()
    if rent_ is None:
        flash('Invalid rent code')
        return redirect(url_for('auth.login'))
    else:
        pop_idlist_recent("recent_rents", rent_id)

    return rent_


def get_rent_addrs(rent_id):
    rent_addrs = \
        Rent.query.join(TypeMailTo).with_entities(Rent.id, Rent.rentcode, Rent.tenantname,
                                                  func.mjinn.mail_addr(Rent.id, 0, 0).label('mailaddr'),
                                                  func.mjinn.prop_addr(Rent.id).label('propaddr'),
                                                  func.mjinn.tot_charges(Rent.id).label('totcharges'),
                                                  TypeMailTo.mailtodet) \
            .filter(Rent.id == rent_id) \
            .one_or_none()
    if rent_addrs is None:
        flash('Invalid rent code')

        return redirect(url_for('auth.login'))

    return rent_addrs


def get_rent_mail(rent_id):
    rent_mail = \
        Rent.query \
            .join(Landlord) \
            .join(Manager) \
            .join(MoneyAcc) \
            .join(TypeAdvArr) \
            .join(TypeFreq) \
            .join(TypeStatus) \
            .join(TypeTenure) \
            .with_entities(Rent.id, Rent.rentcode, Rent.arrears, Rent.datecode, Rent.email, Rent.lastrentdate,
                           func.mjinn.check_pr_exists(Rent.id).label('prexists'),
                           func.mjinn.mail_addr(Rent.id, 0, 0).label('mailaddr'),
                           # the following functions take id, renttype (1 for Rent or 2 for Headrent) and periods
                           func.mjinn.next_rent_date(Rent.id, 1, 1).label('nextrentdate'),
                           func.mjinn.next_rent_date(Rent.id, 1, 2).label('nextrentdate_plus1'),
                           func.mjinn.next_rent_date(Rent.id, 1, 3).label('nextrentdate_plus2'),
                           func.mjinn.paid_to_date(Rent.id).label('paidtodate'),
                           func.mjinn.prop_addr(Rent.id).label('propaddr'),
                           func.mjinn.tot_charges(Rent.id).label('totcharges'),
                           func.mjinn.last_arrears_level(Rent.id).label('lastarrearslevel'),
                           Rent.rentpa, Rent.tenantname, Rent.freq_id, Landlord.name,
                           Manager.managername, Manager.manageraddr, Manager.manageraddr2,
                           MoneyAcc.bank_name, MoneyAcc.acc_name, MoneyAcc.acc_num, MoneyAcc.sort_code,
                           TypeAdvArr.advarrdet, TypeFreq.freqdet, TypeStatus.statusdet, TypeTenure.tenuredet) \
            .filter(Rent.id == rent_id) \
            .one_or_none()

    return rent_mail


def post_rent(rent_id):
    rent = Rent.query.get(rent_id)
    postvals_id = get_postvals_id()
    # we need the post values with the class id generated for the actual combobox values:
    rent.actype_id = postvals_id["actype"]
    rent.advarr_id = postvals_id["advarr"]
    rent.arrears = strToDec(request.form.get("arrears"))
    # we may write code later to generate datecode from lastrentdate!:
    rent.datecode = request.form.get("datecode")
    rent.deed_id = request.form.get("deedcode")
    rent.email = request.form.get("email")
    rent.freq_id = postvals_id["frequency"]
    rent.landlord_id = postvals_id["landlord"]
    rent.lastrentdate = request.form.get("lastrentdate")
    rent.mailto_id = postvals_id["mailto"]
    rent.note = request.form.get("note")
    rent.prdelivery_id = postvals_id["prdelivery"]
    rent.price = strToDec(request.form.get("price")) or strToDec("99999")
    rent.rentcode = request.form.get("rentcode")
    rent.rentpa = strToDec(request.form.get("rentpa"))
    rent.rentcode = request.form.get("rentcode")
    rent.salegrade_id = postvals_id["salegrade"]
    rent.source = request.form.get("source")
    rent.status_id = postvals_id["status"]
    rent.tenantname = request.form.get("tenantname")
    rent.tenure_id = postvals_id["tenure"]
    db.session.add(rent)
    db.session.flush()
    rent_id = rent.id
    db.session.commit()

    return rent_id


def update_roll_rent(rent_id, arrears):
    rent = Rent.query.get(rent_id)
    last_rent_date = db.session.execute(func.mjinn.next_rent_date(rent.id, 1, 1)).scalar()
    rent.lastrentdate = last_rent_date
    rent.arrears = arrears


# def update_roll_rents(rent_mails):
#     update_vals = []
#     for rent_mailop in rent_mails:
#         update_vals.append(update_roll_rent(rent_mailop.id))
#     db.session.bulk_update_mappings(Rent, update_vals)
