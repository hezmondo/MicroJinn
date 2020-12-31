import json
from app import db
from flask import request
from sqlalchemy import func
from app.main.common import get_idlist_recent
from app.main.functions import commit_to_database, dateToStr, strToDate, strToDec

from app.models import Agent, Charge, Chargetype, Extmanager, Extrent, Jstore, Landlord, \
    Manager, Pr_filter, Property, Rent, Typeactype, Typeadvarr, Money_account, Typedeed, Typefreq, \
    Typemailto, Typeprdelivery, Typeproperty, Typesalegrade, Typestatus, Typetenure, User, Emailaccount


def get_rentobjs(action, id):
    # get filter dictionary and filtered rent objects
    qfilter = []
    # simple filter dictionary for home page
    dict_basic = {
        "rentcode": "",
        "agentdetails": "",
        "propaddr": "",
        "source": "",
        "tenantname": ""
    }
    # more complex filter dictionary for queries and payrequest pages
    dict_plus = {
        "actype": ["all actypes"],
        "agentmailto": "include",
        "arrears": "",
        "charges": "include",
        "emailable": "include",
        "enddate": "",
        "landlord": ["all landlords"],
        "prdelivery": ["all prdeliveries"],
        "rentpa": "",
        "rentperiods": "",
        "runsize": "",
        "salegrade": ["all salegrades"],
        "status": ["all statuses"],
        "tenure": ["all tenures"]
    }
    filterdict = dict_basic if action in ("basic", "external") else {**dict_basic, **dict_plus}
    if action == "load":
        # load predefined filter dictionary from jstore
        jdict = Jstore.query.with_entities(Jstore.content).filter(Jstore.id == id).one_or_none()[0]
        jdict = json.loads(jdict)
        for key, value in jdict.items():
            filterdict[key] = value
        print ("filterdict after load")
    # for home page on "get"" visit we load the last 30 rents visited by this user
    if action == "basic" and request.method == "GET":
        id_list = get_idlist_recent("recent_rents")
        qfilter = [Rent.id.in_(id_list)]
    else:
        # now we construct advanced sqlalchemy filter using this filter dictionary
        qfilter, filterdict = get_qfilter(filterdict, action)
        print("filterdict after qfilter done")
        print(filterdict)
    if action == "save":
        # save this filter dictionary in either jstore or pr_filter
        print("filterdict during save")
        print(filterdict)
        jname = request.form.get("filtername")
        j_id = \
            Jstore.query.with_entities(Jstore.id).filter \
                (Jstore.code == jname).one_or_none()
        if j_id:
            j_id = j_id[0]
            jstore = Jstore.query.get(j_id)
            jstore.code = jname
            jstore.content = json.dumps(filterdict)
            db.session.commit()
        else:
            jstore = Jstore()
            jstore.code = jname
            jstore.content = json.dumps(filterdict)
            db.session.add(jstore)
        db.session.commit()

    # now get rent objects data using this filter
    rentprops = get_rentobjs_data(qfilter, action, 100)

    return filterdict, rentprops


def get_qfilter(filterdict, action):
    # first get filter values submitted from home or queries page and insert them into the dictionary
    if request.method == "POST":
        for key, value in filterdict.items():
            if key in ("actype", "landlord", "prdelivery", "salegrade", "status", "tenure"):
                actval = request.form.getlist(key)
            else:
                actval = request.form.get(key)
            print(key, actval)
            filterdict[key] = actval
    print(filterdict)
    filter = []
    # now iterate through all key values - this should surely be capable of refactoring?
    for key, value in filterdict.items():
        if key == "rentcode" and value and value != "":
            if action == "external":
                filter.append(Extrent.rentcode.startswith([value]))
            else:
                filter.append(Rent.rentcode.startswith([value]))
        elif key == "agentdetails" and value and value != "":
            if action == "external":
                filter.append(Extrent.agentdetails.ilike('%{}%'.format(value)))
            else:
                filter.append(Agent.agdetails.ilike('%{}%'.format(value)))
        elif key == "propaddr" and value and value != "":
            if action == "external":
                filter.append(Extrent.propaddr.ilike('%{}%'.format(value)))
            else:
                filter.append(Property.propaddr.ilike('%{}%'.format(value)))
        elif key == "source" and value and value != "":
            if action == "external":
                filter.append(Extrent.source.ilike('%{}%'.format(value)))
            else:
                filter.append(Rent.source.ilike('%{}%'.format(value)))
        elif key == "tenantname" and value and value != "":
            if action == "external":
                filter.append(Extrent.tenantname.ilike('%{}%'.format(value)))
            else:
                filter.append(Rent.tenantname.ilike('%{}%'.format(value)))
        elif key == "actype":
            if value and value != "" and value != [] and value != ["all actypes"]:
                filter.append(Typeactype.actypedet.in_(value))
            else: filterdict[key] = ["all actypes"]
        elif key == "agentmailto":
            if value and value == "exclude":
                filter.append(Rent.mailto_id.notin_(1, 2))
            elif key == "agentmailto" and value and value == "only":
                filter.append(Rent.mailto_id.in_(1, 2))
            else: filterdict[key] = "include"
        elif key == "arrears" and value and value != "":
            filter.append(Rent.arrears == strToDec('{}'.format(value)))
        # I will get to this when I do
        # elif key == "charges" and value == "exclude":
        #     filter.append(Rent.mailto_id.notin_(1, 2))
        # elif key == "charges" and value == "only":
        #     filter.append(Rent.mailto_id.in_(1, 2))
        # elif key == "emailable" and value == "exclude":
        #     filter.append(Rent.mailto_id.notin_(1, 2))
        # elif key == "emailable" and value == "only":
        #     filter.append(Rent.mailto_id.in_(1, 2))
        elif key == "enddate" and value and value != "":
            filter.append(Rent.lastrentdate <= strToDate('{}'.format(value)))
        elif key == "landlord":
            if value and value != "" and value != [] and value != ["all landlords"]:
                filter.append(Landlord.landlordname.in_(value))
            else: filterdict[key] = ["all landlords"]
        elif key == "prdelivery":
            if value and value != "" and value != [] and value != ["all prdeliveries"]:
                filter.append(Typeprdelivery.prdeliverydet.in_(value))
            else: filterdict[key] = ["all prdeliveries"]

        elif key == "rentpa" and value and value != "":
            filter.append(Rent.rentpa == strToDec('{}'.format(value)))
        elif key == "rentperiods" and value and value != "":
            filter.append(Rent.rentpa == strToDec('{}'.format(value)))
        elif key == "salegrade":
            if value and value != "" and value != "list" and value != [] and value != ["all salegrades"]:
                filter.append(Typesalegrade.salegradedet.in_('{}'.format(value)))
            else:
                filterdict[key] = ["all salegrades"]
        elif key == "status":
            if value and value != "" and value != [] and value != ["all statuses"]:
                filter.append(Typestatus.statusdet.in_(value))
            else:
                filterdict[key] = ["all statuses"]

        elif key == "tenure":
            if value and value != "" and value != [] and value != ["all tenures"]:
                filter.append(Typetenure.tenuredet.in_(value))
            else:
                filterdict[key] = ["all tenures"]

    return filter, filterdict


def get_rentobjs_data(qfilter, action, runsize):
    if action == "basic":
        # simple search of main rents submitted from home page
        rentobjs = \
            Property.query \
                .join(Rent) \
                .outerjoin(Agent) \
                .with_entities(Rent.id, Agent.agdetails, Rent.arrears, Rent.freq_id, Rent.lastrentdate,
                               # the following function takes id, rentype (1 for Rent or 2 for Headrent) and periods
                               func.mjinn.next_rent_date(Rent.id, 1, 1).label('nextrentdate'),
                               Property.propaddr, Rent.rentcode, Rent.rentpa, Rent.source, Rent.tenantname) \
                .filter(*qfilter).order_by(Rent.rentcode).limit(runsize).all()

    elif action == "external":
        # simple search of external rents submitted from home page - not yet completed
        rentobjs = \
            Extrent.query \
            .join(Extmanager) \
            .with_entities(Extrent.id, Extrent.rentcode, Extrent.propaddr, Extrent.tenantname, Extrent.owner,
                           Extrent.rentpa, Extrent.arrears, Extrent.lastrentdate, Extrent.source, Extrent.status,
                           Extmanager.codename, Extrent.agentdetails) \
            .filter(*qfilter).order_by(Extrent.rentcode).limit(runsize).all()

    else:
        # advanced search submitted from queries page
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
                    .filter(*qfilter).order_by(Rent.rentcode).limit(runsize).all()

    return rentobjs
