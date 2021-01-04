from app import db
from flask import request
from sqlalchemy import desc, func
from app.main.functions import commit_to_database
from app.models import Agent, Headrent, Landlord, Typeadvarr, Typefreq, Typestatus, Typetenure\


def get_headrents():
    statusdets = [value for (value,) in Typestatus.query.with_entities(Typestatus.statusdet).all()]
    statusdets.insert(0, "all statuses")
    headrents = Headrent.query.join(Typestatus).outerjoin(Agent).with_entities(Agent.agdetails, Headrent.id,
                                                                               Headrent.hrcode, Headrent.rentpa,
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
    headrent = \
        Headrent.query \
            .join(Landlord) \
            .outerjoin(Agent) \
            .join(Typeadvarr) \
            .join(Typefreq) \
            .join(Typestatus) \
            .join(Typetenure) \
            .with_entities(Headrent.id, Headrent.hrcode, Headrent.arrears, Headrent.datecode, Headrent.lastrentdate,
                           Headrent.propaddr, Headrent.rentpa, Headrent.reference, Headrent.note, Headrent.source,
                           Landlord.landlordname, Agent.agdetails, Typeadvarr.advarrdet, Typefreq.freqdet,
                           Typestatus.statusdet, Typetenure.tenuredet,
                           # the following function takes id, rentype (1 for Rent or 2 for Headrent) and periods
                           func.mjinn.next_rent_date(Headrent.id, 2, 1).label('nextrentdate')) \
            .filter(Headrent.id == id) \
            .one_or_none()

    return headrent


def post_headrent(id):
    if id == 0:
        headrent = Headrent()
        headrent.id = 0
    else:
        headrent = Headrent.query.get(id)
    headrent.agdetails = request.form.get("agdetails")
    db.session.add(headrent)
    commit_to_database()
