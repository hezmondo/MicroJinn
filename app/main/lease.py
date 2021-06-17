from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from flask import request
from app.main.functions import money, moneyToStr
from app.dao.lease import dbget_lease, dbget_leasedata, dbget_leases, dbget_lease_row, \
    dbget_uplift_type_id, dbpost_lease
from app.models import Lease, LeaseUpType, Rent


def get_lease_info(lease_id):
    rent_id = int(request.args.get('rent_id', "0", type=str))
    rentcode = request.args.get('rentcode', "ABC1", type=str)
    lease, uplift_types = dbget_lease(lease_id, rent_id)
    if not lease:
        lease = {
                    'id': 0,
                    'rent_id': rent_id,
                    'rentcode': rentcode
                }

    return lease, uplift_types


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
    leases, uplift_types = dbget_leases(lfilter)

    return leases, uplift_types, rcd, uld, ult


def get_lease_variables(rent_id):
    fhfactor = 1 + (Decimal(request.form.get('fh_rate')) / 100)
    grfactor = 1 + (Decimal(request.form.get('gr_rate')) / 100)
    gr_new = Decimal(request.form.get('gr_new'))
    yp_val = Decimal(request.form.get('yp_val'))
    leasedata = dbget_leasedata(rent_id, grfactor, date.today())
    grval = leasedata["grval"]
    realty = leasedata["realty"]
    rent_code = leasedata["rent_code"]
    salevalue = leasedata["salevalue"]
    unexpired = leasedata["unexpired"]
    fhval = money(salevalue / pow(fhfactor, unexpired))
    unimpval = money(salevalue * realty / 100)
    margeval = money((salevalue - unimpval - fhval - grval) / 2) if unexpired < 80 else Decimal(0)
    tribval = money(fhval + grval + margeval)
    leq5 = money(tribval - (margeval/5))
    leq4 = money(leq5 - yp_val*100)
    leq3 = money(leq4 - yp_val*100)
    leq2 = money(leq3 + 500)
    val100 = money(salevalue / pow(fhfactor, 100))
    leq1 = leq2 - val100
    lease_variables = {'#unexpired#': str(unexpired),
                       '#lease_rentcode#': rent_code,
                       '#relativity#': str(realty),
                       '#fh_value#': moneyToStr(fhval if fhval else 1111.11, pound=True),
                       '#gr_value#': moneyToStr(grval if grval else 1111.11, pound=True),
                       '#marriage_value#': moneyToStr(margeval if margeval else 1111.11, pound=True),
                       '#sale_value#': moneyToStr(salevalue if salevalue else 1111.11, pound=True),
                       '#tribunal_value#': moneyToStr(tribval if tribval else 1111.11, pound=True),
                       '#unimproved_value#': moneyToStr(unimpval if unimpval else 1111.11, pound=True),
                       '#leq5#': moneyToStr(leq5 if leq5 else 1111.11, pound=True),
                       '#leq4#': moneyToStr(leq4 if leq4 else 1111.11, pound=True),
                       '#leq3#': moneyToStr(leq3 if leq3 else 1111.11, pound=True),
                       '#leq2#': moneyToStr(leq2 if leq2 else 1111.11, pound=True),
                       '#leq1#': moneyToStr(leq1 if leq1 else 1111.11, pound=True),
                       '#gr_new#': moneyToStr(gr_new if gr_new else 111.11, pound=True)
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
        lease = dbget_lease_row(lease_id)
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
    lease.uplift_type_id = dbget_uplift_type_id(uplift_type)
    dbpost_lease(lease)

    return rent_id


