import json
from app import db
from flask import request, session
from sqlalchemy import func
from app.dao.common import get_idlist_recent
from app.dao.functions import strToDate, strToDec
from app.models import Agent, Charge, ManagerExt, RentExt, Jstore, Landlord, Property, Rent, TypeAcType, \
    TypeDoc, TypePrDelivery, TypeSaleGrade, TypeStatus, TypeTenure


def get_filters(type):
    filters = Jstore.query.filter(Jstore.type == type).all()

    return filters


def get_rent_s(action, filter_id):
    # collect doctypes to hold in session, as this is the first trip to the server
    session['doc_types'] = [value for (value,) in TypeDoc.query.with_entities(TypeDoc.desc).all()]
    # get filter dictionary and filtered rent objects
    qfilter = []
    # simple filter dictionary for home page
    dict_basic = {
        "rentcode": "",
        "agentdetail": "",
        "propaddr": "",
        "source": "",
        "tenantname": "",
        "filtertype": "rentprop"
    }
    # more complex filter dictionary for filter and payrequest pages
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
        jdict = Jstore.query.with_entities(Jstore.content).filter(Jstore.id == filter_id).one_or_none()[0]
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
        post_rent__filter(filterdict)
    # now get filtered rent objects for this filter
    rent_s = get_rent_s_data(qfilter, action, 100)
    if action == 'basic':
        rent_s = sorted(rent_s, key=lambda o: id_list.index(o.id))
    return filterdict, rent_s


def get_qfilter(filterdict, action):
    # first get filter values submitted from home or filter page and insert them into the dictionary
    if request.method == "POST":
        for key, value in filterdict.items():
            if key in ("actype", "landlord", "prdelivery", "salegrade", "status", "tenure"):
                actval = request.form.getlist(key)
            else:
                actval = request.form.get(key) or ""
            print(key, actval)
            filterdict[key] = actval
    print(filterdict)
    filter = []
    # now iterate through all key values - this can surely be refactored?
    for key, value in filterdict.items():
        if key == "rentcode" and value and value != "":
            if action == "external":
                filter.append(RentExt.rentcode.startswith([value]))
            else:
                filter.append(Rent.rentcode.startswith([value]))
        elif key == "agentdetail" and value and value != "":
            if action == "external":
                filter.append(RentExt.agentdetail.ilike('%{}%'.format(value)))
            else:
                filter.append(Agent.detail.ilike('%{}%'.format(value)))
        elif key == "propaddr" and value and value != "":
            if action == "external":
                filter.append(RentExt.propaddr.ilike('%{}%'.format(value)))
            else:
                filter.append(Property.propaddr.ilike('%{}%'.format(value)))
        elif key == "source" and value and value != "":
            if action == "external":
                filter.append(RentExt.source.ilike('%{}%'.format(value)))
            else:
                filter.append(Rent.source.ilike('%{}%'.format(value)))
        elif key == "tenantname" and value and value != "":
            if action == "external":
                filter.append(RentExt.tenantname.ilike('%{}%'.format(value)))
            else:
                filter.append(Rent.tenantname.ilike('%{}%'.format(value)))
        elif key == "actype":
            if value and value != "" and value != [] and value != ["all actypes"]:
                filter.append(TypeAcType.actypedet.in_(value))
            else: filterdict[key] = ["all actypes"]
        elif key == "agentmailto":
            if value and value == "exclude":
                filter.append(Rent.mailto_id.notin_(1, 2))
            elif key == "agentmailto" and value and value == "only":
                filter.append(Rent.mailto_id.in_(1, 2))
            else: filterdict[key] = "include"
        # elif key == "arrears" and value and value != "":
        #     filter.append(Rent.arrears == strToDec('{}'.format(value)))
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
                filter.append(Landlord.name.in_(value))
            else: filterdict[key] = ["all landlords"]
        elif key == "prdelivery":
            if value and value != "" and value != [] and value != ["all prdeliveries"]:
                filter.append(TypePrDelivery.prdeliverydet.in_(value))
            else: filterdict[key] = ["all prdeliveries"]
        # elif key == "rentpa" and value and value != "":
        #     filter.append(Rent.rentpa == strToDec('{}'.format(value)))
        # elif key == "rentperiods" and value and value != "":
        #     filter.append(Rent.rentpa == strToDec('{}'.format(value)))
        elif key == "salegrade":
            if value and value != "" and value != "list" and value != [] and value != ["all salegrades"]:
                filter.append(TypeSaleGrade.salegradedet.in_('{}'.format(value)))
            else:
                filterdict[key] = ["all salegrades"]
        elif key == "status":
            if value and value != "" and value != [] and value != ["all statuses"]:
                filter.append(TypeStatus.statusdet.in_(value))
            else:
                filterdict[key] = ["all statuses"]
        elif key == "tenure":
            if value and value != "" and value != [] and value != ["all tenures"]:
                filter.append(TypeTenure.tenuredet.in_(value))
            else:
                filterdict[key] = ["all tenures"]

    return filter, filterdict


def get_rent_s_data(qfilter, action, runsize):
    if action == "basic":
        # simple search of views rents submitted from home page
        rent_s = \
            Property.query \
                .join(Rent) \
                .outerjoin(Agent) \
                .with_entities(Rent.id, Agent.detail, Rent.arrears, Rent.freq_id, Rent.lastrentdate,
                               # the following function takes id, rentype (1 for Rent or 2 for Headrent) and periods
                               func.mjinn.next_rent_date(Rent.id, 1, 1).label('nextrentdate'),
                               Property.propaddr, Rent.rentcode, Rent.rentpa, Rent.source, Rent.tenantname) \
                .filter(*qfilter).limit(runsize).all()

    elif action == "external":
        # simple search of external rents submitted from home page - not yet completed
        rent_s = \
            RentExt.query \
            .join(ManagerExt) \
            .with_entities(RentExt.id, RentExt.rentcode, RentExt.propaddr, RentExt.tenantname, RentExt.owner,
                           RentExt.rentpa, RentExt.arrears, RentExt.lastrentdate, RentExt.source, RentExt.status,
                           ManagerExt.codename, RentExt.agentdetail) \
            .filter(*qfilter).order_by(RentExt.rentcode).limit(runsize).all()

    else:
        # advanced search submitted from filter page
        rent_s = \
                Property.query \
                    .join(Rent) \
                    .join(Landlord) \
                    .outerjoin(Agent) \
                    .outerjoin(Charge) \
                    .join(TypeAcType) \
                    .join(TypePrDelivery) \
                    .join(TypeStatus) \
                    .join(TypeSaleGrade) \
                    .join(TypeTenure) \
                    .with_entities(Rent.id, TypeAcType.actypedet, Agent.detail, Rent.arrears, Rent.lastrentdate,
                                   # the following function takes id, rentype (1 for Rent or 2 for Headrent) and periods
                                   func.mjinn.next_rent_date(Rent.id, 1, 1).label('nextrentdate'),
                                   func.mjinn.tot_charges(Rent.id).label('totcharges'),
                                   Landlord.name, Property.propaddr, Rent.rentcode, Rent.rentpa, Rent.source, Rent.tenantname,
                                   TypePrDelivery.prdeliverydet, TypeSaleGrade.salegradedet, TypeStatus.statusdet,
                                   TypeTenure.tenuredet) \
                    .filter(*qfilter).order_by(Rent.rentcode).limit(runsize).all()

    return rent_s


def post_rent__filter(filterdict):
    # save this filter dictionary in jstore
    print("filterdict during save")
    print(filterdict)
    jname = request.form.get("filtername")
    jtype = request.form.get("filtertype")
    if jtype == "payrequest":
        jtype = 1
    elif jtype == "rentprop":
        jtype = 2
    else:
        jtype = 3
    j_id = \
        Jstore.query.with_entities(Jstore.id).filter \
            (Jstore.code == jname).one_or_none()
    if j_id:
        j_id = j_id[0]
        jstore = Jstore.query.get(j_id)
    else:
        jstore = Jstore()
    jstore.type = jtype
    jstore.code = jname
    jstore.content = json.dumps(filterdict)
    db.session.add(jstore)
    db.session.commit()

