import sqlalchemy
from app import db
from datetime import date
from dateutil.relativedelta import relativedelta
from flask import request
from sqlalchemy import func
from app.dao.functions import moneyToStr
from app.models import Lease, Lease_uplift_type, Rent


# leases
def get_lease(id):
    # id can be actual lease id or 0 (for new lease or for id unknown as coming from rent)
    action = request.args.get('action', "view", type=str)
    rentcode = request.args.get('rentcode', "DUMMY" , type=str)
    rentid = int(request.args.get('rentid', "0", type=str))
    lease_filter = []
    if id == 0 and action == "new":
        lease = {
            'id': 0,
            'rent_id': rentid,
            'rentcode': rentcode
        }
    else:
        if id == 0:
            lease_filter.append(Lease.rent_id == rentid)
        else:
            lease_filter.append(Lease.id == id)
        lease = \
            Lease.query.join(Rent).join(Lease_uplift_type).with_entities(Lease.id, Rent.rentcode, Lease.term,
                 Lease.startdate, Lease.startrent, Lease.info, Lease.upliftdate, Lease_uplift_type.uplift_type,
                 Lease.lastvaluedate, Lease.lastvalue, Lease.impvaluek, Lease.rent_id, Lease.rentcap) \
                .filter(*lease_filter).one_or_none()

    uplift_types = [value for (value,) in Lease_uplift_type.query.with_entities(Lease_uplift_type.uplift_type).all()]

    return action, lease, uplift_types


def get_leasedata(rent_id, fh_rate, gr_rate, new_gr_a, new_gr_b, yp_low, yp_high):
    resultproxy = db.session.execute(sqlalchemy.text("CALL lex_valuation(:a, :b, :c, :d, :e, :f, :g)"), params={"a": rent_id, "b": fh_rate, "c": gr_rate, "d": new_gr_a, "e": new_gr_b, "f": yp_low, "g": yp_high})
    leasedata = [{column: value for column, value in rowproxy.items()} for rowproxy in resultproxy][0]
    db.session.commit()

    return leasedata


def get_leases():
    lease_filter = []
    rcd = request.form.get("rentcode") or "all rentcodes"
    uld = request.form.get("upliftdays") or ""
    ult = request.form.get("uplift_type") or "all uplift types"
    if rcd and rcd != "all rentcodes":
        lease_filter.append(Rent.rentcode.ilike('%{}%'.format(rcd)))
    if uld and uld != "":
        uld = int(uld)
        enddate = date.today() + relativedelta(days=uld)
        lease_filter.append(Lease.upliftdate <= enddate)
    if ult and ult != "" and ult != "all uplift types":
        lease_filter.append(Lease_uplift_type.uplift_type.ilike('%{}%'.format(ult)) )

    leases = Lease.query.join(Rent).join(Lease_uplift_type).with_entities(Rent.rentcode, Lease.id, Lease.info,
              func.mjinn.lex_unexpired(Lease.id).label('unexpired'),
              Lease.term, Lease.upliftdate, Lease_uplift_type.uplift_type) \
        .filter(*lease_filter).limit(60).all()

    uplift_types = [value for (value,) in Lease_uplift_type.query.with_entities(Lease_uplift_type.uplift_type).all()]
    uplift_types.insert(0, "all uplift types")

    return leases, uplift_types, rcd, uld, ult


def get_lease_variables(rent_id):
    fh_rate = request.form.get('fh_rate')
    gr_rate = request.form.get('gr_rate')
    new_gr_a = request.form.get('new_gr_a')
    new_gr_b = request.form.get('new_gr_b')
    yp_low = request.form.get('yp_low')
    yp_high = request.form.get('yp_high')

    leasedata = get_leasedata(rent_id, fh_rate, gr_rate, new_gr_a, new_gr_b, yp_low, yp_high)
    impval = leasedata["impvalk"] * 1000
    unimpval = leasedata["impvalk"] * leasedata["realty"] * 10 if leasedata["realty"] > 0 else impval
    lease_variables = {'#unexpired#': str(leasedata["unexpired"]) if leasedata else "11.11",
                       '#rent_code#': leasedata["rent_code"] if leasedata else "some rentcode",
                       '#relativity#': str(leasedata["realty"]) if leasedata else "some relativity",
                       '#totval#': str(leasedata["totval"]) if leasedata else "some total value",
                       '#unimpvalue#': moneyToStr(unimpval if leasedata else 555.55, pound=True),
                       '#impvalue#': moneyToStr(impval if leasedata else 555.55, pound=True),
                       '#leq99a#': moneyToStr(leasedata["leq99a"] if leasedata else 55555.55, pound=True),
                       '#grnewa#': moneyToStr(leasedata["grnew1"] if leasedata else 555.55, pound=True),
                       '#grnewb#': moneyToStr(leasedata["grnew2"] if leasedata else 555.55, pound=True),
                       '#leq125a#': moneyToStr(leasedata["leq125a"] if leasedata else 55555.55, pound=True),
                       '#leq175a#': moneyToStr(leasedata["leq175a"] if leasedata else 55555.55, pound=True),
                       '#leq175f#': moneyToStr(leasedata["leq175f"] if leasedata else 55555.55, pound=True),
                       '#leq175p#': moneyToStr(leasedata["leq175p"] if leasedata else 55555.55, pound=True),
                       }

    return leasedata, lease_variables


def post_lease(id):
    rentid = int(request.form.get("rent_id"))
    # new lease for id 0, otherwise existing lease:
    if id == 0:
        lease = Lease()
        lease.id = 0
        lease.rent_id = rentid
        lease.startdate = "1991-01-01"
        lease.upliftdate = "1991-01-01"
        lease.lastvaluedate = "1991-01-01"
    else:
        lease = Lease.query.get(id)
    lease.term = request.form.get("term")
    lease.startdate = request.form.get("startdate")
    lease.startrent = request.form.get("startrent")
    lease.info = request.form.get("info")
    lease.upliftdate = request.form.get("upliftdate")
    lease.impvaluek = request.form.get("impvaluek")
    lease.rentcap = request.form.get("rentcap")
    lease.lastvalue = request.form.get("lastvalue")
    lease.lastvaluedate = request.form.get("lastvaluedate")
    lease.rent_id = rentid
    uplift_type = request.form.get("uplift_type")
    lease.uplift_type_id = \
        Lease_uplift_type.query.with_entities(Lease_uplift_type.id).filter \
            (Lease_uplift_type.uplift_type == uplift_type).one()[0]
    print(request.form)
    db.session.add(lease)
    db.session.commit()

    return rentid


