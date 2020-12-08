import json
import sqlalchemy
from app import db
from datetime import date
from dateutil.relativedelta import relativedelta
from flask import flash, redirect, url_for, request, session
from flask_login import current_user, login_required
from sqlalchemy import and_, asc, desc, extract, func, literal, or_, text
from app.main.common import get_combos_common
from app.main.functions import commit_to_database, dateToStr, strToDate, strToDec

from app.models import Agent, Charge, Chargetype, Extmanager, Extrent, Jstore, Landlord, Lease, Lease_uplift_type, \
    Manager, Property, Rent, Typeactype, Typeadvarr, Money_account, Typedeed, Typefreq, Typemailto, Typeprdelivery, \
    Typeproperty, Typesalegrade, Typestatus, Typetenure, User, Emailaccount


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


# leases
def get_lease(id):
    # id can be actual lease id or 0 (for new lease or for id unknown as coming from rent)
    action = request.args.get('action', "view", type=str)
    rentcode = request.args.get('rentcode', "DUMMY" , type=str)
    rentid = int(request.args.get('rentid', "0", type=str))
    lease_filter = []
    if id == 0 and action == "new":
        lease = {
            'id': 0,
            'rent_id': rentid,
            'rentcode': rentcode
        }
    else:
        if id == 0:
            lease_filter.append(Lease.rent_id == rentid)
        else:
            lease_filter.append(Lease.id == id)
        lease = \
            Lease.query.join(Rent).join(Lease_uplift_type).with_entities(Lease.id, Rent.rentcode, Lease.term,
                 Lease.startdate, Lease.startrent, Lease.info, Lease.upliftdate, Lease_uplift_type.uplift_type,
                 Lease.lastvaluedate, Lease.lastvalue, Lease.impvaluek, Lease.rent_id, Lease.rentcap) \
                .filter(*lease_filter).one_or_none()

    uplift_types = [value for (value,) in Lease_uplift_type.query.with_entities(Lease_uplift_type.uplift_type).all()]

    return action, lease, uplift_types


def get_leasedata(rent_id, fh_rate, gr_rate, new_gr_a, new_gr_b, yp_low, yp_high):
    resultproxy = db.session.execute(sqlalchemy.text("CALL lex_valuation(:a, :b, :c, :d, :e, :f, :g)"), params={"a": rent_id, "b": fh_rate, "c": gr_rate, "d": new_gr_a, "e": new_gr_b, "f": yp_low, "g": yp_high})
    leasedata = [{column: value for column, value in rowproxy.items()} for rowproxy in resultproxy][0]
    db.session.commit()

    return leasedata


def get_leases():
    lease_filter = []
    rcd = request.form.get("rentcode") or "all rentcodes"
    uld = request.form.get("upliftdays") or "all uplift dates"
    ult = request.form.get("uplift_type") or "all uplift types"
    if rcd and rcd != "all rentcodes":
        lease_filter.append(Rent.rentcode.ilike('%{}%'.format(rcd)))
    if uld and uld != "all uplift dates":
        enddate = date.today() + relativedelta(days='{}'.format(uld))
        lease_filter.append(Lease.upliftdate <= enddate)
    if ult and ult != "" and ult != "all uplift types":
        lease_filter.append(Lease_uplift_type.uplift_type.ilike('%{}%'.format(ult)) )

    leases = Lease.query.join(Rent).join(Lease_uplift_type).with_entities(Rent.rentcode, Lease.id, Lease.info,
              func.mjinn.lex_unexpired(Lease.id).label('unexpired'),
              Lease.term, Lease.upliftdate, Lease_uplift_type.uplift_type) \
        .filter(*lease_filter).limit(60).all()

    uplift_types = [value for (value,) in Lease_uplift_type.query.with_entities(Lease_uplift_type.uplift_type).all()]
    uplift_types.insert(0, "all uplift types")

    return leases, uplift_types, rcd, uld, ult


# properties
def get_property(id):
    property = Property.query.join(Typeproperty).with_entities(Property.id, Property.propaddr,
                   Typeproperty.proptypedet).filter(Property.id == id).one_or_none()
    proptypedets = [value for (value,) in Typeproperty.query.with_entities(Typeproperty.proptypedet).all()]

    return property, proptypedets


# rent object and associated queries
def get_rentobjs_basic(action):
    qfilterbasic = []
    if action == "view":
        id_list = get_idlist_recent("recent_rents")
        qfilterbasic.append(Rent.id.in_(id_list))
    agentdetails = request.form.get("agentdetails") or ""
    propaddr = request.form.get("propaddr") or ""
    rentcode = request.form.get("rentcode") or ""
    source = request.form.get("source") or ""
    tenantname = request.form.get("tenantname") or ""
    runsize = request.form.get("runsize") or 100
    if action == "external":
        if agentdetails and agentdetails != "":
            qfilterbasic.append(Extrent.agentdetails.ilike('%{}%'.format(agentdetails)))
        if propaddr and propaddr != "":
            qfilterbasic.append(Extrent.propaddr.ilike('%{}%'.format(propaddr)))
        if rentcode and rentcode != "":
            qfilterbasic.append(Extrent.rentcode.startswith([rentcode]))
        if source and source != "":
            qfilterbasic.append(Extrent.source.ilike('%{}%'.format(source)))
        if tenantname and tenantname != "":
            qfilterbasic.append(Extrent.tenantname.ilike('%{}%'.format(tenantname)))
        rentprops = getrentobjs_external(qfilterbasic, runsize)
    else:
        if agentdetails and agentdetails != "":
            qfilterbasic.append(Agent.agdetails.ilike('%{}%'.format(agentdetails)))
        if propaddr and propaddr != "":
            qfilterbasic.append(Property.propaddr.ilike('%{}%'.format(propaddr)))
        if rentcode and rentcode != "":
            qfilterbasic.append(Rent.rentcode.startswith([rentcode]))
        if source and source != "":
            qfilterbasic.append(Rent.source.ilike('%{}%'.format(source)))
        if tenantname and tenantname != "":
            qfilterbasic.append(Rent.tenantname.ilike('%{}%'.format(tenantname)))
        rentprops = getrentobjs_basic(qfilterbasic, runsize)

    return agentdetails, propaddr, rentcode, source, tenantname, rentprops


def get_rentobjs_plus(action, name):
    jname = name
    agentdetails = request.form.get("agentdetails") or ""
    propaddr = request.form.get("propaddr") or ""
    rentcode = request.form.get("rentcode") or ""
    source = request.form.get("source") or ""
    tenantname = request.form.get("tenantname") or ""
    enddate = request.form.get("enddate") or date.today() + relativedelta(days=45)
    runsize = request.form.get("runsize") or 100
    qfilter = []
    if agentdetails and agentdetails != "":
        qfilter.append(Agent.agdetails.ilike('%{}%'.format(agentdetails)))
    if propaddr and propaddr != "":
        qfilter.append(Property.propaddr.ilike('%{}%'.format(propaddr)))
    if rentcode and rentcode != "":
        qfilter.append(Rent.rentcode.startswith([rentcode]))
    if source and source != "":
        qfilter.append(Rent.source.ilike('%{}%'.format(source)))
    if tenantname and tenantname != "":
        qfilter.append(Rent.tenantname.ilike('%{}%'.format(tenantname)))
    if enddate and enddate != "":
        qfilter.append(func.mjinn.next_rent_date(Rent.id, 1, 1) < "{}".format(enddate))
    landlords, statusdets, tenuredets = get_queryoptions_common()
    actypedets, floads, options, prdeliveries, salegradedets = get_queryoptions_advanced()
    if request.method == "POST":
        jname = request.form.get("jname")
        actype = request.form.getlist("actype")
        arrears = request.form.get("arrears")
        landlord = request.form.getlist("landlord")
        prdelivery = request.form.getlist("prdelivery")
        rentpa = request.form.get("rentpa")
        rentperiods = request.form.get("rentperiods")
        salegrade = request.form.getlist("salegrade")
        status = request.form.getlist("status")
        tenure = request.form.getlist("tenure")
    else:
        returns = Jstore.query.with_entities(Jstore.content).filter(Jstore.name == jname)[0][0]
        print(returns)
        returns = json.loads(returns)
        agentdetails = returns["agd"]
        actype = returns["act"]
        arrears = returns["arr"]
        landlord = returns["lld"]
        prdelivery = returns["prd"]
        propaddr = returns["pop"]
        rentcode = returns["rcd"]
        rentpa = returns["rpa"]
        rentperiods = returns["rpd"]
        salegrade = returns["sal"]
        status = returns["sta"]
        source = returns["soc"]
        tenantname = returns["tna"]
        tenure = returns["ten"]
    if actype and actype != actypedets and actype[0] != "all actypes":
        qfilter.append(Typeactype.actypedet.in_(actype))
    if arrears and arrears != "":
        qfilter.append(text("Rent.arrears {}".format(arrears)))
    if landlord and landlord != landlords and landlord[0] != "all landlords":
        qfilter.append(Landlord.landlordname.in_(landlord))
    if prdelivery and prdelivery != prdeliveries and prdelivery != "":
        qfilter.append(Typeprdelivery.prdeliverydet.in_(prdelivery))
    if rentpa and rentpa != "":
        qfilter.append(text("Rent.rentpa {}".format(rentpa)))
    if rentperiods and rentperiods != "":
        qfilter.append(text("Rent.rentperiods {}".format(rentperiods)))
    if salegrade and salegrade != salegradedets and salegrade[0] != "all salegrades":
        qfilter.append(Typesalegrade.salegradedet.in_(salegrade))
    if status and status != statusdets and status[0] != "all statuses":
        qfilter.append(Typestatus.statusdet.in_(status))
    if tenure and tenure != tenuredets and tenure[0] != "all tenures":
        qfilter.append(Typetenure.tenuredet.in_(tenure))
    if action == "save":
        store = {}
        store["act"] = actype
        store["agd"] = agentdetails
        store["arr"] = arrears
        store["lld"] = landlord
        store["prd"] = prdelivery
        store["pop"] = propaddr
        store["rcd"] = rentcode
        store["rpa"] = rentpa
        store["rpd"] = rentperiods
        store["sal"] = salegrade
        store["soc"] = source
        store["sta"] = status
        store["tna"] = tenantname
        store["ten"] = tenure
        j_id = \
            Jstore.query.with_entities(Jstore.id).filter \
                (Jstore.name == jname).one()[0]
        if j_id:
            jstore = Jstore.query.get(j_id)
            jstore.name = jname
            jstore.content = json.dumps(store)
            db.session.commit()
        else:
            jstore = Jstore()
            jstore.name = jname
            jstore.content = json.dumps(store)
            db.session.add(jstore)
        db.session.commit()
    rentprops = getrentobjs_advanced(qfilter, runsize)

    return actype, agentdetails, arrears, enddate, jname, landlord, prdelivery, propaddr, rentcode, rentpa, \
           rentperiods, runsize, salegrade, source, status, tenantname, tenure, rentprops

def getrentobjs_basic(qfilter, runsize):
    rentobjs = \
        Property.query \
            .join(Rent) \
            .outerjoin(Agent) \
            .with_entities(Rent.id, Agent.agdetails, Rent.arrears, Rent.freq_id, Rent.lastrentdate,
                           # the following function takes id, rentype (1 for Rent or 2 for Headrent) and periods
                           func.mjinn.next_rent_date(Rent.id, 1, 1).label('nextrentdate'),
                           Property.propaddr, Rent.rentcode, Rent.rentpa, Rent.source, Rent.tenantname) \
            .filter(*qfilter) \
            .limit(runsize).all()

    return rentobjs


def getrentobjs_external(qfilter, runsize):
    rentobjs = \
        Extrent.query \
        .join(Extmanager) \
        .with_entities(Extrent.id, Extrent.rentcode, Extrent.propaddr, Extrent.tenantname, Extrent.owner,
                       Extrent.rentpa, Extrent.arrears, Extrent.lastrentdate, Extrent.source, Extrent.status,
                       Extmanager.codename, Extrent.agentdetails) \
        .filter(*qfilter) \
        .limit(runsize).all()

    return rentobjs


def getrentobjs_advanced(qfilter, runsize):
    rentobjs = \
        Property.query \
            .join(Rent) \
            .join(Landlord) \
            .outerjoin(Agent) \
            .outerjoin(Charge) \
            .join(Typeactype) \
            .join(Typeprdelivery) \
            .join(Typestatus) \
            .join(Typesalegrade) \
            .join(Typetenure) \
            .with_entities(Rent.id, Typeactype.actypedet, Agent.agdetails, Rent.arrears, Rent.lastrentdate,
                           # the following function takes id, rentype (1 for Rent or 2 for Headrent) and periods
                           func.mjinn.next_rent_date(Rent.id, 1, 1).label('nextrentdate'),
                           func.mjinn.tot_charges(Rent.id).label('totcharges'),
                           Landlord.landlordname, Property.propaddr, Rent.rentcode, Rent.rentpa, Rent.source, Rent.tenantname,
                           Typeprdelivery.prdeliverydet, Typesalegrade.salegradedet, Typestatus.statusdet,
                           Typetenure.tenuredet) \
            .filter(*qfilter) \
            .limit(runsize).all()

    return rentobjs


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


def get_combos_rentonly():
    # This function returns the list values for various comboboxes used only by rents
    actypedets = [value for (value,) in Typeactype.query.with_entities(Typeactype.actypedet).all()]
    deedcodes = [value for (value,) in Typedeed.query.with_entities(Typedeed.deedcode).all()]
    mailtodets = [value for (value,) in Typemailto.query.with_entities(Typemailto.mailtodet).all()]
    salegradedets = [value for (value,) in Typesalegrade.query.with_entities(Typesalegrade.salegradedet).all()]

    return actypedets, deedcodes, mailtodets, salegradedets


def get_queryoptions_common():
    # return options for common multiple choice controls in home page and queries page
    advarrdets, freqdets, landlords, statusdets, tenuredets = get_combos_common()
    landlords.insert(0, "all landlords")
    statusdets.insert(0, "all statuses")
    tenuredets.insert(0, "all tenures")

    return landlords, statusdets, tenuredets

def get_queryoptions_advanced():
    # return options for advanced multiple choice controls in home page and queries page
    actypedets, deedcodes, mailtodets, salegradedets = get_combos_rentonly()
    salegradedets.insert(0, "all salegrades")
    actypedets.insert(0, "all actypes")
    floads = [value for (value,) in Jstore.query.with_entities(Jstore.name).all()]
    prdeliveries = [value for (value,) in Typeprdelivery.query.with_entities(Typeprdelivery.prdeliverydet).all()]
    options = ("Include", "Exclude", "Only")

    return actypedets, floads, options, prdeliveries, salegradedets


def get_idlist_recent(recent_field):
    id_list = [1, 51, 101, 151, 201, 251, 301, 351, 401, 451, 501]
    id_list = json.loads(getattr(current_user, recent_field)) if getattr(current_user, recent_field) else id_list

    return id_list


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


def post_lease(id):
    rentid = int(request.form.get("rent_id"))
    # new lease for id 0, otherwise existing lease:
    if id == 0:
        lease = Lease()
        lease.id = 0
        lease.rent_id = rentid
        lease.startdate = "1991-01-01"
        lease.upliftdate = "1991-01-01"
        lease.lastvaluedate = "1991-01-01"
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
    lease.lastvaluedate = request.form.get("lastvaluedate")
    lease.rent_id = rentid
    uplift_type = request.form.get("uplift_type")
    lease.uplift_type_id = \
        Lease_uplift_type.query.with_entities(Lease_uplift_type.id).filter \
            (Lease_uplift_type.uplift_type == uplift_type).one()[0]
    print(request.form)
    db.session.add(lease)
    db.session.commit()

    return rentid


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