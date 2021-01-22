from app import db
from flask import request
from sqlalchemy import func
from app.dao.common import get_postvals_id
from app.dao.functions import strToDec
from app.models import Agent, Headrent, Landlord, Typeadvarr, Typefreq, Type_status_hr, Typetenure\


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
            filter.append(Type_status_hr.hr_status.in_(status))

    headrents = \
        Headrent.query \
            .join(Type_status_hr) \
            .outerjoin(Agent) \
            .with_entities(Agent.detail, Headrent.id,Headrent.code, Headrent.rentpa, Headrent.arrears,
                           Headrent.freq_id, Headrent.lastrentdate, Headrent.propaddr, Type_status_hr.hr_status,
                   func.mjinn.next_date(Headrent.lastrentdate,Headrent.freq_id, 1).label('nextrentdate')) \
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
                .join(Typeadvarr) \
                .join(Typefreq) \
                .join(Type_status_hr) \
                .join(Typetenure) \
                .with_entities(Headrent.id, Headrent.code, Headrent.arrears, Headrent.datecode, Headrent.lastrentdate,
                               Headrent.propaddr, Headrent.rentpa, Headrent.reference, Headrent.note, Headrent.source,
                               Landlord.landlordname, Agent.detail, Typeadvarr.advarrdet, Typefreq.freqdet,
                               Type_status_hr.hr_status, Typetenure.tenuredet,
                               # the following function takes id, rentype (1 for Rent or 2 for Headrent) and periods
                               func.mjinn.next_rent_date(Headrent.id, 2, 1).label('nextrentdate')) \
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
    # we may write code later to generate datecode from lastrentdate!:
    headrent.code = request.form.get("rentcode")
    headrent.datecode = request.form.get("datecode")
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
