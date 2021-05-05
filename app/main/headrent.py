import json
from flask import request
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from app.dao.agent import get_agent_id
from app.dao.headrent import add_new_recent_search, delete, get_headrent, get_headrent_row, get_headrents, \
    get_recent_searches, get_recent_searches_asc, get_most_recent_search, post_headrent
from app.main.common import inc_date_m
from app.dao.common import get_idlist_recent, commit_to_database
from app.main.functions import dateToStr, strToDec, strToDate
from app.main.rent import get_paidtodate, get_rent_gale
from app.models import Agent, Headrent
from app.modeltypes import AdvArr, Freqs, HrStatuses, SaleGrades, Tenures
from sqlalchemy import func


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


def mget_headrents(filtr):
    headrents = get_headrents(filtr)
    for headrent in headrents:
        headrent.status = HrStatuses.get_name(headrent.status_id)
        headrent.nextrentdate = inc_date_m(headrent.lastrentdate, headrent.freq_id, headrent.datecode_id, 1)
    return headrents


def mget_headrents_dict():
    return {'rentcode': request.form.get('rentcode') or '',
            'address': request.form.get('address') or '',
            'agent': request.form.get('agent') or '',
            'status': request.form.getlist('status') or ['active'],
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

    return fdict, filtr


def mget_headrents_from_recent():
    filtr, list = mget_headrents_recent_filter()
    recent_search = get_most_recent_search()
    fdict = json.loads(recent_search.dict) if recent_search else {'rentcode': '', 'address': '', 'agent': '', 'status': ['active'],
             'nextrentdate': date.today() + relativedelta(days=30)}
    headrents = mget_headrents(filtr)
    return fdict, sorted(headrents, key=lambda o: list.index(o.id))


def mget_headrents_from_search():
    fdict, filtr = mget_headrents_filter()
    # If the search dictionary is not in recent_search table we post it
    mpost_search(fdict)
    headrents = mget_headrents(filtr)
    return fdict, headrents


def mget_headrents_recent_filter():
    list = get_idlist_recent("recent_headrents")
    filtr = [Headrent.id.in_(list)]
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
        recent_search.rentcode = fdict.get('rentcode')
        recent_search.address = fdict.get('address')
        recent_search.agent = fdict.get('agent')
        recent_search.nextrentdate = datetime.strptime(fdict.get('nextrentdate'), '%Y-%m-%d').strftime("%d-%m-%Y")
        recent_search.status = fdict.get('status')
    return recent_searches


def mpost_search(fdict):
    recent_searches = get_recent_searches_asc()
    # convert fdict into a string, as this is how it is saved in the db
    str_dict = json.dumps(fdict)
    # If the search dict already exists in the table we do nothing
    for recent_search in recent_searches:
        if str_dict == recent_search.dict:
            return
    # If there are already 6 records in the table we delete the oldest
    if len(recent_searches) >= 6:
        first_record = recent_searches[0]
        delete(first_record)
    add_new_recent_search(fdict)
    commit_to_database()


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
