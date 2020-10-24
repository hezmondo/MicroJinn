import os
import json
import datetime
from flask import flash, redirect, request
from werkzeug.utils import secure_filename
from app import db
from app.main.functions import commit_to_database, convert_html_to_pdf, validate_image
from app.models import Agent, Charge, Chargetype, Formletter, Digfile, Docfile, Extmanager, Extrent, Headrent, Income, \
    Incomealloc, Landlord, Lease, Lease_uplift_type, Loan, Manager, Money_category, Money_item, Property, Rent, \
    Rental, Template, Typeactype, Typeadvarr, Money_account, Typedeed, Typefreq, Typedoc, \
    Typemailto, Typepayment, Typeproperty, Typesalegrade, Typestatus, Typetenure, User, Emailaccount


def post_agent(id, action):
    if action == "edit":
        agent = Agent.query.get(id)
    else:
        agent = Agent()
    agent.agdetails = request.form.get("address")
    agent.agemail = request.form.get("email")
    agent.agnotes = request.form.get("notes")
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
            Chargetype.chargedesc == request.form.get("chargedesc")).one()[0]
    charge.chargestartdate = request.form.get("chargestartdate")
    charge.chargetotal = request.form.get("chargetotal")
    charge.chargedetails = request.form.get("chargedetails")
    charge.chargebalance = request.form.get("chargebalance")
    db.session.add(charge)
    db.session.commit()
    id_ = charge.id

    return id_


def post_digfile(id):
    if id == 0:
        # new docfile:
        newdigfile = Digfile()
    else:
        # existing docfile:
        newdigfile = Docfile.query.get(id)
    if request.form.get('rentcode') and request.form.get('rentcode') != "":
        rentcode = request.form.get('rentcode')
        newdigfile.rent_id = \
            Rent.query.with_entities(Rent.id).filter(Rent.rentcode == rentcode).one()[0]
    newdigfile.digfile_date = request.form.get('digfile_date')
    newdigfile.summary = request.form.get('dgf_summary')
    doctype = request.form.get('doc_type')
    newdigfile.doctype_id = \
        Typedoc.query.with_entities(Typedoc.id).filter(Typedoc.desc == doctype).one()[0]
    newdigfile.out_in = 1 if request.form.get('out_in') == "in" else 0
    db.session.add(newdigfile)
    db.session.commit()
    id_ = newdigfile.id

    return id_


def post_docfile(id):
    if id == 0:
        # new docfile:
        docfile = Docfile()
    else:
        # existing docfile:
        docfile = Docfile.query.get(id)
    if request.form.get('rentcode') and request.form.get('rentcode') != "":
        rentcode = request.form.get('rentcode')
        docfile.rent_id = \
            Rent.query.with_entities(Rent.id).filter(Rent.rentcode == rentcode).one()[0]
    docfile.docfile_date = request.form.get('docfile_date')
    docfile.summary = request.form.get('dfsummary')
    docfile.docfile_text = request.form.get('xinput').replace("£", "&pound;")
    doctype = request.form.get('doc_type')
    docfile.doctype_id = \
        Typedoc.query.with_entities(Typedoc.id).filter(Typedoc.desc == doctype).one()[0]
    docfile.out_in = 0 if request.form.get('out_in') == "in" else 1
    db.session.add(docfile)
    db.session.commit()
    id_ = docfile.id
    source_html = docfile.docfile_text
    output_filename = "{}-{}.pdf".format(docfile.summary, str(docfile.docfile_date))
    convert_html_to_pdf(source_html, output_filename)

    return id_


def post_formletter(id, action):
    if action == "edit":
        formletter = Formletter.query.get(id)
    else:
        formletter = Formletter()
    formletter.code = request.form.get("code")
    formletter.summary = request.form.get("summary")
    formletter.subject = request.form.get("subject")
    formletter.block = request.form.get("block")
    formletter.bold = request.form.get("bold")
    doctype = request.form.get("doc_type")
    formletter.doctype_id = \
        Typedoc.query.with_entities(Typedoc.id).filter \
            (Typedoc.desc == doctype).one()[0]
    template = request.form.get("template")
    formletter.template_id = \
        Template.query.with_entities(Template.id).filter \
            (Template.code == template).one()[0]
    db.session.add(formletter)
    db.session.commit()
    id_ = formletter.id

    return id_


def post_emailaccount(id, action):
    if action == "edit":
        emailacc = Emailaccount.query.get(id)
    else:
        emailacc = Emailaccount()
    emailacc.smtp_server = request.form.get("smtp_server")
    emailacc.smtp_port = request.form.get("smtp_port")
    emailacc.smtp_timeout = request.form.get("smtp_timeout")
    emailacc.smtp_debug = request.form.get("smtp_debug")
    emailacc.smtp_tls = request.form.get("smtp_tls")
    emailacc.smtp_user = request.form.get("smtp_user")
    emailacc.smtp_password = request.form.get("smtp_password")
    emailacc.smtp_sendfrom = request.form.get("smtp_sendfrom")
    emailacc.imap_server = request.form.get("imap_server")
    emailacc.imap_port = request.form.get("imap_port")
    emailacc.imap_tls = request.form.get("imap_tls")
    emailacc.imap_user = request.form.get("imap_user")
    emailacc.imap_password = request.form.get("imap_password")
    emailacc.imap_sentfolder = request.form.get("imap_sentfolder")
    emailacc.imap_draftfolder = request.form.get("imap_draftfolder")
    db.session.add(emailacc)
    db.session.commit()
    id_ = emailacc.id

    return id_


def post_headrent(id, action):
    if action == "edit":
        headrent = Headrent.query.get(id)
    else:
        headrent = Agent()
    headrent.agdetails = request.form.get("agdetails")
    db.session.add(headrent)
    commit_to_database()
    id_ = headrent.id

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
    landlord.landlordname = request.form.get("name")
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
    db.session.commit()
    id_ = landlord.id
    return id_


def post_lease(id, action):
    if action == "new":
        # new lease:
        lease = Lease()
    else:
        lease = Lease.query.get(id)
    lease.term = request.form.get("term")
    lease.startdate = request.form.get("startdate")
    lease.startrent = request.form.get("startrent")
    lease.info = request.form.get("info")
    lease.upliftdate = request.form.get("upliftdate")
    lease.impvaluek = request.form.get("impvaluek")
    lease.rentcap = request.form.get("rentcap")
    lease.lastvalue = request.form.get("lastvalue")
    lease.last_value_date = request.form.get("lastvaluedate")
    lease.rent_id = request.form.get("rent_id")
    uplift_type = request.form.get("uplift_type")
    lease.uplift_type_id = \
        Lease_uplift_type.query.with_entities(Lease_uplift_type.id).filter \
            (Lease_uplift_type.uplift_type == uplift_type).one()[0]
    db.session.add(lease)
    db.session.commit()
    id_ = lease.id

    return id_


def post_loan(id, action):
    if action == "edit":
        loan = Loan.query.get(id)
    else:
        loan = Loan()
    loan.code = request.form.get("loancode")
    loan.interest_rate = request.form.get("interest_rate")
    loan.end_date = request.form.get("end_date")
    frequency = request.form.get("frequency")
    loan.frequency = \
        Typefreq.query.with_entities(Typefreq.id).filter(Typefreq.freqdet == frequency).one()[0]
    advarr = request.form.get("advarr")
    loan.advarr_id = \
        Typeadvarr.query.with_entities(Typeadvarr.id).filter(Typeadvarr.advarrdet == advarr).one()[0]
    loan.lender = request.form.get("lender")
    loan.borrower = request.form.get("borrower")
    loan.notes = request.form.get("notes")
    # loan.val_date = request.form.get("val_date")
    # loan.valuation = request.form.get("valuation")
    db.session.add(loan)
    db.session.commit()
    id_ = loan.id

    return id_


def post_moneyaccount(id, action):
    if action == "edit":
        moneyacc = Money_account.query.get(id)
    else:
        moneyacc = Money_account()
    moneyacc.bankname = request.form.get("bankname")
    moneyacc.accname = request.form.get("accname")
    moneyacc.sortcode = request.form.get("sortcode")
    moneyacc.accnum = request.form.get("accnum")
    moneyacc.accdesc = request.form.get("accdesc")
    db.session.add(moneyacc)
    db.session.commit()
    id_ = moneyacc.id

    return id_


def post_moneyitem(id, action):
    if action == "edit":
        bankitem = Money_item.query.get(id)
    else:
        bankitem = Money_item()
    bankitem.num = request.form.get("num")
    bankitem.date = request.form.get("date")
    bankitem.amount = request.form.get("amount")
    bankitem.payer = request.form.get("payer")
    accdesc = request.form.get("accdesc")
    bankitem.bankacc_id = \
        Money_account.query.with_entities(Money_account.id).filter \
            (Money_account.accdesc == accdesc).one()[0]
    cleared = request.form.get("cleared")
    bankitem.cleared = 1 if cleared == "cleared" else 0
    cat = request.form.get("category")
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
    property.propaddr = request.form.get("propaddr")
    proptypedet = request.form.get("proptypedet")
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
    rental.propaddr = request.form.get("propaddr")
    rental.tenantname = request.form.get("tenantname")
    rental.rentpa = request.form.get("rentpa")
    rental.arrears = request.form.get("arrears")
    rental.startrentdate = request.form.get("startrentdate")
    if rental.astdate:
        rental.astdate = request.form.get("astdate")
    rental.lastgastest = request.form.get("lastgastest")
    rental.note = request.form.get("note")
    frequency = request.form.get("frequency")
    rental.freq_id = \
        Typefreq.query.with_entities(Typefreq.id).filter(Typefreq.freqdet == frequency).one()[0]
    advarr = request.form.get("advarr")
    rental.advarr_id = \
        Typeadvarr.query.with_entities(Typeadvarr.id).filter(Typeadvarr.advarrdet == advarr).one()[0]
    db.session.add(rental)
    db.session.commit()
    id_ = rental.id

    return id_

def postrentobj(id):
    if id > 0:
        # existing rent:
        rent = Rent.query.get(id)
        agent = Agent.query.filter(Agent.id == rent.agent_id).one_or_none()
    else:
        # new rent:
        rent = Rent()
        agent = Agent()

    actype = request.form.get("actype")
    rent.actype_id = \
        Typeactype.query.with_entities(Typeactype.id).filter(Typeactype.actypedet == actype).one()[0]
    advarr = request.form.get("advarr")
    rent.advarr_id = \
        Typeadvarr.query.with_entities(Typeadvarr.id).filter(Typeadvarr.advarrdet == advarr).one()[0]
    rent.arrears = request.form.get("arrears")

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
    rent.note = request.form.get("note")
    rent.price = request.form.get("price")
    rent.rentpa = request.form.get("rentpa")
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
    if id < 1:
        rent.rentcode = request.form.get("rentcode")
        id = rent.id
    else:
        db.session.commit()

    return redirect('/rent_object/{}'.format(id))


def post_upload():
    print(request.form)
    print(request.files)
    rentid = request.form.get("rentid")
    rentcode = request.form.get("rentcode")
    doctype = request.form.get("doc_type")
    digdate = request.form.get("dig_date")
    outin = request.form.get("out_in")
    uploaded_file = request.files.get('file')
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in ['.pdf', '.doc', '.docx', '.ods', '.odt', '.jpg', '.png', '.gif']:
            return "Invalid file suffix", 400
        elif file_ext in ['.jpg', '.png', '.gif'] and file_ext != validate_image(uploaded_file.stream):
            return "Invalid image", 400
        uploaded_file.save(os.path.join('uploads', filename))
        newdigfile = Digfile()
        newdigfile.doctype_id = \
            Typedoc.query.with_entities(Typedoc.id).filter(Typedoc.desc == doctype).one()[0]
        newdigfile.digfile_date = digdate
        newdigfile.summary = rentcode + '-' + filename
        newdigfile.rent_id = rentid
        newdigfile.out_in = 0 if outin == "out" else 1
        newdigfile.digdata = uploaded_file.read()
        db.session.add(newdigfile)
        db.session.commit()
        return '', 204
    else:
        flash('No filename!')
        return redirect(request.url)

