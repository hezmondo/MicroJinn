from app import db
from flask import request
from sqlalchemy import desc, func
from app.main.common import get_combo_id
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
    if id == 0:
        headrent =  Headrent()
        headrent.id = 0
    if request.method == "POST":
        headrent =  post_headrent(headrent)
    else:
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


def post_headrent(headrent):
    headrent.hrcode = request.form.get("hrcode")
    headrent.rentpa = request.form.get("rentpa")
    headrent.arrears = request.form.get("arrears")
    headrent.lastrentdate = request.form.get("lastrentdate")
    headrent.datecode = request.form.get("datecode")
    headrent.source = request.form.get("source")
    headrent.reference = request.form.get("reference")
    headrent.note = request.form.get("note")
    headrent.landlord = request.form.get("landlord")
    headrent.agent = request.form.get("agent")
    advarr = request.form.get("advarr")
    headrent.advarr_id = get_combo_id("advarr", advarr)
    frequency = request.form.get("frequency")
    headrent.freq_id = get_combo_id("frequency", frequency)
    landlord = request.form.get("landlord")
    headrent.landlord_id = get_combo_id("landlord", landlord)
    status = request.form.get("source")
    headrent.status = get_combo_id("status", status)
    tenure = request.form.get("tenure")
    headrent.tenure_id = get_combo_id("tenure", tenure)
    db.session.add(headrent)
    commit_to_database()
    headrent = Headrent.query.filter(Headrent.agdetails == agdet).first()
