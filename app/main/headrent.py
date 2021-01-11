from app import db
from flask import request
from sqlalchemy import desc, func
from app.main.common import get_postvals_toid
from app.main.functions import commit_to_database, strToDec
from app.models import Agent, Headrent, Landlord, Typeadvarr, Typefreq, Typestatus, Typetenure\


def get_headrents():
    statusdets = [value for (value,) in Typestatus.query.with_entities(Typestatus.statusdet).all()]
    statusdets.insert(0, "all statuses")
    headrents = Headrent.query.join(Typestatus).outerjoin(Agent).with_entities(Agent.detail, Headrent.id,
                                                                               Headrent.code, Headrent.rentpa,
                                                                               Headrent.arrears, Headrent.freq_id,
                                                                               Headrent.lastrentdate,
                                                                               Headrent.propaddr,
                                                                               func.mjinn.next_date(
                                                                                   Headrent.lastrentdate,
                                                                                   Headrent.freq_id, 1).label(
                                                                                   'nextrentdate'),
                                                                               Typestatus.statusdet).limit(100).all()
    return headrents, statusdets


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
                .join(Typestatus) \
                .join(Typetenure) \
                .with_entities(Headrent.id, Headrent.code, Headrent.arrears, Headrent.datecode, Headrent.lastrentdate,
                               Headrent.propaddr, Headrent.rentpa, Headrent.reference, Headrent.note, Headrent.source,
                               Landlord.landlordname, Agent.detail, Typeadvarr.advarrdet, Typefreq.freqdet,
                               Typestatus.statusdet, Typetenure.tenuredet,
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
    postvals_toid = get_postvals_toid()
    # we need the post values as class id generated for the actual combobox values:
    headrent.advarr_id = postvals_toid["advarr"]
    headrent.agent_id = postvals_toid["agent"]
    headrent.arrears = strToDec(request.form.get("arrears"))
    # we may write code later to generate datecode from lastrentdate!:
    headrent.code = request.form.get("rentcode")
    headrent.datecode = request.form.get("datecode")
    headrent.freq_id = postvals_toid["frequency"]
    headrent.landlord_id = postvals_toid["landlord"]
    headrent.lastrentdate = request.form.get("lastrentdate")
    headrent.note = request.form.get("note")
    headrent.reference = request.form.get("reference")
    headrent.rentpa = strToDec(request.form.get("rentpa"))
    headrent.salegrade_id = postvals_toid["salegrade"]
    headrent.source = request.form.get("source")
    headrent.status_id = postvals_toid["status"]
    headrent.tenantname = request.form.get("tenantname")
    headrent.tenure_id = postvals_toid["tenure"]
    db.session.add(headrent)
    db.session.flush()
    _id = headrent.id
    db.session.commit()

    return _id
