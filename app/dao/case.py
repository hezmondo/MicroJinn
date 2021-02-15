from app.models import Case
from app import db


def merge_case(case_details, case_nad, rent_id):
    case = Case()
    case.id = rent_id
    case.case_details = case_details
    case.case_nad = case_nad
    db.session.merge(case)