import json
from flask import request
from datetime import date
from dateutil.relativedelta import relativedelta
from app.dao.agent import get_agent_id
from app.dao.headrent import get_headrent, get_headrent_row, get_headrents, get_recent_searches, \
    get_most_recent_search, post_headrent, \
    save_search
from app.dao.landlord import get_landlord_id
from app.main.common import inc_date_m
from app.dao.common import get_idlist_recent, commit_to_database
from app.main.functions import strToDec
from app.main.rent import get_paidtodate, get_rent_gale
from app.models import Agent, Headrent
from app.modeltypes import AdvArr, Freqs, HrStatuses, SaleGrades, Tenures
from sqlalchemy import func


def append_headrents_next_rent_date(headrents):
    for headrent in headrents:
        headrent.nextrentdate = inc_date_m(headrent.lastrentdate, headrent.freq_id, headrent.datecode_id, 1)
    return headrents


def create_new_headrent():
    # create new headrent function not yet built, so return any id:
    return 23


def mget_headrent(headrent_id):
    headrent = get_headrent(headrent_id)
    headrent.status = HrStatuses.get_name(headrent.status_id)
    headrent.tenuredet = Tenures.get_name(headrent.tenure_id)
    headrent.advarrdet = AdvArr.get_name(headrent.advarr_id)
    headrent.paidtodate = get_paidtodate(headrent.advarrdet, headrent.arrears, headrent.datecode_id, headrent.freq_id,
                                         headrent.lastrentdate, headrent.rentpa)
    headrent.nextrentdate = inc_date_m(headrent.lastrentdate, headrent.freq_id, headrent.datecode_id, 1)
    headrent.rent_gale = get_rent_gale(headrent.nextrentdate, headrent.freq_id, headrent.rentpa)

    return headrent


# def mget_headrents_default():
#     filtr = [Headrent.status_id == 1]
#     fdict = {'code': '', 'address': '', 'agent': '', 'status': ['active'],
#              'nextrentdate': date.today() + relativedelta(days=30)}
#     headrents = mget_headrents_with_status(filtr)
#     headrents = append_headrents_next_rent_date(headrents)
#
#     return fdict, headrents


def mget_headrents_dict():
    return {'rentcode': request.form.get('rentcode') or '',
            'address': request.form.get('address') or '',
            'agent': request.form.get('agent') or '',
            'status': request.form.getlist('status') or ['active'],
            # Work in progress - request.args.get('date') is the date selected by the user when clicking on a date in
            # the table. Currently this overwrites the date in the search field, which may not always be suitable
            'nextrentdate': request.form.get('nextrentdate')
                            or date.today() + relativedelta(days=30)}


def mget_headrents_filter():
    filtr = []
    fdict = mget_headrents_dict()
    if fdict.get('rentcode'):
        filtr.append(Headrent.code.startswith([fdict.get('rentcode')]))
    if fdict.get('address'):
        filtr.append(Headrent.propaddr.ilike('%{}%'.format(fdict.get('address'))))
    if fdict.get('agent'):
        filtr.append(Agent.detail.ilike('%{}%'.format(fdict.get('agent'))))
    if fdict.get('status') and fdict.get('status') != ["all statuses"]:
        ids = []
        for i in range(len(fdict.get('status'))):
            ids.append(HrStatuses.get_id(fdict.get('status')[i]))
            filtr.append(Headrent.status_id.in_(ids))
    if fdict.get('nextrentdate'):
        filtr.append(func.mjinn.next_rent_date(Headrent.id, 2) <= fdict.get('nextrentdate'))
        # filtr.append(Headrent.get_next_rent_date() <= fdict.get('nextrentdate'))

    return fdict, filtr


def mget_headrents_from_recent():
    filtr, list = mget_headrents_recent_filter()
    recent_search = get_most_recent_search()
    fdict = json.loads(recent_search.dict) if recent_search else {'rentcode': '', 'address': '', 'agent': '', 'status': ['active'],
             'nextrentdate': date.today() + relativedelta(days=30)}
    headrents = mget_headrents_with_status(filtr)
    headrents = append_headrents_next_rent_date(headrents)
    return fdict, sorted(headrents, key=lambda o: list.index(o.id))


def mget_headrents_from_search():
    fdict, filtr = mget_headrents_filter()
    # We save the search dict to the recent_search table. This calls a commit so must be done before we get the
    # headrents. If we commit in between eager loading the headrents and rendering the template, sqlalchemy will
    # have to make a trip to the database to load each headrent in the template
    mpost_save_search(fdict)
    headrents = mget_headrents_with_status(filtr)
    headrents = append_headrents_next_rent_date(headrents)
    return fdict, headrents


def mget_headrents_recent_filter():
    list = get_idlist_recent("recent_headrents")
    filtr =[Headrent.id.in_(list)]
    return filtr, list


def mget_headrents_with_status(filtr):
    headrents = get_headrents(filtr)
    for headrent in headrents:
        headrent.status = HrStatuses.get_name(headrent.status_id)
    return headrents


def mget_recent_searches():
    recent_searches = get_recent_searches()
    for recent_search in recent_searches:
        fdict = json.loads(recent_search.dict)
        recent_search.full_dict = fdict
        recent_search.rentcode = recent_search.full_dict.get('rentcode')
        recent_search.address = recent_search.full_dict.get('address')
        recent_search.agent = recent_search.full_dict.get('agent')
        recent_search.nextrentdate = recent_search.full_dict.get('nextrentdate')
        recent_search.status = recent_search.full_dict.get('status')
    return recent_searches


def mpost_save_search(fdict, desc=""):
    save_search(fdict, desc)


def update_headrent(headrent_id):
    headrent = get_headrent_row(headrent_id)
    headrent.advarr_id = request.form.get("advarr")
    headrent.agent_id = get_agent_id("agent")
    headrent.arrears = strToDec(request.form.get("arrears"))
    headrent.code = request.form.get("rentcode")
    # we need code to generate datecode_id from lastrentdate with user choosing sequence:
    # headrent.datecode_id = int(request.form.get("datecode_id"))
    headrent.freq_id = Freqs.get_id(request.form.get("frequency"))
    headrent.lastrentdate = request.form.get("lastrentdate")
    headrent.reference = request.form.get("reference")
    headrent.rentpa = strToDec(request.form.get("rentpa"))
    headrent.salegrade_id = request.form.get("salegrade")
    headrent.source = request.form.get("source")
    headrent.status_id = request.form.get("status")
    headrent.tenantname = request.form.get("tenantname")
    headrent.tenure_id = request.form.get("tenure")
    post_headrent(headrent)


def update_landlord(headrent_id, landlord_id):
    headrent = get_headrent_row(headrent_id)
    headrent.landlord_id = landlord_id
    post_headrent(headrent)


def update_note(headrent_id, note):
    headrent = get_headrent_row(headrent_id)
    headrent.note = note
    post_headrent(headrent)


def update_propaddr(headrent_id, propaddr):
    headrent = get_headrent_row(headrent_id)
    headrent.propaddr = propaddr
    post_headrent(headrent)
