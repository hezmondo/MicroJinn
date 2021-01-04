from app import db
from flask import flash, redirect, url_for, request
from sqlalchemy import func
from app.main.common import pop_idlist_recent
from app.main.functions import commit_to_database, strToDec

from app.models import Agent, Landlord, Manager, Property, Rent, Typeactype, Typeadvarr, Typedeed, Typefreq, \
    Typemailto, Typeproperty, Typesalegrade, Typestatus, Typetenure


def getrentobj_main(id):
    pop_idlist_recent("recent_rents", id)
    rentobj = \
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
    if rentobj is None:
        flash('Invalid rent code')
        return redirect(url_for('auth.login'))

    properties = \
        Property.query \
            .join(Rent) \
            .join(Typeproperty) \
            .with_entities(Property.id, Property.propaddr, Typeproperty.proptypedet) \
            .filter(Rent.id == id) \
            .all()

    return rentobj, properties


def postrentobj(id):
    if id == 0:
        # new rent:
        rent = Rent()
        agent = Agent()
        rent.rentcode = request.form.get("rentcode")
        rent.id = 0
    else:
        # existing rent:
        rent = Rent.query.get(id)
        agent = Agent.query.filter(Agent.id == rent.agent_id).one_or_none()

    actype = request.form.get("actype")
    rent.actype_id = \
        Typeactype.query.with_entities(Typeactype.id).filter(Typeactype.actypedet == actype).one()[0]
    advarr = request.form.get("advarr")
    rent.advarr_id = \
        Typeadvarr.query.with_entities(Typeadvarr.id).filter(Typeadvarr.advarrdet == advarr).one()[0]
    rent.arrears = strToDec(request.form.get("arrears"))

    # we may write code later to generate datecode from lastrentdate!:
    rent.datecode = request.form.get("datecode")

    deedtype = request.form.get("deedtype")
    rent.deed_id = \
        Typedeed.query.with_entities(Typedeed.id).filter(Typedeed.deedcode == deedtype).one()[0]
    rent.email = request.form.get("email")
    frequency = request.form.get("frequency")
    rent.freq_id = \
        Typefreq.query.with_entities(Typefreq.id).filter(Typefreq.freqdet == frequency).one()[0]
    landlord = request.form.get("landlord")
    rent.landlord_id = \
        Landlord.query.with_entities(Landlord.id).filter(Landlord.landlordname == landlord).one()[0]
    rent.lastrentdate = request.form.get("lastrentdate")
    mailto = request.form.get("mailto")
    rent.mailto_id = \
        Typemailto.query.with_entities(Typemailto.id).filter(Typemailto.mailtodet == mailto).one()[0]
    rent.note = request.form.get("note") or ""
    if request.form.get("price") != "None":
        rent.price = strToDec(request.form.get("price")) or strToDec("99999")
    rent.rentpa = strToDec(request.form.get("rentpa"))
    salegrade = request.form.get("salegrade")
    rent.salegrade_id = \
        Typesalegrade.query.with_entities(Typesalegrade.id).filter(Typesalegrade.salegradedet == salegrade).one()[0]
    rent.source = request.form.get("source")
    status = request.form.get("status")
    rent.status_id = \
        Typestatus.query.with_entities(Typestatus.id).filter(Typestatus.statusdet == status).one()[0]
    rent.tenantname = request.form.get("tenantname")
    tenure = request.form.get("tenure")
    rent.tenure_id = \
        Typetenure.query.with_entities(Typetenure.id).filter(Typetenure.tenuredet == tenure).one()[0]

    agdetails = request.form.get("agent")
    if agdetails and agdetails != "None":
        if not agent:
            agent = Agent()
            agent.agdetails = agdetails
            agent.rent_agent.append(rent)
            db.session.add(agent)
        else:
            agent.agdetails = agdetails
    db.session.commit()

    return redirect('/rent_object/{}'.format(id))
