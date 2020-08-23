import json
from flask import redirect, request
from app import db
from app.main.functions import commit_to_database, convert_html_to_pdf
from app.models import Agent, Charge, Chargetype, Doc, Doc_out, Extmanager, Extrent, Income, Incomealloc, \
    Landlord, Loan, Manager, Money_category, Money_item, Property, Rent, Rental, Template, \
    Typeactype, Typeadvarr, Money_account, Typedeed, Typefreq, Typedoc, \
    Typemailto, Typepayment, Typeproperty, Typesalegrade, Typestatus, Typetenure, User, Emailaccount


def post_agent(id, action):
    if action == "edit":
        agent = Agent.query.get(id)
    else:
        agent = Agent()
    agent.agdetails = request.form["address"]
    agent.agemail = request.form["email"]
    agent.agnotes = request.form["notes"]
    db.session.add(agent)
    commit_to_database()
    id_ = agent.id

    return id_


def post_charge(id, action):
    if action == "edit":
        charge = Charge.query.get(id)
    else:
        charge = Charge()
    charge.chargetype_id = \
        Chargetype.query.with_entities(Chargetype.id).filter(
            Chargetype.chargedesc == request.form["chargedesc"]).one()[0]
    charge.chargestartdate = request.form["chargestartdate"]
    charge.chargetotal = request.form["chargetotal"]
    charge.chargedetails = request.form["chargedetails"]
    charge.chargebalance = request.form["chargebalance"]
    db.session.add(charge)
    db.session.commit()
    id_ = charge.id

    return id_


def post_doc(id, action):
    if action == "edit":
        doc = Doc.query.get(id)
    else:
        doc = Doc()
    doc.code = request.form["code"]
    doc.subject = request.form["subject"]
    doc.part1 = request.form["part1"]
    doc.part2 = request.form["part2"]
    doc.part3 = request.form["part3"]
    type = request.form["doc_type"]
    doc.type_id = \
        Typedoc.query.with_entities(Typedoc.id).filter \
            (Typedoc.desc == type).one()[0]
    template = request.form["template"]
    doc.template_id = \
        Template.query.with_entities(Template.id).filter \
            (Template.code == template).one()[0]
    db.session.add(doc)
    db.session.commit()
    id_ = doc.id
    return id_


def post_emailaccount(id, action):
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
    db.session.add(emailacc)
    db.session.commit()
    id_ = emailacc.id

    return id_


def post_incomeobject(id, action):
    # this object comprises 1 income record plus 1 or more incomealloc records. First, we do the income record
    if action == "edit":
        income = Income.query.get(id)
    else:
        income = Income()
    income.paydate = request.form.get("paydate")
    income.amount = request.form.get("amount")
    income.payer = request.form.get("payer")
    bankacc = request.form.get("bankacc")
    income.bankacc_id = \
        Money_account.query.with_entities(Money_account.id).filter(Money_account.accdesc == bankacc).one()[0]
    paytype = request.form.get("paytype")
    income.paytype_id = \
        Typepayment.query.with_entities(Typepayment.id).filter(Typepayment.paytypedet == paytype).one()[0]
    # having set the column values, we add this single income record to the db session
    db.session.add(income)
    # now we get the income allocations from the request form to post 1 or more records to the incomealloc table
    if action == "edit":
        allocs = zip(request.form.getlist("incall_id"), request.form.getlist('rentcode'),
                         request.form.getlist('alloctot'), request.form.getlist("chargedesc"))
        for incall_id, rentcode, alloctot, chargedesc in allocs:
            print(incall_id, rentcode, alloctot, chargedesc)
            if alloctot == "0" or alloctot == "0.00":
                continue
            if incall_id and int(incall_id) > 0:
                incalloc = Incomealloc.query.get(int(incall_id))
            else:
                incalloc = Incomealloc()
            incalloc.rentcode = rentcode
            incalloc.amount = alloctot
            print(incalloc.amount)
            incalloc.chargetype_id = \
                Chargetype.query.with_entities(Chargetype.id).filter(Chargetype.chargedesc == chargedesc).one()[0]
            print(incalloc.chargetype_id)
            incalloc.landlord_id = \
                Landlord.query.join(Rent).with_entities(Landlord.id).filter(Rent.rentcode == rentcode).one()[0]
            # having set the column values, we add each incomealloc record to the db session (using the ORM relationship)
            income.incomealloc_income.append(incalloc)
    else:
        allocs = zip(request.form.getlist('rentcode'), request.form.getlist("c_id"), request.form.getlist("chargedesc"),
                     request.form.getlist('alloctot'), request.form.getlist('landlord'))
        for rentcode, alloctot, c_id, chargedesc, landlord in allocs:
            print(rentcode, alloctot, c_id, chargedesc, landlord)
            if alloctot == "0" or alloctot == "0.00":
                continue
            incalloc = Incomealloc()
            incalloc.rentcode = rentcode
            incalloc.amount = alloctot
            print(incalloc.amount)
            incalloc.chargetype_id = \
                Chargetype.query.with_entities(Chargetype.id).filter(Chargetype.chargedesc == chargedesc).one()[0]
            print(incalloc.chargetype_id)
            incalloc.landlord_id = \
                Landlord.query.with_entities(Landlord.id).filter(Landlord.landlordname == landlord).one()[0]
            # having set the column values, we add each incomealloc record to the db session (using the ORM relationship)
            income.incomealloc_income.append(incalloc)
            # now we have to deal with updating or deleting existing charges
            if c_id  and c_id > 0:
                d_charge = Charge.query.get(c_id)
                db.session.delete(d_charge)

    # having added the income record and all incomealloc records to the db session, we now attempt a commit
    db.session.commit()
    # in case of a new record, we need to find and return the new id, to display the new (or updated) income object
    id_ = income.id

    return id_


def post_landlord(id, action):
    if action == "edit":
        landlord = Landlord.query.get(id)
    else:
        landlord = Landlord()
    landlord.landlordname = request.form["name"]
    landlord.landlordaddr = request.form["address"]
    landlord.taxdate = request.form["taxdate"]
    emailacc = request.form["emailacc"]
    landlord.emailacc_id = \
        Emailaccount.query.with_entities(Emailaccount.id).filter \
            (Emailaccount.smtp_server == emailacc).one()[0]
    bankacc = request.form["bankacc"]
    landlord.bankacc_id = \
        Money_account.query.with_entities(Money_account.id).filter \
            (Money_account.accdesc == bankacc).one()[0]
    manager = request.form["manager"]
    landlord.manager_id = \
        Manager.query.with_entities(Manager.id).filter \
            (Manager.managername == manager).one()[0]
    db.session.add(landlord)
    db.session.commit()
    id_ = landlord.id
    return id_


def post_loan(id, action):
    if action == "edit":
        loan = Loan.query.get(id)
    else:
        loan = Loan()
    loan.code = request.form["loancode"]
    loan.start_intrate = request.form["start_intrate"]
    loan.end_date = request.form["end_date"]
    frequency = request.form["frequency"]
    loan.freq_id = \
        Typefreq.query.with_entities(Typefreq.id).filter(Typefreq.freqdet == frequency).one()[0]
    advarr = request.form["advarr"]
    loan.advarr_id = \
        Typeadvarr.query.with_entities(Typeadvarr.id).filter(Typeadvarr.advarrdet == advarr).one()[0]
    loan.lender = request.form["lender"]
    loan.borrower = request.form["borrower"]
    loan.notes = request.form["notes"]
    loan.val_date = request.form["val_date"]
    loan.valuation = request.form["valuation"]
    db.session.commit()
    id_ = loan.id

    return id_


def post_moneyaccount(id, action):
    if action == "edit":
        moneyacc = Money_account.query.get(id)
    else:
        moneyacc = Money_account()
    moneyacc.bankname = request.form["bankname"]
    moneyacc.accname = request.form["accname"]
    moneyacc.sortcode = request.form["sortcode"]
    moneyacc.accnum = request.form["accnum"]
    moneyacc.accdesc = request.form["accdesc"]
    db.session.add(moneyacc)
    db.session.commit()
    id_ = moneyacc.id

    return id_


def post_moneyitem(id, action):
    if action == "edit":
        bankitem = Money_item.query.get(id)
    else:
        bankitem = Money_item()
    bankitem.num = request.form["num"]
    bankitem.date = request.form["date"]
    bankitem.amount = request.form["amount"]
    bankitem.payer = request.form["payer"]
    accdesc = request.form["accdesc"]
    bankitem.bankacc_id = \
        Money_account.query.with_entities(Money_account.id).filter \
            (Money_account.accdesc == accdesc).one()[0]
    cleared = request.form["cleared"]
    bankitem.cleared = 1 if cleared == "cleared" else 0
    cat = request.form["category"]
    bankitem.cat_name = \
        Money_category.query.with_entities(Money_category.id).filter \
            (Money_category.cat_name == cat).one()[0]
    db.session.add(bankitem)
    db.session.commit()
    id_ = bankitem.id

    return id_


def post_property(id, action):
    if action == "edit":
        property = Property.query.get(id)
    else:
        property = Property()
    property.propaddr = request.form["propaddr"]
    proptypedet = request.form["proptypedet"]
    property.typeprop_id = \
        Typeproperty.query.with_entities(Typeproperty.id).filter \
            (Typeproperty.proptypedet == proptypedet).one()[0]
    db.session.add(property)
    db.session.commit()
    id_ = property.id

    return id_


def post_rental(id, action):
    if action == "edit":
        rental = Rental.query.get(id)
    else:
        rental = Rental()
    rental.propaddr = request.form["propaddr"]
    rental.tenantname = request.form["tenantname"]
    rental.rentpa = request.form["rentpa"]
    rental.arrears = request.form["arrears"]
    rental.startrentdate = request.form["startrentdate"]
    if rental.astdate:
        rental.astdate = request.form["astdate"]
    rental.lastgastest = request.form["lastgastest"]
    rental.note = request.form["note"]
    frequency = request.form["frequency"]
    rental.freq_id = \
        Typefreq.query.with_entities(Typefreq.id).filter(Typefreq.freqdet == frequency).one()[0]
    advarr = request.form["advarr"]
    rental.advarr_id = \
        Typeadvarr.query.with_entities(Typeadvarr.id).filter(Typeadvarr.advarrdet == advarr).one()[0]
    db.session.add(rental)
    db.session.commit()
    id_ = rental.id

    return id_

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
        Landlord.query.with_entities(Landlord.id).filter(Landlord.landlordname == landlord).one()[0]
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

    return redirect('/rentobject/{}'.format(id))

def post_html(action):
    if action == "edit":
        doc_out = Doc_out.query.get(id)
    else:
        doc_out = Doc_out()
    doc_out.doc_text = request.form['xinput'].replace("£", "&pound;")
    doc_out.rent_id = request.form['rent_id']
    doc_out.doc_id = request.form['doc_id']
    doc_out.doc_date = request.form['doc_date']
    db.session.add(doc_out)
    db.session.commit()
    id_ = doc_out.rent_id
    source_html = doc_out.doc_text
    output_filename = "testin.pdf"
    convert_html_to_pdf(source_html, output_filename)

    return id_
