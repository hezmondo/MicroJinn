import json
import sqlalchemy
from app import db
from datetime import date
from dateutil.relativedelta import relativedelta
from flask import flash, redirect, url_for, request
from flask_login import current_user
from sqlalchemy import func
from app.main.common import get_idlist_recent
from app.main.functions import commit_to_database, dateToStr, strToDate, strToDec

from app.models import Agent, Charge, Chargetype, Extmanager, Extrent, Jstore, Landlord, Lease, Lease_uplift_type, \
    Manager, Pr_filter, Property, Rent, Typeactype, Typeadvarr, Money_account, Typedeed, Typefreq, \
    Typemailto, Typeprdelivery, Typeproperty, Typesalegrade, Typestatus, Typetenure, User, Emailaccount


# agents
def get_agents():
    if request.method == "POST":
        agd = request.form.get("address") or ""
        age = request.form.get("email") or ""
        agn = request.form.get("notes") or ""
        agents = Agent.query.filter(Agent.agdetails.ilike('%{}%'.format(agd)), Agent.agemail.ilike('%{}%'.format(age)),
                        Agent.agnotes.ilike('%{}%'.format(agn))).all()
    else:
        id_list = get_idlist_recent("recent_agents")
        agents = Agent.query.filter(Agent.id.in_(id_list))
    return agents


def get_agent(id):

    if id == 0:
        agent = Agent()
        agent.id = 0
    else:
        agent = Agent.query.get(id)
        pop_idlist_recent("recent_agents", id)

    return agent


# charges
def get_charge(id):
    rentcode = request.args.get('rentcode', "XNEWX" , type=str)
    rentid = int(request.args.get('rentid', "0", type=str))
    # new charge has id = 0
    if id == 0:
        charge = {
            'id': 0,
            'rentid': rentid,
            'rentcode': rentcode,
            'chargedesc': "notice fee",
            'chargestartdate': date.today()
        }
    else:
        charge = \
            Charge.query.join(Rent).join(Chargetype).with_entities(Charge.id, Rent.id.label("rentid"), Rent.rentcode,
                   Chargetype.chargedesc, Charge.chargestartdate, Charge.chargetotal, Charge.chargedetails,
                       Charge.chargebalance) \
                    .filter(Charge.id == id).one_or_none()
    chargedescs = [value for (value,) in Chargetype.query.with_entities(Chargetype.chargedesc).all()]

    return charge, chargedescs


def get_charges(rentid):
    qfilter = []
    if request.method == "POST":
        rcd = request.form.get("rentcode") or ""
        cdt = request.form.get("chargedetails") or ""
        qfilter.append(Rent.rentcode.startswith([rcd]))
        qfilter.append(Charge.chargedetails.ilike('%{}%'.format(cdt)))
    elif rentid != "0":
        qfilter.append(Charge.rent_id == rentid)

    charges = Charge.query.join(Rent).join(Chargetype).with_entities(Charge.id, Rent.rentcode, Chargetype.chargedesc,
                     Charge.chargestartdate, Charge.chargetotal, Charge.chargedetails, Charge.chargebalance) \
            .filter(*qfilter).all()

    return charges


# external rents
def get_externalrent(id):
    externalrent = Extrent.query.join(Extmanager).with_entities(Extrent.rentcode, Extrent.propaddr,
                    Extrent.tenantname, Extrent.owner, Extrent.rentpa, Extrent.arrears, Extrent.lastrentdate,
                        Extrent.source, Extrent.status, Extmanager.codename, Extrent.agentdetails) \
        .filter(Extrent.id == id).one_or_none()

    return externalrent


# landlords
def get_landlords():
    landlords = Landlord.query.join(Manager).with_entities(Landlord.id, Landlord.landlordname, Landlord.landlordaddr,
                   Landlord.taxdate, Manager.managername).all()

    return landlords


def get_landlord(id):
    if id == 0:
        landlord = Landlord()
        landlord.id = 0
    else:
        landlord = Landlord.query.join(Manager).join(Emailaccount).join(Money_account).with_entities(Landlord.id,
                     Landlord.landlordname, Landlord.landlordaddr, Landlord.taxdate, Manager.managername,
                         Emailaccount.smtp_server, Money_account.accdesc).filter(Landlord.id == id).one_or_none()
    return landlord

def get_landlord_extras():
    managers = [value for (value,) in Manager.query.with_entities(Manager.managername).all()]
    emailaccs = [value for (value,) in Emailaccount.query.with_entities(Emailaccount.smtp_server).all()]
    bankaccs = [value for (value,) in Money_account.query.with_entities(Money_account.accdesc).all()]

    return managers, emailaccs, bankaccs


# properties
def get_property(id):
    property = Property.query.join(Typeproperty).with_entities(Property.id, Property.propaddr,
                   Typeproperty.proptypedet).filter(Property.id == id).one_or_none()
    proptypedets = [value for (value,) in Typeproperty.query.with_entities(Typeproperty.proptypedet).all()]

    return property, proptypedets


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


def pop_idlist_recent(recent_field, id):
    id_list = json.loads(getattr(current_user, recent_field))
    if id not in id_list:
        id_list.insert(0, id)
        if len(id_list) > 30:
            id_list.pop()
        setattr(current_user, recent_field, json.dumps(id_list))
        db.session.commit()


def post_agent(id):
    if id == 0:
        agent = Agent()
        agent.id = 0
        agent.code = ""
    else:
        agent = Agent.query.get(id)

    agdet = request.form.get("address")
    agent.agdetails = agdet
    agent.agemail = request.form.get("email")
    agent.agnotes = request.form.get("notes")
    db.session.add(agent)
    commit_to_database()
    agent = Agent.query.filter(Agent.agdetails == agdet).first()

    return agent


def post_charge(id):
    # new charge for id 0, otherwise existing charge:
    if id == 0:
        charge = Charge()
        charge.id = 0
        charge.rent_id = int(request.form.get("rentid"))
    else:
        charge = Charge.query.get(id)
    charge.chargetype_id = \
        Chargetype.query.with_entities(Chargetype.id).filter(
            Chargetype.chargedesc == request.form.get("chargedesc")).one()[0]
    charge.chargestartdate = request.form.get("chargestartdate")
    charge.chargetotal = strToDec(request.form.get("chargetotal"))
    charge.chargedetails = request.form.get("chargedetails")
    charge.chargebalance = strToDec(request.form.get("chargebalance"))
    rent_id = charge.rent_id
    db.session.add(charge)
    db.session.commit()

    return rent_id


def post_landlord(id):
    if id == 0:
        landlord = Landlord()
        landlord.id = 0
    else:
        landlord = Landlord.query.get(id)
    ll_name = request.form.get("name")
    landlord.landlordname = ll_name
    landlord.landlordaddr = request.form.get("address")
    landlord.taxdate = request.form.get("taxdate")
    emailacc = request.form.get("emailacc")
    landlord.emailacc_id = \
        Emailaccount.query.with_entities(Emailaccount.id).filter \
            (Emailaccount.smtp_server == emailacc).one()[0]
    bankacc = request.form.get("bankacc")
    landlord.bankacc_id = \
        Money_account.query.with_entities(Money_account.id).filter \
            (Money_account.accdesc == bankacc).one()[0]
    manager = request.form.get("manager")
    landlord.manager_id = \
        Manager.query.with_entities(Manager.id).filter \
            (Manager.managername == manager).one()[0]
    db.session.add(landlord)
    commit_to_database()
    landlord = Landlord.query.filter(Landlord.landlordname == ll_name).first()

    return landlord


def post_property(id, action):
    if action == "edit":
        property = Property.query.get(id)
    else:
        property = Property()
    property.propaddr = request.form.get("propaddr")
    proptypedet = request.form.get("proptypedet")
    property.typeprop_id = \
        Typeproperty.query.with_entities(Typeproperty.id).filter \
            (Typeproperty.proptypedet == proptypedet).one()[0]
    db.session.add(property)
    db.session.commit()
    id_ = property.id

    return id_


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
