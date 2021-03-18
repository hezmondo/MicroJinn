import json
from flask import request
from app.main.common import get_advarrdet, get_idlist_recent, get_prdelivery_id, get_status_id, inc_date_m
from app.main.functions import strToDate
from app.main.rent import get_propaddr
from app.dao.rent import get_rent_sdata, post_rent__filter
from app.models import Agent, RentExternal, Jstore, Landlord, Property, Rent


def get_filters(type):
    filters = Jstore.query.filter(Jstore.type == type).all()

    return filters


def get_rent_s(action, filter_id):
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
    rent_s = get_rent_sdata(qfilter, action, 50)
    if action != 'external':
        for rent in rent_s:
            rent.advarrdet = get_advarrdet(rent.advarr_id)
            rent.detail = rent.agent.detail if hasattr(rent.agent, 'detail') else 'no agent'
            rent.nextrentdate = inc_date_m(rent.lastrentdate, rent.freq_id, rent.datecode_id, 1)
            rent.propaddr = get_propaddr(rent.id)

    # TODO: Repeated if statement - This can be cleaned up
    if action == 'basic' and request.method == "GET":
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
                filter.append(RentExternal.rentcode.startswith([value]))
            else:
                filter.append(Rent.rentcode.startswith([value]))
        elif key == "agentdetail" and value and value != "":
            if action == "external":
                filter.append(RentExternal.agentdetail.ilike('%{}%'.format(value)))
            else:
                filter.append(Rent.Agent.detail.ilike('%{}%'.format(value)))
        elif key == "propaddr" and value and value != "":
            if action == "external":
                filter.append(RentExternal.propaddr.ilike('%{}%'.format(value)))
        elif key == "source" and value and value != "":
            if action == "external":
                filter.append(RentExternal.source.ilike('%{}%'.format(value)))
            else:
                filter.append(Rent.source.ilike('%{}%'.format(value)))
        elif key == "tenantname" and value and value != "":
            if action == "external":
                filter.append(RentExternal.tenantname.ilike('%{}%'.format(value)))
            else:
                filter.append(Rent.tenantname.ilike('%{}%'.format(value)))
        elif key == "actype":
            if value and value != "" and value != [] and value != ["all actypes"]:
                filter.append()
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
                filter.append(Rent.Landlord.name.in_(value))
            else: filterdict[key] = ["all landlords"]
        elif key == "prdelivery":
            if value and value != "" and value != [] and value != ["all prdeliveries"]:
                list = []
                for item in value:
                    item = get_prdelivery_id(item)
                filter.append(Rent.prdelivery_id.in_(value))
            else: filterdict[key] = ["all prdeliveries"]
        # elif key == "rentpa" and value and value != "":
        #     filter.append(Rent.rentpa == strToDec('{}'.format(value)))
        # elif key == "rentperiods" and value and value != "":
        #     filter.append(Rent.rentpa == strToDec('{}'.format(value)))
        elif key == "salegrade":
            if value and value != "" and value != "list" and value != [] and value != ["all salegrades"]:
                filter.append("")
            else:
                filterdict[key] = ["all salegrades"]
        elif key == "status":
            if value and value != "" and value != [] and value != ["all statuses"]:
                filter.append()
            else:
                filterdict[key] = ["all statuses"]
        elif key == "tenure":
            if value and value != "" and value != [] and value != ["all tenures"]:
                filter.append()
            else:
                filterdict[key] = ["all tenures"]

    return filter, filterdict
