from app.models import Case
from app import db
from sqlalchemy import exists


def check_case_exists(rent_id):
    return db.session.query(exists().where(Case.id == rent_id)).scalar()


def add_case(case_details, case_nad, rent_id):
    case = Case()
    case.id = rent_id
    case.case_details = case_details
    case.case_nad = case_nad
    db.session.add(case)