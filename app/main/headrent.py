from flask import request
from app.dao.headrent import get_headrents
from app.main.common import get_hr_status, inc_date_m

from app.models import Agent, Headrent


def create_new_headrent():
    # create new headrent function not yet built, so return any id:
    return 23


def get_headrents_p():
    filter = []
    filterdict = {'rentcode': '', 'address': '', 'agent': '', 'status': 'all statuses'}
    if request.method == "POST":
        rentcode = request.form.get("rentcode") or ""
        filterdict['rentcode'] = rentcode
        if rentcode and rentcode != "":
            filter.append(Headrent.code.startswith([rentcode]))
        address = request.form.get("address") or ""
        filterdict['address'] = address
        if address and address != "":
            filter.append(Headrent.propaddr.ilike('%{}%'.format(address)))
        agent = request.form.get("agent") or ""
        filterdict['agent'] = agent
        if agent and agent != "":
            filter.append(Agent.detail.ilike('%{}%'.format(agent)))
        status = request.form.getlist("status") or ""
        filterdict['status'] = status
    #     have to work out how to do this

    headrents = get_headrents(filter)
    for headrent in headrents:
        headrent.nextrentdate = inc_date_m(headrent.lastrentdate, headrent.freq_id, headrent.datecode_id, 1)
        headrent.status = get_hr_status(headrent.status_id)
    return filterdict, headrents


