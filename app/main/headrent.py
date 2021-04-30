from flask import request
from datetime import date
from dateutil.relativedelta import relativedelta
from app.dao.agent import get_agent_id
from app.dao.headrent import get_headrent, get_headrent_row, get_headrents, post_headrent
from app.dao.landlord import get_landlord_id
from app.main.common import inc_date_m
from app.main.functions import strToDec
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


def mget_headrents_default():
    filtr = [Headrent.status_id == 1]
    fdict = {'code': '', 'address': '', 'agent': '', 'status': ['all statuses'], 'nextrentdate': date.today()}
    headrents = mget_headrents_with_status(filtr)

    return fdict, headrents


def mget_headrents_dict():
    return {'rentcode': request.form.get('rentcode') or '',
            'address': request.form.get('address') or '',
            'agent': request.form.get('agent') or '',
            'status': request.form.getlist('status') or ['active'],
            # Work in progress - request.args.get('date') is the date selected by the user when clicking on a date in
            # the table. Currently this overwrites the date in the search field, which may not always be suitable
            'nextrentdate': request.args.get('date') or request.form.get('nextrentdate')
                            or date.today() + relativedelta(days=50)}


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


def mget_headrents_from_search():
    fdict, filtr = mget_headrents_filter()
    headrents = mget_headrents_with_status(filtr)
    return fdict, headrents


def mget_headrents_with_status(filtr):
    headrents = get_headrents(filtr)
    for headrent in headrents:
        headrent.status = HrStatuses.get_name(headrent.status_id)
    return headrents


# def get_headrents_p():
#     filter = []
#     filterdict = {'code': '', 'address': '', 'agent': '', 'status': ['all statuses'], 'nextrentdate': date.today()}
#     if request.method == "POST":
#         rentcode = request.form.get("rentcode") or ""
#         filterdict['rentcode'] = rentcode
#         if rentcode:
#             filter.append(Headrent.code.startswith([rentcode]))
#         address = request.form.get("address") or ""
#         filterdict['address'] = address
#         if address:
#             filter.append(Headrent.propaddr.ilike('%{}%'.format(address)))
#         agent = request.form.get("agent") or ""
#         filterdict['agent'] = agent
#         if agent:
#             filter.append(Agent.detail.ilike('%{}%'.format(agent)))
#         status = request.form.getlist("status") or ["all statuses"]
#         if status and status != ["all statuses"]:
#             ids = []
#             for i in range(len(status)):
#                 ids.append(HrStatuses.get_id(status[i]))
#                 filter.append(Headrent.status_id.in_(ids))
#             filterdict['status'] = status
#     else:
#         filter.append(Headrent.status_id==1)
#     headrents = get_headrents(filter)
#     for headrent in headrents:
#         headrent.status = HrStatuses.get_name(headrent.status_id)
#
#     return filterdict, headrents


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
