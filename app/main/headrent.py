from flask import request
from app.dao.agent import get_agent_id
from app.dao.headrent import get_headrents, post_headrent
from app.dao.landlord import get_landlord_id
from app.main.common import get_advarr_id, get_freq_id, get_hr_status, get_tenure_id, get_salegrade_id, \
    get_status_id, inc_date_m
from app.main.functions import strToDec
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


def update_headrent(headrent_id):
    headrent = Headrent.query.get(headrent_id)
    headrent.advarr_id = get_advarr_id(request.form.get("advarr"))
    headrent.agent_id = get_agent_id("agent")
    headrent.arrears = strToDec(request.form.get("arrears"))
    headrent.code = request.form.get("rentcode")
    # we need code to generate datecode_id from lastrentdate with user choosing sequence:
    # headrent.datecode_id = int(request.form.get("datecode_id"))
    headrent.freq_id = get_freq_id('frequency')
    headrent.landlord_id = get_landlord_id(request.form.get("landlord"))
    headrent.lastrentdate = request.form.get("lastrentdate")
    headrent.note = request.form.get("note")
    headrent.reference = request.form.get("reference")
    headrent.rentpa = strToDec(request.form.get("rentpa"))
    headrent.salegrade_id = get_salegrade_id(request.form.get("salegrade"))
    headrent.source = request.form.get("source")
    headrent.status_id = get_status_id(request.form.get("status"))
    headrent.tenantname = request.form.get("tenantname")
    headrent.tenure_id = get_tenure_id(request.form.get("tenure"))
    post_headrent(headrent)

    return


