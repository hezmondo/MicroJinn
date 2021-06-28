import math
from datetime import date
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from flask import request
from app.main.functions import money, moneyToStr
from app.dao.lease import dbget_lease, dbget_leaseval_data, dbget_leases, dbget_lease_row, dbget_lease_relvals, \
    dbget_lease_row_rent, dbget_uplift_type_id, dbpost_lease
from app.models import Lease, LeaseUpType, Rent


def get_gr_value(freq_id, gr_rate, method, rentpa, unexpired, uplift_date, uplift_value, uplift_years):
    # we obtain the present value of future periodic rent payments over a period of years:
    # first the simplest case of the rent fixed at zero throughout the remaining unexpired term:
    if method == 'ZERO':
        return money(0)
    # next the next simplest case of the rent fixed throughout the remaining unexpired term:
    if method == 'FIXED':
        return money(get_rent_period_value(freq_id, gr_rate, rentpa, unexpired))
    # next the cases where the annual rent increases every x years by some set formula:
    gr_value = money(0)
    factor = 1 / (1 + gr_rate / 100)
    period_to_uplift = uplift_date - date.today()
    years_to_uplift = money(period_to_uplift.days / 365.25)
    # next the case of the rent increasing by a fixed percentage on each uplift date:
    if method == 'ADDPC':
        gr_value = gr_value + get_rent_period_value(freq_id, gr_rate, rentpa, years_to_uplift)
        rentpa = rentpa * (1 + (uplift_value/100))
        expiring = unexpired -  years_to_uplift
        pushaway = years_to_uplift
        while expiring > uplift_years:
            grv_add = get_rent_period_value(freq_id, gr_rate, rentpa, uplift_years)
            gr_value = gr_value + grv_add * pow(factor, pushaway)
            expiring = expiring - uplift_years
            pushaway = pushaway + uplift_years
        grv_add = get_rent_period_value(freq_id, gr_rate, rentpa, expiring)
        gr_value = money(gr_value + grv_add * pow(factor, pushaway))
        return gr_value
    # next the case of the rent increasing by a fixed amount on each uplift date:


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
    fhfactor = 1 + (money(request.form.get('fh_rate')) / 100)
    gr_new = money(request.form.get('gr_new'))
    gr_rate = money(request.form.get('gr_rate'))
    yp_val = money(request.form.get('yp_val'))
    filtr = []
    filtr.append(Lease.rent_id == rent_id)
    leasedata = dbget_leaseval_data(filtr)
    freq_id = leasedata.freq_id
    method = leasedata.method
    rent_code = leasedata.rentcode
    rentpa = leasedata.rentpa
    uplift_date = leasedata.uplift_date
    uplift_value = leasedata.uplift_value
    uplift_years = leasedata.years
    salevalue = money(leasedata.sale_value_k * 1000)
    startdate = leasedata.start_date
    difference = date.today() - startdate
    unexpired = money(leasedata.term - (difference.days / 365.25))
    relativity = get_relativity(unexpired)
    gr_value = get_gr_value(freq_id, gr_rate, method, rentpa, unexpired, uplift_date, uplift_value, uplift_years)
    fhval = money(salevalue / pow(fhfactor, unexpired))
    unimpval = money(salevalue * relativity / 100)
    marriagevalue = money((salevalue - unimpval - fhval - gr_value) / 2) if math.floor(unexpired) < 80 else Decimal(0)
    tribval = money(fhval + gr_value + marriagevalue)
    leq5 = money(tribval + 400 - (marriagevalue/5))
    leq4 = money(leq5 - yp_val*100)
    leq3 = money(leq4 - yp_val*100)
    leq2 = money(leq3 + 500)
    val100 = money(salevalue / pow(fhfactor, 100))
    leq1 = leq2 - val100
    lease_variables = {'#unexpired#': str(unexpired),
                       '#lease_rentcode#': rent_code,
                       '#relativity#': str(relativity),
                       '#fh_value#': moneyToStr(fhval if fhval else 1111.11, pound=True),
                       '#gr_value#': moneyToStr(gr_value if gr_value else 1111.11, pound=True),
                       '#marriage_value#': moneyToStr(marriagevalue if marriagevalue else 1111.11, pound=True),
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


def get_rent_period_value(freq_id, gr_rate, rentpa, period):
    # we obtain the present value of future periodic rent payments over a period of years:
    factor = 1 / (1 + (gr_rate / freq_id) / 100)
    periods = period * freq_id
    inc = (periods % 1) or 0.001
    rpval = 0
    while math.floor(periods) > 1:
        rpval = rpval + ((rentpa/freq_id) * pow(factor, inc))
        inc = inc + 1
        periods = periods - 1

    return rpval


def get_relativity(unexpired):
    # we obtain the relativity as a value apportioned between two values in the lease_relativity table:
    if math.floor(unexpired) < 96.5:
        ids = []
        ids.append(math.floor(unexpired))
        ids.append(math.floor(unexpired) + 1)
        relativity_values = dbget_lease_relvals(ids)
        low = relativity_values[0][0]
        high = relativity_values[1][0]

        return money(low + ((high - low) * (unexpired % 1)))
    else:
        return money(100)


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


