import json
from datetime import date
from flask import request
from math import ceil
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from app.dao.action import add_action
from app.dao.agent import get_agent
from app.dao.charge import get_charges_rent
from app.dao.common import commit_to_database, get_deed_id, get_filter_stored, get_idlist_recent, get_recent_searches
from app.dao.landlord import get_landlord_id
from app.dao.property import get_propaddrs
from app.dao.rent import get_rent, getrents_basic_sql, getrents_advanced, \
    get_rentsexternal, post_rent, post_rent_filter
from app.main.common import get_rents_fdict, inc_date_m, mpost_search
from app.main.functions import dateToStr, hashCode, money, moneyToStr, round_decimals_down, strToDec
from app.main.rent_filter import dict_advanced, dict_basic, filter_advanced, filter_basic, filter_basic_sql_1, \
    filter_basic_sql_2
from app.models import Rent, RentExternal
from app.modeltypes import AcTypes, AdvArr, Freqs, MailTos, PrDeliveryTypes, SaleGrades, Statuses, Tenures


def get_mailaddr(rent_id, agent_id, mailto_id, tenantname):
    if mailto_id == 1 or mailto_id == 2:
        agent = get_agent(agent_id)
        mailaddr = agent.detail if agent else None
        if mailto_id == 2 and mailaddr:
            mailaddr = tenantname + ' care of ' + mailaddr
    else:
        propaddr = get_propaddr(rent_id)
        if mailto_id == 4:
            mailaddr = 'The owner or occupier, ' + propaddr
        else:
            mailaddr = tenantname + ', ' + propaddr

    return mailaddr


def get_paidtodate(advarrdet, arrears, datecode_id, freq_id, lastrentdate, rentpa):
    paidtodate = lastrentdate
    if arrears <= 0.5:
        if advarrdet == "in advance":
            paidtodate = inc_date_m(paidtodate, freq_id, datecode_id, 1)
            paidtodate = paidtodate - relativedelta(days=1)
        return paidtodate
    else:
        # n is the number of periods of rent owed
        n = ceil(arrears * freq_id / rentpa)
        if advarrdet == "in advance":
            n = n - 1
            paidtodate = inc_date_m(paidtodate, freq_id, datecode_id, -n)
            paidtodate = paidtodate - relativedelta(days=1)
        else:
            paidtodate = inc_date_m(paidtodate, freq_id, datecode_id, -n)
        return paidtodate


def get_price_quote(price, paidtodate, totcharges, rentpa):
    if price != 0:
        days = (date.today() - paidtodate).days
        price_quote = price + totcharges + (days * rentpa / Decimal(365.25))
    else:
        price_quote = Decimal(99999)
    return price_quote


def get_propaddr(rent_id):
    propaddrs = get_propaddrs(rent_id)
    propaddr = '; '.join(each.propaddr.strip() for each in propaddrs)
    return propaddr


def get_popaddr(prop_rent):
    propaddr = '; '.join(item.propaddr.strip() for item in prop_rent)
    return propaddr


def mget_recent_searches(type):
    recent_searches = get_recent_searches(type)
    for recent_search in recent_searches:
        fdict = json.loads(recent_search.dict)
        recent_search.full_dict = fdict
        recent_search.rentcode = fdict.get('rentcode')
        recent_search.tenantname = fdict.get('tenantname')
        recent_search.propaddr = fdict.get('propaddr')
        recent_search.source = fdict.get('source')
        recent_search.agent = fdict.get('agentdetail')
    return recent_searches


def get_rent_gale(next_rent_date, frequency, rentpa):
    if rentpa == 0:
        return money(rentpa)
    missing_pennies = (rentpa * 100) % frequency
    if missing_pennies == 0:
        return money(rentpa / frequency)
    rent_gale = money(round_decimals_down(rentpa / frequency))
    if (frequency == 2 and next_rent_date.month > 6) or (frequency == 4 and next_rent_date.month > 9):
        # TODO: Check that we can divide by 100 without any errors or extra 00000s ever
        return rent_gale + (missing_pennies / 100)
    else:
        return money(rent_gale)


def get_rentp(rent_id):
    # returns a mutable dict with Rent (full) plus joined and derived variables for rent screen, mail, payrequest
    rent = get_rent(rent_id)
    rent.actype = AcTypes.get_name(rent.actype_id)
    rent.advarrdet = AdvArr.get_name(rent.advarr_id)
    rent.charges = get_charges_rent(rent_id)
    rent.totcharges = get_totcharges(rent.charges)
    rent.freqdet = Freqs.get_name(rent.freq_id)
    rent.mailaddr = get_mailaddr(rent_id, rent.agent_id, rent.mailto_id, rent.tenantname)
    rent.mailto = MailTos.get_name(rent.mailto_id)
    rent.nextrentdate = inc_date_m(rent.lastrentdate, rent.freq_id, rent.datecode_id, 1)
    rent.paidtodate = get_paidtodate(rent.advarrdet, rent.arrears, rent.datecode_id, rent.freq_id, rent.lastrentdate,
                                     rent.rentpa)
    rent.prdeliverydet = PrDeliveryTypes.get_name(rent.prdelivery_id)
    rent.propaddrs = get_propaddrs(rent_id)
    rent.price_quote = get_price_quote(rent.price, rent.paidtodate, rent.totcharges, rent.rentpa)
    rent.rent_gale = get_rent_gale(rent.nextrentdate, rent.freq_id, rent.rentpa)
    rent.tenuredet = Tenures.get_name(rent.tenure_id)
    rent.rent_type = "rent charge" if rent.tenuredet == "rentcharge" else "ground rent"
    rent.salegrade = SaleGrades.get_name(rent.salegrade_id)
    rent.statusdet = Statuses.get_name(rent.status_id)

    return rent


def get_pr_strings(rent_pr):
    return {'#advarr#': rent_pr.advarrdet,
            '#arrears#': moneyToStr(rent_pr.arrears, pound=True),
            '#arrears_start_date#': dateToStr(rent_pr.arrears_start_date),
            '#arrears_end_date#': dateToStr(rent_pr.arrears_end_date),
            '#landlord_name#': rent_pr.landlord.name,
            '#lastrentdate#': dateToStr(rent_pr.lastrentdate),
            '#manageraddr#': rent_pr.landlord.manager.manageraddr,
            '#nextrentdate#': dateToStr(rent_pr.nextrentdate),
            '#paidtodate#': dateToStr(rent_pr.paidtodate),
            '#periodly#': rent_pr.freqdet,
            '#price_quote#': moneyToStr(rent_pr.price_quote, pound=True),
            '#propaddr#': '; '.join(each.propaddr.strip() for each in rent_pr.propaddrs),
            '#rentcode#': rent_pr.rentcode,
            '#rentgale#': moneyToStr(rent_pr.rent_gale, pound=True),
            '#rentpa#': moneyToStr(rent_pr.rentpa, pound=True),
            '#rent_type#': rent_pr.rent_type,
            '#totcharges#': moneyToStr(rent_pr.totcharges, pound=True),
            '#totdue#': moneyToStr(rent_pr.arrears + rent_pr.totcharges + rent_pr.rent_gale, pound=True),
            '#acc_name#': rent_pr.landlord.money_account.acc_name,
            '#acc_num#': rent_pr.landlord.money_account.acc_num,
            '#arrearsenddate_plus1#': dateToStr(rent_pr.arrears_end_date_1),
            '#bank_name#': rent_pr.landlord.money_account.bank_name,
            '#manageraddr2#': rent_pr.landlord.manager.manageraddr2,
            '#managername#': rent_pr.landlord.manager.managername,
            '#next_gale_start#': dateToStr(rent_pr.next_gale_start),
            # '#nextrentdate_plus1#': dateToStr(inc_date_m(rent_pr.lastrentdate,
            #                                              rent_pr.freq_id, rent_pr.datecode_id, 2)),
            '#pay_date#': dateToStr(rent_pr.pay_date),
            '#sort_code#': rent_pr.landlord.money_account.sort_code,
            '#tenantname#': rent_pr.tenantname,
            '#today#': dateToStr(date.today())}


def get_rent_strings(rent, type='mail'):
    # this function creates strings needed for mail, pay requests
    # first we test and manipulate certain items from rent
    lastrentdate = rent.lastrentdate
    arrears_start_date = dateToStr(rent.paidtodate + relativedelta(days=1))
    arrears_end_date = dateToStr(rent.nextrentdate + relativedelta(days=-1)) \
        if rent.advarrdet == "in advance" else dateToStr(lastrentdate)
    next_gale_start = dateToStr(rent.nextrentdate) \
        if rent.advarrdet == "in advance" else dateToStr(lastrentdate + relativedelta(days=1))
    charges = rent.charges if hasattr(rent, 'charges') else Decimal(0)
    # TODO: charges_string needs cleaning adds ', ' onto final charge
    charges_string = "no charges"
    charges_list = []
    if charges and charges != 0:
        for charge in charges:
            charge_string = "{} {} added on {}".format(moneyToStr(charge.chargetotal, pound=True),
                                                       charge.chargetype.chargedesc, dateToStr(charge.chargestartdate))
            charges_string += charge_string + ", "
            charges_list.append(charge_string)
    # price = rent.price if rent.price else Decimal(0)
    # if price != 0:
    #     days = (date.today() - rent.paidtodate).days
    #     # days = Decimal(days)
    #     price_quote = price + rent.totcharges + (days * rent.rentpa / Decimal(365.25))
    # else:
    #     price_quote = Decimal(99999)
    propaddr = '; '.join(each.propaddr.strip() for each in rent.propaddrs)
    rent_strings_1 = {'#advarr#': rent.advarrdet,
                      '#arrears#': moneyToStr(rent.arrears, pound=True),
                      '#arrears_start_date#': arrears_start_date,
                      '#arrears_end_date#': arrears_end_date,
                      '#landlord_name#': rent.landlord.name,
                      '#lastrentdate#': dateToStr(rent.lastrentdate),
                      '#manageraddr#': rent.landlord.manager.manageraddr,
                      '#nextrentdate#': dateToStr(rent.nextrentdate),
                      '#paidtodate#': dateToStr(rent.paidtodate),
                      '#periodly#': rent.freqdet,
                      '#price_quote#': moneyToStr(rent.price_quote, pound=True),
                      '#propaddr#': propaddr,
                      '#rentcode#': rent.rentcode,
                      '#rentgale#': moneyToStr(rent.rent_gale, pound=True),
                      '#rentpa#': moneyToStr(rent.rentpa, pound=True),
                      '#rent_type#': rent.rent_type,
                      '#totcharges#': moneyToStr(rent.totcharges, pound=True),
                      '#totdue#': moneyToStr(rent.arrears + rent.totcharges, pound=True)
                      }
    rent_stat = get_rent_stat(rent, rent_strings_1)
    rent_owing = get_rent_owing(rent, rent_strings_1, rent.nextrentdate)
    price_stat = "for sale at {}".format(moneyToStr(rent.price_quote, pound=True)) \
        if rent.salegrade_id == 1 else "not for sale"
    rent_strings_2 = {'#acc_name#': rent.landlord.money_account.acc_name,
                      '#acc_num#': rent.landlord.money_account.acc_num,
                      '#arrearsenddate_plus1#': dateToStr(inc_date_m(rent.lastrentdate,
                                                                     rent.freq_id, rent.datecode_id, 2) + relativedelta(
                          days=-1)) \
                          if rent.advarrdet == "in advance" else dateToStr(rent.nextrentdate),
                      '#bank_name#': rent.landlord.money_account.bank_name,
                      '#charges_string#': charges_string,
                      '#hashcode#': hashCode(rent.rentcode),
                      '#manageraddr2#': rent.landlord.manager.manageraddr2,
                      '#managername#': rent.landlord.manager.managername,
                      '#next_gale_start#': next_gale_start,
                      '#nextrentdate_plus1#': dateToStr(inc_date_m(rent.lastrentdate,
                                                                   rent.freq_id, rent.datecode_id, 2)),
                      '#pay_date#': dateToStr(date.today() + relativedelta(days=30)),
                      '#rent_stat#': rent_stat,
                      '#sort_code#': rent.landlord.money_account.sort_code,
                      '#tenantname#': rent.tenantname,
                      '#today#': dateToStr(date.today()),
                      }
    rent_strings_3 = {'#rent_owing#': rent_owing,
                      '#rent_stat#': rent_stat
                      }

    rent_strings_rent = {'charges_list': charges_list,
                         'price_stat': price_stat,
                         'rent_owing': rent_owing,
                         'rent_stat': rent_stat,
                         'nextrentdate': rent.nextrentdate
                         }
    if type == 'rent':
        return rent_strings_rent
    elif type == 'payrequest':
        return {**rent_strings_1, **rent_strings_2}
    elif type == 'xray':
        rent_strings_xray = {'arrears': moneyToStr(rent.arrears, pound=True),
                             'arrears_start_date': arrears_start_date,
                             'arrears_end_date': arrears_end_date,
                             'lastrentdate': dateToStr(rent.lastrentdate),
                             'nextrentdate': dateToStr(rent.nextrentdate),
                             'paidtodate': dateToStr(rent.paidtodate),
                             'price_quote': moneyToStr(rent.price_quote, pound=True),
                             '#propaddr#': propaddr,
                             'rentgale': moneyToStr(rent.rent_gale, pound=True),
                             'rent_owing': rent_owing,
                             'rentpa': moneyToStr(rent.rentpa, pound=True),
                             'rent_type': rent.rent_type,
                             'totcharges': moneyToStr(rent.totcharges, pound=True),
                             'totdue': moneyToStr(rent.arrears + rent.totcharges, pound=True)
                             }
        return rent_strings_xray
    else:
        return {**rent_strings_1, **rent_strings_2, **rent_strings_3}


def get_rent_owing(rent, rent_strings, nextrentdate):
    if rent.statusdet not in ("grouped payment", "sold off", "terminated"):
        if rent.arrears == 0 and nextrentdate >= date.today():
            rent_owing = "There is no {0} owing to us on this property and {0} is paid up to {1}. \
                            Further {0} will be due and payable {2} {3} on {4} in the sum of {5}" \
                .format(rent_strings["#rent_type#"], rent_strings["#paidtodate#"], rent_strings["#periodly#"],
                        rent_strings["#advarr#"], rent_strings["#nextrentdate#"], rent_strings["#rentgale#"])
        elif rent.arrears == 0 and nextrentdate < date.today():
            rent_owing = "{0} was last paid on this property up to {1}. Further {0} was due and \
                            payable {2} {3} on {4} in the sum of {5} but no rent demand has yet been issued." \
                .format(rent_strings["#rent_type#"], rent_strings["#paidtodate#"], rent_strings["#periodly#"],
                        rent_strings["#advarr#"], rent_strings["#nextrentdate#"], rent_strings["#rentgale#"])
        elif rent.arrears > 0 and rent.lastrentdate > date.today():
            rent_owing = "A recent pay request has been issued for {} {} due {} {} on {}. \
            This amount is not payable until the date stated on the pay request." \
                .format(rent_strings["#totdue#"], rent_strings["#rent_type#"], rent_strings["#periodly#"],
                        rent_strings["#advarr#"], rent_strings["#lastrentdate#"])
        else:
            rent_owing = "The total amount owing to us on this property is {0} being {1} owing for the period from {2} \
             to {3}." \
                .format(rent_strings["#totdue#"], rent_strings["#rent_type#"], rent_strings["#arrears_start_date#"],
                        rent_strings["#arrears_end_date#"])
        if rent.totcharges and rent.totcharges > 0:
            rent_owing = rent_owing.strip('.') + " plus other charges as set out below."
        # TODO reduced
    else:
        rent_owing = "no rent owing because the status for this rent is either grouped payment, managed, \
                        sold off or terminated"

    return rent_owing


def get_rents_advanced(action, filtr_id):  # get rents for advanced queries page with multiple and stored filters
    rents = []
    if action == "load":  # load predefined filter dictionary from jstore
        filter_data = get_filter_stored(filtr_id)
        fdict = json.loads(filter_data.content)
        for key, value in fdict.items():
            fdict[key] = value
        # add metadata of filter to display on rents_advanced.html
        fdict['code'] = filter_data.code
        fdict['description'] = filter_data.description
    else:
        fdict = dict_advanced()  # get request form values or default dictionary
    # now we construct advanced sqlalchemy filter using either dictionary
    filtr = filter_advanced(fdict)
    if action == "save":
        post_rent_filter(fdict)
        # add metadata of filter to display on rents_advanced.html
        fdict['code'] = request.form.get("filtername")
        fdict['description'] = request.form.get("filterdesc")
    # now get filtered rent objects for this filter
    if request.method == 'POST':
        runsize = (request.form.get('runsize') or 300) if action != 'load' else (fdict.get('runsize') or 300)
        rents = getrents_advanced(filtr, runsize)
        for rent in rents:
            rent.propaddr = get_propaddr(rent.id)

    return fdict, rents


def get_rents_basic_sql():  # get rents for home rents page with simple search option
    fdict = dict_basic()
    id_list = get_idlist_recent("recent_rents") if request.method == "GET" else None
    sql = filter_basic_sql_1() + filter_basic_sql_2(fdict, id_list)
    rents = getrents_basic_sql(sql)
    # Sort the rents by the order that they were accessed
    if request.method == 'GET':
        rents = sorted(rents, key=lambda o: id_list.index(o.id))

    return fdict, rents


def get_rents_external():
    dict = get_rents_fdict()
    if request.method == "POST":  # create filter from post values
        for key, value in dict.items():
            val = request.form.get(key) or ""
            dict[key] = val
    filtr = []
    if dict.get('rentcode') and dict.get('rentcode') != "":
        filtr.append(RentExternal.rentcode.startswith([dict.get('rentcode')]))
    if dict.get('agentdetail') and dict.get('agentdetail') != "":
        filtr.append(RentExternal.agentdetail.ilike('%{}%'.format(dict.get('agentdetail'))))
    if dict.get('propaddr') and dict.get('propaddr') != "":
        filtr.append(RentExternal.propaddr.ilike('%{}%'.format(dict.get('propaddr'))))
    if dict.get('source') and dict.get('source') != "":
        filtr.append(RentExternal.source.ilike('%{}%'.format(dict.get('source'))))
    if dict.get('tenantname') and dict.get('tenantname') != "":
        filtr.append(RentExternal.tenantname.ilike('%{}%'.format(dict.get('tenantname'))))
    rents = get_rentsexternal(filtr)

    return dict, rents


def get_rent_stat(rent, rent_strings):
    if rent.statusdet in ("sold off", "terminated"):
        rent_stat = "This property has been sold off or terminated and was subject to a {} of {} " \
                    "per annum payable {} {}, last paid to {}." \
            .format(rent_strings["#rent_type#"], rent_strings["#rentpa#"], rent_strings["#periodly#"],
                    rent_strings["#advarr#"], rent_strings["#paidtodate#"])
    elif rent.statusdet in ("grouped payment", "managed"):
        rent_stat = "This property is subject to a {} of {} per annum payable {} {} but \
                        this rent is collected within a block rent or otherwise managed elsewhere." \
            .format(rent_strings["#rent_type#"], rent_strings["#rentpa#"], rent_strings["#periodly#"],
                    rent_strings["#advarr#"])
    else:
        rent_stat = "This property is subject to a {} of {} per annum payable {} {}." \
            .format(rent_strings["#rent_type#"], rent_strings["#rentpa#"], rent_strings["#periodly#"],
                    rent_strings["#advarr#"])

    return rent_stat


def get_totcharges(charges):
    totcharges = 0
    if charges and charges != 0:
        for charge in charges:
            totcharges += charge.chargebalance
    return totcharges


# simple check that there are no mail/post conflicts. If there are, a message is displayed on rent page load
def rent_validation(rent, message=""):
    messages = [message] if message else []
    action_message = ''
    if ('email' in rent.prdeliverydet) and ('@' not in rent.email):
        messages.append('Payrequest delivery is set to email but there is no valid email address linked to this rent.')
        action_message = 'No valid email '
    if not rent.mailaddr:
        messages.append("No mail address set. Please change the mail address "
                        "from 'mail to agent' or link a new agent.")
        action_message = action_message + 'No valid mail address'
    if action_message:
        # save alert to actions table
        action_str = 'Rent ' + rent.rentcode + ': ' + action_message
        add_action(3, 1, action_str, 'rent_bp.rent', {'rent_id': rent.id})
        commit_to_database()
    return messages


def update_landlord(rent_id):
    rent = Rent.query.get(rent_id)
    rent.landlord_id = get_landlord_id(request.form.get("landlord"))
    rent_id = post_rent(rent)

    return rent_id


def update_rent_rem(rent_id):
    rent = Rent.query.get(rent_id)
    rent.actype_id = AcTypes.get_id(request.form.get("actype"))
    rent.advarr_id = AdvArr.get_id(request.form.get("advarr"))
    rent.arrears = strToDec(request.form.get("arrears"))
    # we need code to generate datecode_id from lastrentdate with user choosing sequence:
    # rent.datecode_id = int(request.form.get("datecode_id"))
    rent.deed_id = get_deed_id(request.form.get("deedcode"))
    rent.freq_id = Freqs.get_id(request.form.get("frequency"))
    rent.lastrentdate = request.form.get("lastrentdate")
    price = request.form.get("price")
    rent.prdelivery_id = AdvArr.get_id(request.form.get("advarr"))
    rent.price = price if (price and price != 'None') else Decimal(0)
    rent.rentpa = strToDec(request.form.get("rentpa"))
    rent.salegrade_id = SaleGrades.get_id(request.form.get("salegrade"))
    rent.source = request.form.get("source")
    rent.status_id = Statuses.get_id(request.form.get("status"))
    rent.tenure_id = Tenures.get_id(request.form.get("tenure"))
    rent_id = post_rent(rent)

    return rent_id


def update_roll_rent(rent_id, last_rent_date, arrears):
    rent = Rent.query.get(rent_id)
    rent.lastrentdate = last_rent_date
    rent.arrears = arrears


def update_rollback_rent(rent_id, arrears):
    rent = Rent.query.get(rent_id)
    last_rent_date = inc_date_m(rent.lastrentdate, rent.freq_id, rent.datecode_id, -1)
    rent.lastrentdate = last_rent_date
    rent.arrears = arrears


def update_tenant(rent_id):
    rent = Rent.query.get(rent_id)
    rent.tenantname = request.form.get("tenantname")
    rent.mailto_id = MailTos.get_id(request.form.get("mailto"))
    rent.email = request.form.get("email")
    rent.prdelivery_id = PrDeliveryTypes.get_id(request.form.get("prdelivery"))
    rent.note = request.form.get("note")
    rent_id = post_rent(rent)

    return rent_id
