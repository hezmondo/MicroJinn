from datetime import datetime
from app import db
from app.models import PrArrearsMatrix, PrBatch, PrCharge, PrHistory, Rent
from app.modeltypes import PrDeliveryTypes
from app.dao.database import commit_to_database
from sqlalchemy import desc
from sqlalchemy.orm import load_only


def post_pr_batch(runcode, size, status, is_account):
    pr_batch = PrBatch(datetime=datetime.now(), code=runcode, size=size, status=status, is_account=is_account)
    db.session.add(pr_batch)
    # db.session.flush()
    # batch_id = pr_batch.id
    commit_to_database()
    return pr_batch


def add_pr_charge(pr_id, charge_id, case_created):
    pr_charge = PrCharge()
    pr_charge.id = pr_id
    pr_charge.charge_id = charge_id
    pr_charge.case_created = case_created
    db.session.add(pr_charge)


def add_pr_history(pr_history):
    db.session.add(pr_history)
    db.session.flush()
    return pr_history.id


def get_last_arrears_level(rent_id):
    return db.session.query(PrHistory.arrears_level).filter_by(rent_id=rent_id).order_by(-PrHistory.id).first()


def get_pr_charge(pr_id):
    return PrCharge.query.filter_by(id=pr_id).one_or_none()


def get_pr_block(pr_id):
    return db.session.query(PrHistory).filter_by(id=pr_id).with_entities(PrHistory.block).scalar()


def get_pr_file(pr_id):
    pr_file = PrHistory.query.join(Rent).with_entities(PrHistory.id, PrHistory.summary, PrHistory.block,
                                                       PrHistory.datetime, PrHistory.rent_date, PrHistory.total_due,
                                                       Rent.rentcode, Rent.id.label("rent_id")) \
        .filter(PrHistory.id == pr_id).one_or_none()
    return pr_file


def get_pr_history(rent_id):
    return PrHistory.query.filter_by(rent_id=rent_id).order_by(desc(PrHistory.datetime))


def get_pr_history_row(pr_id):
    return PrHistory.query.get(pr_id)


def get_recovery_info(suffix):
    recovery_info = db.session.query(PrArrearsMatrix).filter_by(suffix=suffix).options(load_only('arrears_clause',
                                                                                                 'recovery_charge',
                                                                                                 'create_case')).\
        one_or_none()
    arrears_clause = recovery_info.arrears_clause
    create_case = recovery_info.create_case
    recovery_charge = recovery_info.recovery_charge
    return arrears_clause, create_case, recovery_charge


def get_recovery_info_x(suffix):
    recovery_info = db.session.query(PrArrearsMatrix).filter_by(suffix=suffix).options(load_only('recovery_charge',
                                                                                                 'create_case')).\
        one_or_none()
    create_case = recovery_info.create_case
    recovery_charge = recovery_info.recovery_charge
    return create_case, recovery_charge


def post_updated_payrequest(block, pr_id):
    pr_history = PrHistory.query.get(pr_id)
    rent_id = pr_history.rent_id
    pr_history.block = block
    commit_to_database()
    return rent_id


def post_updated_payrequest_delivery(delivered, pr_file):
    rent_id = pr_file.rent_id
    pr_file.delivered = delivered
    commit_to_database()
    return rent_id


def prepare_new_pr_history_entry(pr_history_data, rent_id, method='email'):
    summary = pr_history_data.get('pr_code') + "-" + method + "-" + pr_history_data.get('mailaddr')[0:25]
    pr_history = PrHistory(block=pr_history_data.get('block').replace("£", "&pound;"), rent_id=rent_id,
                           summary=summary, datetime=datetime.now(),
                           rent_date=datetime.strptime(pr_history_data.get('rent_date'), '%Y-%m-%d'),
                           total_due=pr_history_data.get('tot_due'),
                           arrears_level=pr_history_data.get('new_arrears_level'),
                           delivery_method=PrDeliveryTypes.get_id(method), delivered=False)
    # TODO: We are not using the typeprdelivery table yet in any meaningful way
    #  - should we remove it and make delivery_method in pr_history a string column?
    #  - We'd have to hard code the method strings in any combodict filters
    # TODO: Add pending / delivered functionality
    return pr_history
