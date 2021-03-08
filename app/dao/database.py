import json
import logging

from flask_login import current_user
from sqlalchemy import exc
from werkzeug.exceptions import abort

from app import db

dbLogger = logging.getLogger("dbLogger")


def commit_to_database():
    """A shared function to make a commit to the database and
       handle exceptions if encountered"""
    dbLogger.info('Committing changes to db...')
    try:
        db.session.commit()
    except AssertionError as err:
        db.session.rollback()
        abort(409, err)
    except (exc.IntegrityError) as err:
        db.session.rollback()
        abort(409, err.orig)
    except Exception as err:
        db.session.rollback()
        abort(500, err)


def pop_idlist_recent(type, id):
    try:
        id_list = json.loads(getattr(current_user, type))
    except (AttributeError, TypeError, ValueError):
        id_list = [1, 2, 3]
    if id in id_list:
        id_list.remove(id)
    id_list.insert(0, id)
    if len(id_list) > 15:
        id_list.pop()
    setattr(current_user, type, json.dumps(id_list))
    commit_to_database()