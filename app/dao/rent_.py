from app import db
from flask import flash, redirect, url_for, request, session
from sqlalchemy import func
from app.dao.common import get_postvals_id, pop_idlist_recent
from app.dao.functions import strToDec

from app.models import Agent, Landlord, Manager, Property, Rent, Typeactype, Typeadvarr, Typedeed, Typefreq, \
    Typemailto, Typeproperty, Typesalegrade, Typestatus, Typetenure


def create_new_rent():
    # create new rent and property function not yet built, so return id for dummy rent:
    return 23


def get_rent_(rent_id):
    if rent_id == 0:
        # take the user to create new rent function:
        rent_id = create_new_rent()
    rent_ = \
        Rent.query \
            .join(Landlord) \
            .join(Manager) \
            .outerjoin(Agent) \
            .join(Typeactype) \
            .join(Typeadvarr) \
            .join(Typedeed) \
            .join(Typefreq) \
            .join(Typemailto) \
            .join(Typesalegrade) \
            .join(Typestatus) \
            .join(Typetenure) \
            .with_entities(Rent.id, Rent.rentcode, Rent.arrears, Rent.datecode, Rent.email, Rent.lastrentdate,
                           # the following function takes id, rentype (1 for Rent or 2 for Headrent) and periods
                           func.mjinn.next_rent_date(Rent.id, 1, 1).label('nextrentdate'),
                           func.mjinn.paid_to_date(Rent.id).label('paidtodate'),
                           func.mjinn.mail_addr(Rent.id, 0, 0).label('mailaddr'),
                           func.mjinn.prop_addr(Rent.id).label('propaddr'),
                           func.mjinn.tot_charges(Rent.id).label('totcharges'),
                           Rent.note, Rent.price, Rent.rentpa, Rent.source, Rent.tenantname, Rent.freq_id,
                           Agent.id.label("agent_id"), Agent.detail, Landlord.landlordname, Manager.managername,
                           Typeactype.actypedet, Typeadvarr.advarrdet, Typedeed.deedcode, Typefreq.freqdet,
                           Typemailto.mailtodet, Typesalegrade.salegradedet, Typestatus.statusdet,
                           Typetenure.tenuredet) \
            .filter(Rent.id == rent_id) \
            .one_or_none()
    if rent_ is None:
        flash('Invalid rent code')
        return redirect(url_for('auth.login'))
    else:
        pop_idlist_recent("recent_rents", rent_id)

    return rent_


def get_rent_mail(rent_id):
    rent_mail = \
        Rent.query.join(Typemailto).with_entities(Rent.id, Rent.rentcode, Rent.tenantname,
                           func.mjinn.mail_addr(Rent.id, 0, 0).label('mailaddr'),
                           func.mjinn.prop_addr(Rent.id).label('propaddr'),
                           func.mjinn.tot_charges(Rent.id).label('totcharges'),
                           Typemailto.mailtodet) \
            .filter(Rent.id == rent_id) \
            .one_or_none()
    if rent_mail is None:
        flash('Invalid rent code')
        return redirect(url_for('auth.login'))
    else:
        pop_idlist_recent("recent_rents", rent_id)

    return rent_mail


def post_rent(rent_id):
    rent = Rent.query.get(rent_id)
    postvals_id = get_postvals_id()
    # we need the post values with the class id generated for the actual combobox values:
    rent.actype_id = postvals_id["actype"]
    rent.advarr_id = postvals_id["advarr"]
    rent.arrears = strToDec(postvals_id["arrears"])
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
    _id = rent.id
    db.session.commit()

    return _id
