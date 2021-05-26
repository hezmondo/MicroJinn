import json
from flask import request
from datetime import datetime
from app.dao.agent import get_agent_id
from app.dao.headrent import get_headrent, get_headrent_row, get_headrents, post_headrent
from app.main.common import inc_date_m, mpost_search
from app.dao.common import get_idlist_recent, get_recent_searches
from app.main.functions import strToDec
from app.main.rent import get_paidtodate, get_rent_gale
from app.models import Agent, Headrent
from app.modeltypes import AdvArr, Freqs, HrStatuses, Tenures
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
    return {'agent': request.form.get('agent') or '',
            'nextrentdate': request.form.get('nextrentdate') or '',
            'propaddr': request.form.get('propaddr') or '',
            'rentcode': request.form.get('rentcode') or '',
            'status': request.form.getlist('status') or ['active']}
    # dateToStrJson(date.today() + relativedelta(days=35))}


def mget_headrents_filter():
    filtr = []
    fdict = mget_headrents_dict()
    if fdict.get('rentcode'):
        filtr.append(Headrent.code.startswith([fdict.get('rentcode')]))
    if fdict.get('propaddr'):
        filtr.append(Headrent.propaddr.ilike('%{}%'.format(fdict.get('propaddr'))))
    if fdict.get('agent'):
        filtr.append(Agent.detail.ilike('%{}%'.format(fdict.get('agent'))))
    if fdict.get('status') and fdict.get('status') != ["all statuses"]:
        ids = []
        for i in range(len(fdict.get('status'))):
            ids.append(HrStatuses.get_id(fdict.get('status')[i]))
            filtr.append(Headrent.status_id.in_(ids))
    if fdict.get('nextrentdate') and fdict.get('nextrentdate') != '':
        filtr.append(func.mjinn.next_rent_date(Headrent.id, 2) <= fdict.get('nextrentdate'))

    return fdict, filtr


def mget_headrents_default():
    filtr = [Headrent.status_id == 1]
    fdict = {'rentcode': '', 'propaddr': '', 'agent': '', 'status': ['active'],
             'nextrentdate': ''}
    headrents = mget_headrents(filtr)

    return fdict, headrents


def mget_headrents_from_search():
    fdict, filtr = mget_headrents_filter()
    # If the search dictionary is not in the recent_search table we post it
    mpost_search(fdict, 'headrent')
    headrents = mget_headrents(filtr)
    return fdict, headrents


def mget_headrents_recent_filter():
    list = get_idlist_recent("recent_headrents")
    filtr = [Headrent.id.in_(list)]
    return filtr, list


def mget_recent_searches(type):
    recent_searches = get_recent_searches(type)
    for recent_search in recent_searches:
        fdict = json.loads(recent_search.dict)
        recent_search.full_dict = fdict
        recent_search.rentcode = fdict.get('rentcode')
        recent_search.propaddr = fdict.get('propaddr')
        recent_search.agent = fdict.get('agent')
        if fdict.get('nextrentdate') and fdict.get('nextrentdate') != '':
             recent_search.nextrentdate = datetime.strptime(fdict.get('nextrentdate'), '%Y-%m-%d').strftime("%d-%m-%Y")
        recent_search.status = fdict.get('status')
    return recent_searches


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
