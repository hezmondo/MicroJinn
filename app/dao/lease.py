from app import db
from sqlalchemy import select
from sqlalchemy.orm import contains_eager, load_only, joinedload
from app.dao.database import commit_to_database
from app.models import Lease, LeaseExt, LeaseRel, LeaseUpType, Rent


def dget_leasep(lease_id, rent_id):
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


def dget_lease(lease_id):
    return db.session.get(Lease, lease_id)


def dget_lease_exts(filtr):
    stmt = select(LeaseExt).join(Lease).join(Rent) \
        .options(load_only('date', 'value'),
               joinedload('lease').joinedload('rent').load_only('rentcode'))

    return db.session.execute(stmt.filter(*filtr)).unique().scalars().all()


def dget_lease_relvals(ids):
    return db.session.execute(select(LeaseRel.relativity).where(LeaseRel.unexpired.in_(ids))).all()


def dget_lease_rent(rent_id):
    return db.session.execute(select(Lease).filter_by(rent_id=rent_id)).scalar_one()


def dget_leases(lfilter):
    stmt = select(Lease).join(Rent).join(LeaseUpType).options(load_only(Lease.id, Lease.info, Lease.start_date,
                  Lease.term, Lease.uplift_date), joinedload('rent').load_only(Rent.rentcode),
                  joinedload('LeaseUpType').load_only(LeaseUpType.years, LeaseUpType.method, LeaseUpType.value))

    return db.session.execute(stmt.filter(*lfilter)).scalars().all()


def dget_leaseval_data(filtr):  # get lease and rent data for lease extension valuation and quotations
    stmt = select(Lease) \
        .options(load_only(Lease.info, Lease.rent_cap, Lease.rent_id, Lease.sale_value_k, Lease.start_date,
                           Lease.start_rent, Lease.term, Lease.uplift_date),
                 joinedload('LeaseUpType').load_only(LeaseUpType.method, LeaseUpType.value, LeaseUpType.years),
                 joinedload('rent').load_only(Rent.freq_id, Rent.rentcode, Rent.rentpa))

    return db.session.execute(stmt.filter(*filtr)).scalar_one_or_none()


def dget_methods():
    return db.session.execute(select(LeaseUpType.method).distinct()).scalars().all()


def dget_uplift_id(method, value, years):
    return db.session.execute(select(LeaseUpType.id).
        where(LeaseUpType.method==method, LeaseUpType.value==value, LeaseUpType.years==years)) \
        .scalar_one_or_none()


def dpost_lease(lease, uplift_type):
    if uplift_type:
        uplift_type.lease_up_type.append(lease)
        db.session.add(uplift_type)
    else:
        db.session.add(lease)
    commit_to_database()
