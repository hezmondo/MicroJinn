import sqlalchemy
from app import db
from datetime import date
from sqlalchemy import func, select
from app.dao.database import commit_to_database
from app.models import Lease, LeaseRel, LeaseUpType, Rent


def dbget_lease(lease_id, rent_id):
    if lease_id != 0:
        lease = \
            Lease.query.join(Rent) \
                .join(LeaseUpType) \
                .with_entities(Lease.id, Rent.rentcode, Lease.term, Lease.start_date, Lease.start_rent, Lease.info,
                               Lease.uplift_date, LeaseUpType.uplift_type, Lease.value_date, Lease.value,
                               Lease.sale_value_k, Lease.rent_id, Lease.rent_cap) \
                .filter(Lease.id == lease_id).one_or_none()
    else:
        lease = \
            Lease.query.join(Rent) \
                .join(LeaseUpType) \
                .with_entities(Lease.id, Rent.rentcode, Lease.term, Lease.start_date, Lease.start_rent, Lease.info,
                               Lease.uplift_date, LeaseUpType.uplift_type, Lease.value_date, Lease.value,
                               Lease.sale_value_k, Lease.rent_id, Lease.rent_cap) \
                .filter(Lease.rent_id == rent_id).one_or_none()
    uplift_types = [value for (value,) in LeaseUpType.query.with_entities(LeaseUpType.uplift_type).all()]

    return lease, uplift_types


def dbget_leaseval_data(filtr):     # get lease and rent data for lease extension valuation and quotations
    return db.session.query(Lease).join(Rent).join(LeaseUpType) \
            .with_entities(Lease.id, Lease.info,Lease.rent_cap, Lease.rent_id, Lease.sale_value_k, Lease.start_date,
                           Lease.start_rent, Lease.term, Lease.uplift_date, Lease.value, Lease.value_date,
                           LeaseUpType.method, LeaseUpType.uplift_value, LeaseUpType.years,
                           Rent.freq_id, Rent.rentcode, Rent.rentpa) \
                .filter(*filtr).one_or_none()


def dbget_lease_relvals(ids):
    return db.session.execute(select(LeaseRel.relativity).where(LeaseRel.unexpired.in_(ids))).all()


def dbget_lease_row(lease_id):
    return Lease.query.get(lease_id)


def dbget_lease_row_rent(rent_id):
    return db.session.execute(select(Lease).filter_by(rent_id=rent_id)).scalar_one()


def dbget_leasedata(rent_id, gr_rate, calc_date):
    resultproxy = db.session.execute(sqlalchemy.text("CALL lex_valuation(:a, :b, :c)"),
                     params={"a": rent_id, "b": gr_rate, "c": calc_date})
    leasedata = [dict(row) for row in resultproxy][0]
    commit_to_database()

    return leasedata


def dbget_leases(lfilter):
    leases = Lease.query \
        .join(Rent) \
        .join(LeaseUpType) \
        .with_entities(Rent.rentcode, Lease.id, Lease.info,
                        func.mjinn.lex_unexpired(Lease.id, date.today()).label('unexpired'),
                        Lease.term, Lease.uplift_date, LeaseUpType.uplift_type) \
        .filter(*lfilter).limit(60).all()
    uplift_types = [value for (value,) in LeaseUpType.query.with_entities(LeaseUpType.uplift_type).all()]
    uplift_types.insert(0, "all uplift types")

    return leases, uplift_types


def dbget_uplift_type_id(uplift_type):
    uplift_type_id = \
        LeaseUpType.query.with_entities(LeaseUpType.id) \
            .filter(LeaseUpType.uplift_type == uplift_type).one()[0]

    return uplift_type_id


def dbpost_lease(lease):
    db.session.add(lease)
    commit_to_database()


