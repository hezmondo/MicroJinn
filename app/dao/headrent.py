from app import db
from flask import flash, redirect, url_for
from sqlalchemy.orm import joinedload, load_only
from app.dao.database import commit_to_database
from app.models import Agent, Headrent
from app.modeltypes import Freqs, Statuses


def create_new_headrent():
    # create new headrent function not yet built, so return any id:
    return 23


def get_agent_headrents(agent_id):
    return db.session.query(Headrent).filter_by(agent_id=agent_id).options(load_only('id', 'code', 'propaddr')).all()


def get_headrent(headrent_id):  # returns all Headrent member variables as a mutable dict
    if headrent_id == 0:
        # take the user to create new rent function:
        headrent_id = create_new_headrent()
    headrent = db.session.query(Headrent) \
        .filter_by(id=headrent_id).options(joinedload('agent').load_only('id', 'detail'),
                                       joinedload('landlord').load_only('name')) \
        .one_or_none()
    headrent.freqdet = Freqs.get_name(headrent.freq_id)
    if headrent is None:
        flash('Invalid rent code')
        return redirect(url_for('auth.login'))

    return headrent


def get_headrent_row(headrent_id):
    return Headrent.query.get(headrent_id)


def get_headrents(filter):
    headrents = \
            db.session.query(Headrent).join(Agent) \
            .options(load_only('id', 'code', 'arrears', 'datecode_id', 'freq_id', 'lastrentdate',
                               'propaddr', 'rentpa', 'source', 'status_id'),
                joinedload('agent').load_only('detail')) \
            .filter(*filter).order_by(Headrent.code).limit(50).all()
    for rent in headrents:
        rent.status = Statuses.get_name(rent.status_id)

    return headrents


def post_headrent(headrent):
    try:
        db.session.add(headrent)
        message = "Success! This headrent has been updated."
        commit_to_database()
    except Exception as ex:
        message = f"Update headrent failed. Error:  {str(ex)}"

    return message


# def post_headrent_agent_update(agent_id, rent_id):
#     message = ""
#     try:
#         if rent_id != 0:
#             headrent = Headrent.query.get(rent_id)
#             if agent_id != 0:
#                 headrent.agent_id = agent_id
#                 message = "Success! This headrent has been linked to a new agent. " \
#                           "Please review the rent\'s mail address."
#             else:
#                 headrent.agent_id = None
#                 message = "Success! This headrent no longer has an agent."
#         commit_to_database()
#     except Exception as ex:
#         message = f"Update headrent failed. Error:  {str(ex)}"
#
#     return message
