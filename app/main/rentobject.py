from app import db
from flask import flash, redirect, url_for, request
from sqlalchemy import func
from app.main.common import get_combo_id, pop_idlist_recent
from app.main.functions import commit_to_database, strToDec

from app.models import Agent, Landlord, Manager, Property, Rent, Typeactype, Typeadvarr, Typedeed, Typefreq, \
    Typemailto, Typeproperty, Typesalegrade, Typestatus, Typetenure


def create_new_rentobject():
    # create new rent function noit yet built, so return id for dummy rent:
    return 23


def get_rentobject(id):
    if id == 0:
        # take the user to create new rent function:
        id = create_new_rentobject()
    elif request.method == "POST":
        id = post_rent(id)
    pop_idlist_recent("recent_rents", id)
    rentobject = \
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
                           Agent.agdetails, Landlord.landlordname, Manager.managername,
                           Typeactype.actypedet, Typeadvarr.advarrdet, Typedeed.deedcode, Typefreq.freqdet,
                           Typemailto.mailtodet, Typesalegrade.salegradedet, Typestatus.statusdet,
                           Typetenure.tenuredet) \
            .filter(Rent.id == id) \
            .one_or_none()
    if rentobject is None:
        flash('Invalid rent code')
        return redirect(url_for('auth.login'))

    properties = \
        Property.query \
            .join(Rent) \
            .join(Typeproperty) \
            .with_entities(Property.id, Property.propaddr, Typeproperty.proptypedet) \
            .filter(Rent.id == id) \
            .all()

    return rentobject, properties


def post_rent(id):
    rent = Rent.query.get(id)
    rent.rentcode = request.form.get("rentcode")
    actype = request.form.get("actype")
    rent.actype_id = get_combo_id("actype", actype)
    advarr = request.form.get("advarr")
    rent.advarr_id = get_combo_id("advarr", advarr)
    rent.arrears = strToDec(request.form.get("arrears"))
    # we may write code later to generate datecode from lastrentdate!:
    rent.datecode = request.form.get("datecode")
    deedtype = request.form.get("deedtype")
    rent.deed_id = get_combo_id("deedtype", deedtype)
    rent.email = request.form.get("email")
    frequency = request.form.get("frequency")
    rent.freq_id = get_combo_id("frequency", frequency)
    landlord = request.form.get("landlord")
    rent.landlord_id = get_combo_id("landlord", landlord)
    rent.lastrentdate = request.form.get("lastrentdate")
    mailto = request.form.get("mailto")
    rent.mailto_id = get_combo_id("mailto", mailto)
    rent.note = request.form.get("note") or ""
    if request.form.get("price") != "None":
        rent.price = strToDec(request.form.get("price")) or strToDec("99999")
    rent.rentpa = strToDec(request.form.get("rentpa"))
    salegrade = request.form.get("salegrade")
    rent.salegrade_id = get_combo_id("salegrade", salegrade)
    rent.source = request.form.get("source")
    status = request.form.get("status")
    rent.status_id = get_combo_id("status", status)
    rent.tenantname = request.form.get("tenantname")
    tenure = request.form.get("tenure")
    rent.tenure_id = get_combo_id("tenure", tenure)
    db.session.add(rent)
    db.session.flush()
    _id = rent.id
    db.session.commit()

    return _id
