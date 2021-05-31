from app import db
from datetime import datetime
from app.models import Action
import json


# agent - id = 1, pay request - id = 2, rent - id = 3
# alert = 1, info = 0
def add_action(actiontype_id, alert, detail, link, link_vars):
    # first check to see if the action detail is in the db. If it is, we will replace the old action
    # with the updated one
    action = db.session.query(Action).filter_by(detail=detail).one_or_none()
    if action:
        db.session.delete(action)
    action = Action(datetime=datetime.now(), actiontype_id=actiontype_id, detail=detail, link=link,
                    link_vars=json.dumps(link_vars), alert=alert)
    db.session.add(action)
    db.session.flush()


def delete_action(action_id):
    Action.query.filter_by(id=action_id).delete()
    db.session.commit()


def resolve_action(action_id):
    action = get_action(action_id)
    action.alert = False
    detail = action.detail
    action.detail = detail + '- Resolved'
    db.session.commit()


def get_action(action_id):
    return Action.query.get(action_id)


def get_actions():
    return db.session.query(Action).filter().all()


