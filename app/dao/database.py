import logging

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


def rollback_database():
    dbLogger.info('Rolling back db...')
    db.session.rollback()


