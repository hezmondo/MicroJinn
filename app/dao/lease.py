from app import db
from sqlalchemy import select
from sqlalchemy.orm import load_only, joinedload
from app.dao.database import commit_to_database
from app.models import Lease, LeaseRel, LeaseUpType, Rent


def dbget_lease(lease_id, rent_id):
    filtr = []
    if lease_id != 0:
        filtr.append(Lease.id == lease_id)
    else:
        filtr.append(Lease.rent_id == rent_id)
    stmt = select(Lease) \
        .options(load_only(Lease.id, Lease.info, Lease.rent_cap, Lease.rent_id, Lease.sale_value_k, Lease.start_date,
                           Lease.start_rent, Lease.term, Lease.uplift_date, Lease.uplift_id),
                 joinedload('LeaseUpType').load_only(LeaseUpType.id, LeaseUpType.method, LeaseUpType.value,
                                                     LeaseUpType.years),
                 joinedload('rent').load_only(Rent.rentcode))

    return db.session.execute(stmt.filter(*filtr)).scalar_one_or_none()


def dbget_leaseval_data(filtr):  # get lease and rent data for lease extension valuation and quotations
    stmt = select(Lease) \
        .options(load_only(Lease.info, Lease.rent_cap, Lease.rent_id, Lease.sale_value_k, Lease.start_date,
                           Lease.start_rent, Lease.term, Lease.uplift_date, Lease.value, Lease.value_date),
                 joinedload('LeaseUpType').load_only(LeaseUpType.method, LeaseUpType.value, LeaseUpType.years),
                 joinedload('rent').load_only(Rent.freq_id, Rent.rentcode, Rent.rentpa))

    return db.session.execute(stmt.filter(*filtr)).scalar_one_or_none()


def dbget_lease_relvals(ids):

    return db.session.execute(select(LeaseRel.relativity).where(LeaseRel.unexpired.in_(ids))).all()


def dbget_lease_row(lease_id):

    return Lease.query.get(lease_id)


def dbget_lease_row_rent(rent_id):

    return db.session.execute(select(Lease).filter_by(rent_id=rent_id)).scalar_one()


def dbget_leases(lfilter):
    stmt = select(Lease) \
        .options(load_only(Lease.id, Lease.info, Lease.start_date, Lease.term, Lease.uplift_date),
                 joinedload('LeaseUpType').load_only(LeaseUpType.uplift_date),
                 joinedload('rent').load_only(Rent.rentcode))

    return db.session.execute(stmt.filter(*lfilter)).all()


def dbget_methods():
    return db.session.execute(select(LeaseUpType.method)).all()


def dbpost_lease(lease):
    db.session.add(lease)
    commit_to_database()
