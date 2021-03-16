from app import db
from flask import flash, redirect, request, url_for
from sqlalchemy.orm import joinedload, load_only
from app.dao.database import commit_to_database
from app.main.common import get_postvals_id
from app.main.functions import strToDec
from app.models import Headrent


def create_new_headrent():
    # create new headrent function not yet built, so return any id:
    return 23


def get_headrent(headrent_id):  # returns all Headrent member variables as a mutable dict
    if headrent_id == 0:
        # take the user to create new rent function:
        headrent_id = create_new_headrent()
    headrent = db.session.query(Headrent) \
        .filter_by(id=headrent_id).options(joinedload('agent').load_only('id', 'detail'),
                                       joinedload('landlord').load_only('name'),
                                       joinedload('typefreq').load_only('freqdet'),
                                       joinedload('typetenure').load_only('tenuredet')) \
        .one_or_none()
    if headrent is None:
        flash('Invalid rent code')
        return redirect(url_for('auth.login'))

    return headrent


def get_headrents(filter):
    headrents = \
            db.session.query(Headrent) \
            .options(load_only('id', 'code', 'arrears', 'datecode_id', 'freq_id', 'lastrentdate',
                               'propaddr', 'rentpa', 'source'),
                joinedload('agent').load_only('detail')) \
            .filter(*filter).order_by(Headrent.code).limit(50).all()

    return headrents


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
    message = ""
    try:
        if rent_id != 0:
            headrent = Headrent.query.get(rent_id)
            if agent_id != 0:
                headrent.agent_id = agent_id
                message = "Success! This headrent has been linked to a new agent. " \
                          "Please review the rent\'s mail address."
            else:
                headrent.agent_id = None
                message = "Success! This headrent no longer has an agent."
        commit_to_database()
    except Exception as ex:
        message = f"Update headrent failed. Error:  {str(ex)}"
    return message
