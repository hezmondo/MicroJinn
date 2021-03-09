from app import db
from flask import request
from sqlalchemy import func

from app.dao.database import commit_to_database
from app.main.common import get_postvals_id, inc_date_m
from app.main.functions import strToDec
from app.models import Agent, Headrent, Landlord, TypeAdvArr, TypeFreq, TypeStatusHr, TypeTenure\


def get_headrents():
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
        if status and status != "" and status != [] and status != ['all statuses']:
            filter.append(TypeStatusHr.hr_status.in_(status))

    headrents = \
        Headrent.query \
            .join(TypeStatusHr) \
            .outerjoin(Agent) \
            .with_entities(Agent.detail, Headrent.id, Headrent.code, Headrent.datecode_id, Headrent.rentpa,
                           Headrent.arrears, Headrent.freq_id, Headrent.lastrentdate, Headrent.propaddr,
                           TypeStatusHr.hr_status,
                           func.mjinn.inc_date_m(Headrent.lastrentdate, Headrent.freq_id,
                                      Headrent.datecode_id, 1).label('nextrentdate')) \
            .filter(*filter) \
            .limit(100).all()

    return filterdict, headrents


def get_headrent(id):
    if request.method == "POST":
        id =  post_headrent(id)
    if id != 0:
        headrent = \
            Headrent.query \
                .join(Landlord) \
                .outerjoin(Agent) \
                .join(TypeAdvArr) \
                .join(TypeFreq) \
                .join(TypeStatusHr) \
                .join(TypeTenure) \
                .with_entities(Headrent.id, Headrent.code, Headrent.arrears, Headrent.datecode_id, Headrent.freq_id,
                               Headrent.lastrentdate, Headrent.propaddr, Headrent.rentpa, Headrent.reference,
                               Headrent.note, Headrent.source, Landlord.name, Agent.detail, TypeAdvArr.advarrdet,
                               TypeFreq.freqdet, TypeStatusHr.hr_status, TypeTenure.tenuredet) \
                .filter(Headrent.id == id) \
                .one_or_none()
    else:
        headrent =  Headrent()
        headrent.id = 0

    return headrent


def post_headrent(id):
    headrent = Headrent.query.get(id)
    postvals_id = get_postvals_id()
    # we need the post values as class id generated for the actual combobox values:
    headrent.advarr_id = postvals_id["advarr"]
    headrent.agent_id = postvals_id["agent"]
    headrent.arrears = strToDec(request.form.get("arrears"))
    # we need code to generate datecode from lastrentdate with user choosing sequence:
    headrent.code = request.form.get("rentcode")
    headrent.datecode_id = int(request.form.get("datecode_id"))
    headrent.freq_id = postvals_id["frequency"]
    headrent.landlord_id = postvals_id["landlord"]
    headrent.lastrentdate = request.form.get("lastrentdate")
    headrent.note = request.form.get("note")
    headrent.reference = request.form.get("reference")
    headrent.rentpa = strToDec(request.form.get("rentpa"))
    headrent.salegrade_id = postvals_id["salegrade"]
    headrent.source = request.form.get("source")
    headrent.status_id = postvals_id["status"]
    headrent.tenantname = request.form.get("tenantname")
    headrent.tenure_id = postvals_id["tenure"]
    db.session.add(headrent)
    db.session.flush()
    _id = headrent.id
    db.session.commit()

    return _id


def post_headrent_agent_update(agent_id, rent_id):
    if rent_id != 0:
        headrent = Headrent.query.get(rent_id)
        if agent_id != 0:
            headrent.agent_id = agent_id
        else:
            headrent.agent_id = None
    commit_to_database()
