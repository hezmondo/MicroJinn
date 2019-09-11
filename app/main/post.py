from flask import redirect, request

from app import db
from app.models import Agent, Charge, Chargetype, Datef2, Datef4, Extmanager, Extrent, Income, Incomealloc, \
    Landlord, Manager, Property, Rent, Typeactype, Typeadvarr, Typebankacc, Typedeed, Typefreq, Typemailto, \
    Typepayment, Typeproperty, Typesalegrade, Typestatus, Typetenure, User, Emailaccount


def postcharge(id):
    charge = Charge.query.get(id)
    charge.chargetype_id = \
        Chargetype.query.with_entities(Chargetype.id).filter(
            Chargetype.chargedesc == request.form["chargedesc"]).one()[0]
    charge.chargestartdate = request.form["chargestartdate"]
    charge.chargetotal = request.form["chargetotal"]
    charge.chargedetails = request.form["chargedetails"]
    charge.chargebalance = request.form["chargebalance"]
    db.session.commit()
    return


def postemailacc(id, action):
    if action == "edit":
        emailacc = Emailaccount.query.get(id)
    else:
        emailacc = Emailaccount()
    emailacc.smtp_server = request.form["smtp_server"]
    emailacc.smtp_port = request.form["smtp_port"]
    emailacc.smtp_timeout = request.form["smtp_timeout"]
    emailacc.smtp_debug = request.form["smtp_debug"]
    emailacc.smtp_tls = request.form["smtp_tls"]
    emailacc.smtp_user = request.form["smtp_user"]
    emailacc.smtp_password = request.form["smtp_password"]
    emailacc.smtp_sendfrom = request.form["smtp_sendfrom"]
    emailacc.imap_server = request.form["imap_server"]
    emailacc.imap_port = request.form["imap_port"]
    emailacc.imap_tls = request.form["imap_tls"]
    emailacc.imap_user = request.form["imap_user"]
    emailacc.imap_password = request.form["imap_password"]
    emailacc.imap_sentfolder = request.form["imap_sentfolder"]
    emailacc.imap_draftfolder = request.form["imap_draftfolder"]
    if not action == "edit":
        db.session.add(emailacc)
        db.session.commit()
        id = emailacc.id
    else:
        db.session.commit()

    return redirect('/emailaccpage/{}'.format(id))


def postincome(id, action):
    if action == "edit":
        income = Income.query.get(id)
    else:
        income = Income()
    if not action == "edit":
        db.session.add(income)
        db.session.commit()
        id = income.id
    else:
        db.session.commit()

    return redirect('/emailaccpage/{}'.format(id))


def postlandlord(id, action):
    if action == "edit":
        landlord = Landlord.query.get(id)
    else:
        landlord = Landlord()
    landlord.name = request.form["name"]
    landlord.addr = request.form["address"]
    landlord.taxdate = request.form["taxdate"]
    emailacc = request.form["emailacc"]
    landlord.emailacc_id = \
        Emailaccount.query.with_entities(Emailaccount.id).filter \
            (Emailaccount.smtp_server == emailacc).one()[0]
    bankacc = request.form["bankacc"]
    landlord.bankacc_id = \
        Typebankacc.query.with_entities(Typebankacc.id).filter \
            (Typebankacc.accdesc == bankacc).one()[0]
    manager = request.form["manager"]
    landlord.manager_id = \
        Manager.query.with_entities(Manager.id).filter \
            (Manager.name == manager).one()[0]
    if not action == "edit":
        db.session.add(landlord)
        db.session.commit()
        id = landlord.id
    else:
        db.session.commit()

    return redirect('/landlordpage/{}'.format(id))


def postproperty(id):
    property = Property.query.get(id)
    property.propaddr = request.form["propaddr"]
    proptypedet = request.form["proptypedet"]
    property.typeprop_id = \
        Typeproperty.query.with_entities(Typeproperty.id).filter \
            (Typeproperty.proptypedet == proptypedet).one()[0]
    db.session.commit()
    return


def postrentobj(id):
    if id > 0:
        rent = Rent.query.get(id)
        agent = Agent.query.filter(Agent.id == rent.agent_id).one_or_none()
    else:
        rent = Rent()
        agent = Agent()

    actype = request.form["actype"]
    rent.actype_id = \
        Typeactype.query.with_entities(Typeactype.id).filter(Typeactype.actypedet == actype).one()[0]
    advarr = request.form["advarr"]
    rent.advarr_id = \
        Typeadvarr.query.with_entities(Typeadvarr.id).filter(Typeadvarr.advarrdet == advarr).one()[0]
    rent.arrears = request.form["arrears"]

    # we will write code later to generate datecode from lastrentdate!:
    rent.datecode = request.form["datecode"]

    deedtype = request.form["deedtype"]
    rent.deed_id = \
        Typedeed.query.with_entities(Typedeed.id).filter(Typedeed.deedcode == deedtype).one()[0]
    rent.email = request.form["email"]
    frequency = request.form["frequency"]
    rent.freq_id = \
        Typefreq.query.with_entities(Typefreq.id).filter(Typefreq.freqdet == frequency).one()[0]
    landlord = request.form["landlord"]
    rent.landlord_id = \
        Landlord.query.with_entities(Landlord.id).filter(Landlord.name == landlord).one()[0]
    rent.lastrentdate = request.form["lastrentdate"]
    mailto = request.form["mailto"]
    rent.mailto_id = \
        Typemailto.query.with_entities(Typemailto.id).filter(Typemailto.mailtodet == mailto).one()[0]
    rent.note = request.form["note"]
    rent.price = request.form["price"]
    rent.rentpa = request.form["rentpa"]
    salegrade = request.form["salegrade"]
    rent.salegrade_id = \
        Typesalegrade.query.with_entities(Typesalegrade.id).filter(Typesalegrade.salegradedet == salegrade).one()[0]
    rent.source = request.form["source"]
    status = request.form["status"]
    rent.status_id = \
        Typestatus.query.with_entities(Typestatus.id).filter(Typestatus.statusdet == status).one()[0]
    rent.tenantname = request.form["tenantname"]
    tenure = request.form["tenure"]
    rent.tenure_id = \
        Typetenure.query.with_entities(Typetenure.id).filter(Typetenure.tenuredet == tenure).one()[0]

    agdetails = request.form["agent"]
    if agdetails and agdetails != "None":
        if not agent:
            agent = Agent()
            agent.agdetails = agdetails
            agent.rent_agent.append(rent)
            db.session.add(agent)
        else:
            agent.agdetails = agdetails
    if id < 1:
        rent.rentcode = request.form["rentcode"]
        id = rent.id
    else:
        db.session.commit()

    return redirect('/rentobjpage/{}'.format(id))


def postagent(id):
    agent = Agent.query.get(id)
    agent.agdetails = request.form["address"]
    agent.agemail = request.form["email"]
    agent.agnotes = request.form["notes"]
    db.session.commit()
    return
