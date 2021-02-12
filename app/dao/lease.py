import sqlalchemy
from app import db
from datetime import date
from dateutil.relativedelta import relativedelta
from flask import request
from sqlalchemy import func
from app.dao.functions import commit_to_database, moneyToStr
from app.models import Lease, LeaseUpType, Rent


def get_lease(lease_id):
    rent_id = int(request.args.get('rent_id', "0", type=str))
    rentcode = request.args.get('rentcode', "ABC1", type=str)
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
    if not lease:
        lease = {
                    'id': 0,
                    'rent_id': rent_id,
                    'rentcode': rentcode
                }
    uplift_types = [value for (value,) in LeaseUpType.query.with_entities(LeaseUpType.uplift_type).all()]
    return lease, uplift_types


def get_leasedata(rent_id, fh_rate, gr_rate, gr_new, yp_val):
    resultproxy = db.session.execute(sqlalchemy.text("CALL lex_valuation(:a, :b, :c, :d, :e)"), params={"a": rent_id, "b": fh_rate, "c": gr_rate, "d": gr_new, "e": yp_val})
    leasedata = [{column: value for column, value in rowproxy.items()} for rowproxy in resultproxy][0]
    db.session.commit()

    return leasedata


def get_leases():
    lfilter = []
    rcd = request.form.get("rentcode") or "all rentcodes"
    uld = request.form.get("upliftdays") or ""
    ult = request.form.get("uplift_type") or "all uplift types"
    if rcd and rcd != "all rentcodes":
        lfilter.append(Rent.rentcode.ilike('%{}%'.format(rcd)))
    if uld and uld != "":
        uld = int(uld)
        enddate = date.today() + relativedelta(days=uld)
        lfilter.append(Lease.uplift_date <= enddate)
    if ult and ult != "" and ult != "all uplift types":
        lfilter.append(LeaseUpType.uplift_type.ilike('%{}%'.format(ult)))

    leases = Lease.query.join(Rent).join(LeaseUpType).with_entities(Rent.rentcode, Lease.id, Lease.info,
                                                                    func.mjinn.lex_unexpired(Lease.id).label('unexpired'),
                                                                    Lease.term, Lease.uplift_date, LeaseUpType.uplift_type) \
        .filter(*lfilter).limit(60).all()

    uplift_types = [value for (value,) in LeaseUpType.query.with_entities(LeaseUpType.uplift_type).all()]
    uplift_types.insert(0, "all uplift types")

    return leases, uplift_types, rcd, uld, ult


def get_lease_variables(rent_id):
    fh_rate = request.form.get('fh_rate')
    gr_rate = request.form.get('gr_rate')
    gr_new = request.form.get('gr_new')
    yp_val = request.form.get('yp_val')

    leasedata = get_leasedata(rent_id, fh_rate, gr_rate, gr_new, yp_val)
    impval = leasedata["impvalk"] * 1000
    unimpval = leasedata["impvalk"] * leasedata["realty"] * 10 if leasedata["realty"] > 0 else impval
    lease_variables = {'#unexpired#': str(leasedata["unexpired"]) if leasedata else "11.11",
                       '#rent_code#': leasedata["rent_code"] if leasedata else "some rentcode",
                       '#relativity#': str(leasedata["realty"]) if leasedata else "some relativity",
                       '#tot_val#': moneyToStr(leasedata["totval"] if leasedata else 55555.55, pound=True),
                       '#unimpvalue#': moneyToStr(unimpval if leasedata else 555.55, pound=True),
                       '#impvalue#': moneyToStr(impval if leasedata else 555.55, pound=True),
                       '#leq200R#': moneyToStr(leasedata["leq200R"] if leasedata else 55555.55, pound=True),
                       '#leq200P#': moneyToStr(leasedata["leq200P"] if leasedata else 55555.55, pound=True),
                       '#gr_new#': moneyToStr(leasedata["gr_new"] if leasedata else 555.55, pound=True)
                       }

    return leasedata, lease_variables


def post_lease(lease_id):
    rent_id = int(request.form.get("rent_id"))
    # new lease for id 0, otherwise existing lease:
    if lease_id == 0:
        lease = Lease()
        lease.id = 0
        lease.rent_id = rent_id
        lease.start_date = "1991-01-01"
        lease.uplift_date = "1991-01-01"
        lease.value_date = "1991-01-01"
    else:
        lease = Lease.query.get(lease_id)
    lease.term = request.form.get("term")
    lease.start_date = request.form.get("start_date")
    lease.start_rent = request.form.get("start_rent")
    lease.info = request.form.get("info")
    lease.uplift_date = request.form.get("uplift_date")
    lease.sale_value_k = request.form.get("sale_value_k")
    lease.rent_cap = request.form.get("rent_cap")
    lease.value = request.form.get("value")
    lease.value_date = request.form.get("value_date")
    lease.rent_id = rent_id
    uplift_type = request.form.get("uplift_type")
    lease.uplift_type_id = \
        LeaseUpType.query.with_entities(LeaseUpType.id).filter \
            (LeaseUpType.uplift_type == uplift_type).one()[0]
    print(request.form)
    db.session.add(lease)
    commit_to_database()
    return rent_id


