import math
from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from flask import request
from app.main.functions import money, moneyToStr
from app.dao.lease import dbget_lease, dbget_leaseval_data, dbget_leases, dbget_lease_row, dbget_lease_relvals, \
    dbget_lease_row_rent, dbget_uplift_type_id, dbpost_lease
from app.models import Lease, LeaseUpType, Rent


def get_gr_value(freq_id, gr_rate, method, rentcap, rentpa, unexpired, up_date, up_value, up_years):
    # we obtain the present value of future periodic rent payments over a period of years:
    # first the simplest case of the rent fixed at zero throughout the remaining unexpired term:
    if method == 'ZERO':
        return 0
    # next the next simplest case of the rent fixed throughout the remaining unexpired term:
    elif method == 'FIXED':
        return get_rent_period_value(freq_id, gr_rate, rentpa, unexpired)
    # next the cases where the annual rent increases every x years by some set formula:
    gr_value = 0
    factor = 1 / (1 + gr_rate / 100)
    period_to_uplift = up_date - date.today()
    years_to_uplift = period_to_uplift.days / 365.25
    gr_value = gr_value + get_rent_period_value(freq_id, gr_rate, rentpa, years_to_uplift)
    rentpa = inc_rentpa(rentcap, rentpa, method, up_value, up_years)
    expiring = unexpired - years_to_uplift
    pushaway = years_to_uplift
    while expiring > up_years:
        grv_add = get_rent_period_value(freq_id, gr_rate, rentpa, up_years)
        gr_value = gr_value + grv_add * pow(factor, pushaway)
        expiring = expiring - up_years
        pushaway = pushaway + up_years
        rentpa = inc_rentpa(rentcap, rentpa, method, up_value, up_years)
    grv_add = get_rent_period_value(freq_id, gr_rate, rentpa, expiring)

    return gr_value + grv_add * pow(factor, pushaway)


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
    # we obtain all the rent and lease data to calculate for a lease extension quotation:
    fh_rate = float(request.form.get('fh_rate'))
    fhfactor = float(1 + fh_rate / 100)
    gr_new = request.form.get('gr_new')
    gr_rate = float(request.form.get('gr_rate'))
    yp_val = float(request.form.get('yp_val'))
    filtr = []
    filtr.append(Lease.rent_id == rent_id)
    leasedata = dbget_leaseval_data(filtr)
    freq_id = leasedata.freq_id
    method = leasedata.method
    rent_code = leasedata.rentcode
    rentpa = float(leasedata.rentpa)
    up_date = leasedata.uplift_date
    up_value = float(leasedata.uplift_value)
    up_years = leasedata.years
    rentcap = float(leasedata.rent_cap)
    salevalue = float(leasedata.sale_value_k * 1000)
    startdate = leasedata.start_date
    difference = date.today() - startdate
    unexpired = float(leasedata.term - (difference.days / 365.25))
    relativity = get_relativity(unexpired)
    gr_value = get_gr_value(freq_id, gr_rate, method, rentcap, rentpa, unexpired, up_date, up_value, up_years)
    fhval = salevalue / pow(fhfactor, unexpired)
    unimpval = salevalue * relativity / 100
    marriagevalue = (salevalue - unimpval - fhval - gr_value) / 2 if math.floor(unexpired) < 80 else 0
    tribval = fhval + gr_value + marriagevalue
    leq5 = tribval + 400 - (marriagevalue/5)
    leq4 = leq5 - yp_val * 100
    leq3 = leq4 - yp_val * 100
    leq2 = leq3 + 500
    val100 = salevalue / pow(fhfactor, 100)
    leq1 = leq2 - val100
    lease_variables = {'#unexpired#': str(money(unexpired)),
                       '#lease_rentcode#': rent_code,
                       '#relativity#': str(relativity),
                       '#fh_value#': moneyToStr(fhval if fhval else 0, pound=True),
                       '#gr_value#': moneyToStr(gr_value if gr_value else 0, pound=True),
                       '#marriage_value#': moneyToStr(marriagevalue if marriagevalue else 0, pound=True),
                       '#sale_value#': moneyToStr(salevalue if salevalue else 0, pound=True),
                       '#tribunal_value#': moneyToStr(tribval if tribval else 0, pound=True),
                       '#unimproved_value#': moneyToStr(unimpval if unimpval else 0, pound=True),
                       '#leq5#': moneyToStr(leq5 if leq5 else 0, pound=True),
                       '#leq4#': moneyToStr(leq4 if leq4 else 0, pound=True),
                       '#leq3#': moneyToStr(leq3 if leq3 else 0, pound=True),
                       '#leq2#': moneyToStr(leq2 if leq2 else 0, pound=True),
                       '#leq1#': moneyToStr(leq1 if leq1 else 0, pound=True),
                       '#gr_new#': moneyToStr(gr_new if gr_new else 0, pound=True)
                       }

    return leasedata, lease_variables


def get_rent_period_value(freq_id, gr_rate, rentpa, period):
    # we obtain the present value of future periodic rent payments over a period of years:
    factor = float(1 / (1 + (gr_rate / freq_id) / 100))
    periods = period * freq_id
    inc = (periods % 1) or 0.001
    rpval = 0
    while math.floor(periods) > 0.001:
        rpval = rpval + ((rentpa/freq_id) * pow(factor, float(inc)))
        inc = inc + 1
        periods = periods - 1

    return rpval


def get_relativity(unexpired):
    # we obtain the relativity as a value apportioned between two values in the lease_relativity table:
    if math.floor(unexpired) < 96.5:
        ids = [math.floor(unexpired), math.floor(unexpired) + 1]
        # ids.append(math.floor(unexpired))
        # ids.append(math.floor(unexpired) + 1)
        relativity_values = dbget_lease_relvals(ids)
        low = float(relativity_values[0][0])
        high = float(relativity_values[1][0])

        return low + ((high - low) * (unexpired % 1))
    else:
        return 100


def inc_rentpa(rentcap, rentpa, method, up_value, uplift_years):
    if method == 'ADDPC':
        new_rent = rentpa * (1 + (up_value/100))
    if method == 'ADDPCZEDW':
        new_rent = 560.00 if rentpa < 260 else rentpa * (1 + (up_value/100))
    if method == 'ADDVAL':
        new_rent = rentpa + up_value
    if method == 'RPI':
        new_rent = rentpa * pow(1 + (up_value / 100), uplift_years)

    return new_rent if rentcap < 0.01 else min(rentcap, new_rent)


def post_lease():
    rent_id = int(request.form.get("rent_id"))
    lease = dbget_lease_row_rent(rent_id)
    if lease is None:
    # new lease for empty result, otherwise existing lease:
        lease = Lease()
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


