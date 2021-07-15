import math
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from flask import request
from app.main.functions import money, moneyToStr
from app.dao.lease import dget_lease_exts, dget_leasep, dget_leaseval_data, dget_leases, dget_lease_relvals, \
    dget_lease_rent, dget_methods, dget_uplift_id, dpost_lease
from app.dao.rent import dbget_rent_id, get_rentcode
from app.models import Lease, LeaseUpType, Rent


def inc_rentpa(rentcap, rentpa, method, up_value, uplift_years):
    # the uplifted rent is calculated by different methods, the first being a simple percentage uplift:
    new_rent = money(0)
    if method == 'ADDPC':
        new_rent = rentpa * (1 + (up_value/100))
    # Edwards Close has a random first uplift which cannot be calculated. Thereafter a simple percentage uplift:
    if method == 'ADDPCZEDW':
        new_rent = 560.00 if rentpa < 260 else rentpa * (1 + (up_value/100))
    # this method simply adds the same value at each rent uplift:
    if method == 'ADDVAL':
        new_rent = rentpa + up_value
    # this method uplifts the rent according to the increase in the RPI index over the relevant period. As not
    # yet known, we store a value eg 1.80 as the estimated annual percentage increase in the index:
    if method == 'RPI':
        new_rent = rentpa * pow(1 + (up_value / 100), uplift_years)

    return new_rent if rentcap < 0.01 else min(rentcap, new_rent)


def mget_gr_value(freq_id, gr_rate, method, rentcap, rentpa, unexpired, up_date, up_value, up_years):
    # we calculate the present value of future rent payments.  The principle is that a payment 1 year from now
    # is worth 1 / 1.065 (the yearly pushaway factor) of the actual payment, if the discount rate is 6.5 per cent
    # first the simplest case - the rent is fixed at zero throughout the remaining unexpired term:
    if method == 'ZERO':
        return 0
    # next simplest case - the rent is a fixed amount throughout the remaining unexpired term:
    elif method == 'FIXED':
        return mget_rent_period_value(freq_id, gr_rate, rentpa, unexpired)
    # next are the cases where the annual rent increases: eg increasing every 25 years by 50 per cent:
    gr_value = 0
    factor = 1 / (1 + gr_rate / 100)
    period_to_uplift = up_date - date.today()
    years_to_uplift = period_to_uplift.days / 365.25
    # first we obtain the present value of the current rent payments up to the first rent uplift date
    gr_value = gr_value + mget_rent_period_value(freq_id, gr_rate, rentpa, years_to_uplift)
    # next we calculate the increased rent after the first uplift
    rentpa = inc_rentpa(rentcap, rentpa, method, up_value, up_years)
    # next we calculate the remaining unexpired term after the first rent uplift
    expiring = unexpired - years_to_uplift
    # next we set the pushaway value as the period from now to that first rent uplift date
    pushaway = years_to_uplift
    # next we calculate the value of each set of rent payments for each period between uplifts after the first uplift
    while expiring > up_years:
        grv_add = mget_rent_period_value(freq_id, gr_rate, rentpa, up_years)
        gr_value = gr_value + grv_add * pow(factor, pushaway)
        expiring = expiring - up_years
        pushaway = pushaway + up_years
        rentpa = inc_rentpa(rentcap, rentpa, method, up_value, up_years)
    # lastly we calculate the value of the remaining rent payments after the last rent uplift
    grv_add = mget_rent_period_value(freq_id, gr_rate, rentpa, expiring)

    return gr_value + grv_add * pow(factor, pushaway)


def mget_lease_exts():
    rentcode = request.form.get("rentcode") or ""
    sql = mget_sql()
    if rentcode and rentcode != '':
        sql = sql + " WHERE r.rentcode LIKE '{}%' ".format(rentcode)

    return dget_lease_exts(sql), rentcode


# def mget_lease_exts_alt():
#     filtr = []
#     rentcode = request.form.get("rentcode") or ""
#     if rentcode and rentcode != '':
#         filtr.append(Rent.rentcode.ilike('%{}%'.format(rentcode)))
#     return dget_lease_exts_alt(filtr), rentcode


def mget_lease_info(lease_id):
    rent_id = int(request.args.get('rent_id', "0", type=str))
    rentcode = request.args.get('rentcode', "ABC1", type=str)
    lease = dget_leasep(lease_id, rent_id)
    if not lease:
        lease = Lease(rent_id=rent_id, rentcode=rentcode)
    methods = dget_methods()

    return lease, methods


def mget_leases():
    lfilter = []
    rentcode = request.form.get("rentcode") or ""
    days = request.form.get("days") or ""
    method = request.form.get("method") or ""
    if rentcode and rentcode != "":
        lfilter.append(Rent.rentcode.ilike('%{}%'.format(rentcode)))
    if days and days != "":
        days = int(days)
        enddate = date.today() + relativedelta(days=days)
        lfilter.append(Lease.uplift_date <= enddate)
    if method and method != "" and method != "":
        lfilter.append(LeaseUpType.method.ilike('%{}%'.format(method)))
    leases = dget_leases(lfilter)
    for lease in leases:
        lease.unexpired = money(mget_unexpired(lease.term, lease.start_date))

    return leases, rentcode, days, method


def mget_lease_variables(rent_id):
    # we obtain all the rent and lease data to calculate for a lease extension quotation:
    fh_rate = float(request.form.get('fh_rate'))
    fhfactor = float(1 + fh_rate / 100)
    gr_new = request.form.get('gr_new')
    gr_rate = float(request.form.get('gr_rate'))
    yp_val = float(request.form.get('yp_val'))
    filtr = []
    filtr.append(Lease.rent_id == rent_id)
    leasedata = dget_leaseval_data(filtr)
    freq_id = leasedata.rent.freq_id
    method = leasedata.LeaseUpType.method
    rent_code = leasedata.rent.rentcode
    rentpa = float(leasedata.rent.rentpa)
    up_date = leasedata.uplift_date
    up_value = float(leasedata.LeaseUpType.value)
    up_years = leasedata.LeaseUpType.years
    rentcap = float(leasedata.rent_cap)
    # the improved value is the notional value of the leasehold interest with a new long lease at a low ground rent
    salevalue = float(leasedata.sale_value_k * 1000)
    unexpired = mget_unexpired(leasedata.term, leasedata.start_date)
    # relativity is the percentage used to calculate the marriage value - see below
    relativity = mget_relativity(unexpired)
    # now we calculate the present value of all future ground rent payments using the gr discount rate
    gr_value = mget_gr_value(freq_id, gr_rate, method, rentcap, rentpa, unexpired, up_date, up_value, up_years)
    # now we calculate the present value of the future freehold reversion using the fh discount rate
    fhval = salevalue / pow(fhfactor, unexpired)
    # the unimproved value is the notional value of the leasehold interest with the present lease
    unimpval = salevalue * relativity / 100
    # marriage value is the notional difference between the unimproved and improved values of the
    # leasehold interest and is calculated as the improved value x relativity
    marriagevalue = (salevalue - unimpval - fhval - gr_value) / 2 if math.floor(unexpired) < 80 else 0
    # the sum we calculate would be awarded for our interest if arbitrated in a lease extension tribunal
    tribval = fhval + gr_value + marriagevalue
    # now we calculate quotations for a series of 5 alternative new terms and new ground rents
    leq5 = tribval + 400 - (marriagevalue/5)
    leq4 = leq5 - yp_val * 100
    leq3 = leq4 - yp_val * 100
    leq2 = leq3 + 500
    val100 = salevalue / pow(fhfactor, 100)
    leq1 = leq2 - val100
    lease_variables = {'#unexpired#': str(money(unexpired)),
                       '#lease_rentcode#': rent_code,
                       '#relativity#': str(money(relativity)),
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


def mget_relativity(unexpired):
    # we obtain the relativity by interpolating between two consecutive values in the lease_relativity table:
    if math.floor(unexpired) < 96.5:
        ids = [math.floor(unexpired), math.floor(unexpired) + 1]
        relativity_values = dget_lease_relvals(ids)
        low = float(relativity_values[0][0])
        high = float(relativity_values[1][0])

        return low + ((high - low) * (unexpired % 1))
    else:
        return 100


def mget_rent_period_value(freq_id, gr_rate, rentpa, period):
    # we obtain the present value of future rent payments over a set period:
    factor = float(1 / (1 + (gr_rate / freq_id) / 100))
    periods = period * freq_id
    inc = (periods % 1) or 0.001
    rpval = 0
    while math.floor(periods) > 0.001:
        rpval = rpval + ((rentpa/freq_id) * pow(factor, float(inc)))
        inc = inc + 1
        periods = periods - 1

    return rpval


def mget_sql():
    return """ SELECT r.rentcode, x.id, x.date, x.value, x.lease_id, y.rent_id  
                FROM lease_extension x LEFT JOIN lease y
                ON x.lease_id = y.id
                LEFT JOIN rent r
                ON y.rent_id = r.id"""


def mget_unexpired(term, startdate):
    difference = date.today() - startdate
    return float(term - (difference.days / 365.25))


def update_lease():
    rent_id = int(request.form.get("rent_id")) or int(0)
    rentcode = request.form.get("rentcode")
    # new lease if no lease for rent_id, otherwise get existing lease for rent_id:
    lease = dget_lease_rent(rent_id) or Lease(rentcode=rentcode)
    lease.term = request.form.get("term")
    lease.start_datetime = datetime.strptime(request.form.get("start_date"), '%Y-%m-%d')
    lease.start_rent = request.form.get("start_rent")
    lease.info = request.form.get("info")
    lease.uplift_date = datetime.strptime(request.form.get("uplift_date"), '%Y-%m-%d')
    lease.sale_value_k = request.form.get("sale_value_k")
    lease.rent_cap = request.form.get("rent_cap")
    lease.rent_id = rent_id if rent_id > 0 else dbget_rent_id(rentcode)
    method = request.form.get("uplift_method")
    value = request.form.get("uplift_value")
    years = request.form.get("uplift_years")
    uplift_id = dget_uplift_id(method, value, years)
    uplift_type = None
    if uplift_id:
        lease.uplift_id = uplift_id
    else:
        uplift_type = LeaseUpType(method=method, value=value, years=years)
    dpost_lease(lease, uplift_type)

    return rent_id
