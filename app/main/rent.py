from datetime import date
from flask import request
from math import ceil
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from app.dao.agent import get_agent
from app.dao.charge import get_charges_rent
from app.dao.common import get_deed_id, get_status_id
from app.dao.landlord import get_landlord_id
from app.dao.property import get_property_addrs
from app.dao.rent import get_rent, post_rent
from app.main.common import get_actype, get_actype_id, get_advarrdet, get_advarr_id, get_freq, get_freq_id,  \
    get_mailto_id, get_prdelivery, get_prdelivery_id, get_salegrade, get_salegrade_id, get_tenure, get_tenure_id, \
    inc_date_m
from app.main.functions import dateToStr, hashCode, money, moneyToStr, round_decimals_down, strToDec
from app.models import Rent


def get_mailaddr(rent_id, agent_id, mailto_id, tenantname):
    if agent_id and agent_id != 0 and mailto_id in (1, 2):
        agent = get_agent(agent_id)
        mailaddr = agent.detail
        if mailto_id == 2:
            mailaddr = tenantname + 'care of' + mailaddr
    else:
        propaddr = get_propaddr(rent_id)
        if mailto_id == 4:
            mailaddr = 'the owner or occupier' + propaddr
        else:
            mailaddr = tenantname + ', ' + propaddr

    return mailaddr


def get_propaddr(rent_id):
    p_addrs = get_property_addrs(rent_id)
    p_addr = '; '.join(each.propaddr.strip() for each in p_addrs)
    return p_addr


def get_paidtodate(advarrdet, arrears, datecode_id, freq_id, lastrentdate, rentpa):
    paidtodate = lastrentdate
    if arrears <= 0.5:
        if advarrdet == "in advance":
            paidtodate = inc_date_m(paidtodate, freq_id, datecode_id, 1)
            paidtodate = paidtodate + relativedelta(days=30)
        return paidtodate
    else:
        # n is the number of periods of rent owed
        n = ceil(arrears * freq_id / rentpa)
        if advarrdet == "in advance":
            n = n - 1
            paidtodate = inc_date_m(paidtodate, freq_id, datecode_id, -n)
            paidtodate = paidtodate + relativedelta(days=-1)
        else:
            paidtodate = inc_date_m(paidtodate, freq_id, datecode_id, -n)
        return paidtodate


def get_rentp(rent_id):
    # returns a mutable dict with Rent (full) plus joined and derived variables for rent screen, mail, payrequest
    rent = get_rent(rent_id)
    rent.acc_name = rent.landlord.money_account.acc_name
    rent.actypedet = get_actype(rent.actype_id)
    rent.acc_num = rent.landlord.money_account.acc_num
    rent.advarrdet = get_advarrdet(rent.advarr_id)
    rent.bank_name = rent.landlord.money_account.bank_name
    rent.charges = get_charges_rent(rent_id)
    rent.detail = rent.agent.detail if hasattr(rent.agent, 'detail') else "no agent"
    rent.totcharges = get_totcharges(rent.charges)
    rent.freqdet = get_freq(rent.freq_id)
    rent.info = rent.typedeed.info
    rent.landlordname = rent.landlord.name
    rent.mailaddr = get_mailaddr(rent_id, rent.agent_id, rent.mailto_id, rent.tenantname)
    rent.managername = rent.landlord.manager.managername
    rent.manageraddr = rent.landlord.manager.manageraddr
    rent.manageraddr2 = rent.landlord.manager.manageraddr2
    rent.nextrentdate = inc_date_m(rent.lastrentdate, rent.freq_id, rent.datecode_id, 1)
    rent.paidtodate = get_paidtodate(rent.advarrdet, rent.arrears, rent.datecode_id, rent.freq_id, rent.lastrentdate,
                                     rent.rentpa)
    rent.prdeliverydet = get_prdelivery(rent.prdelivery_id)
    rent.propaddr = get_propaddr(rent_id)
    rent.rent_gale = get_rent_gale(rent.nextrentdate, rent.freq_id, rent.rentpa)
    rent.tenuredet = get_tenure(rent.tenure_id)
    rent.rent_type = "rent charge" if rent.tenuredet == "rentcharge" else "ground rent"
    rent.salegrade = get_salegrade(rent.salegrade_id)
    rent.statusdet = rent.typestatus.statusdet
    rent.sort_code = rent.landlord.money_account.sort_code

    return rent


def get_rent_gale(next_rent_date, frequency, rentpa):
    if rentpa == 0 or frequency not in (2, 4):
        return money(rentpa)
    missing_pennies = (rentpa * 100) % frequency
    if missing_pennies == 0:
        return money(rentpa / frequency)
    rent_gale = money(round_decimals_down(rentpa / frequency))
    if (frequency == 2 and next_rent_date.month > 6) or (frequency == 4 and next_rent_date.month > 9):
        return rent_gale + (missing_pennies / 100)
    else:
        return money(rent_gale)


def get_rent_strings(rent, type='mail'):
    # this function creates strings needed for mail, pay requests and rent screen statements
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
                                                       charge.chargedesc, dateToStr(charge.chargestartdate))
            charges_string += charge_string + ", "
            charges_list.append(charge_string)
    price = rent.price if rent.price else Decimal(0)
    if price != 0:
        days = (date.today() - rent.paidtodate).days
        # days = Decimal(days)
        price_quote = price + rent.totcharges + (days * rent.rentpa / Decimal(365.25))
    else:
        price_quote = Decimal(99999)
    rent_strings_1 = {'#advarr#': rent.advarrdet,
                      '#arrears#': moneyToStr(rent.arrears, pound=True),
                      '#arrears_start_date#': arrears_start_date,
                      '#arrears_end_date#': arrears_end_date,
                      '#landlord_name#': rent.landlordname,
                      '#lastrentdate#': dateToStr(rent.lastrentdate),
                      '#manageraddr#': rent.manageraddr,
                      '#nextrentdate#': dateToStr(rent.nextrentdate),
                      '#paidtodate#': dateToStr(rent.paidtodate),
                      '#periodly#': rent.freqdet,
                      '#price_quote#': moneyToStr(price_quote, pound=True),
                      '#propaddr#': rent.propaddr,
                      '#rentcode#': rent.rentcode,
                      '#rentgale#': moneyToStr(rent.rent_gale, pound=True),
                      '#rentpa#': moneyToStr(rent.rentpa, pound=True),
                      '#rent_type#': rent.rent_type,
                      '#totcharges#': moneyToStr(rent.totcharges, pound=True),
                      '#totdue#': moneyToStr(rent.arrears + rent.totcharges, pound=True)
                      }
    rent_stat = get_rent_stat(rent, rent_strings_1)
    rent_owing = get_rent_owing(rent, rent_strings_1, rent.nextrentdate)
    price_stat = "for sale at {}".format(moneyToStr(price_quote, pound=True)) \
        if rent.salegrade_id == 1 else "not for sale"
    rent_strings_2 = {'#acc_name#': rent.acc_name if hasattr(rent, 'acc_name') else "no acc_name",
                      '#acc_num#': rent.acc_num if hasattr(rent, 'acc_num') else "no acc_num",
                      '#arrearsenddate_plus1#': dateToStr(inc_date_m(rent.lastrentdate,
                                                                     rent.freq_id, rent.datecode_id, 2) + relativedelta(
                          days=-1)) \
                          if rent.advarrdet == "in advance" else dateToStr(rent.nextrentdate),
                      '#bank_name#': rent.bank_name,
                      '#charges_string#': charges_string,
                      '#hashcode#': hashCode(rent.rentcode),
                      '#manageraddr2#': rent.manageraddr2,
                      '#managername#': rent.managername,
                      '#next_gale_start#': next_gale_start,
                      '#nextrentdate_plus1#': dateToStr(inc_date_m(rent.lastrentdate,
                                                                   rent.freq_id, rent.datecode_id, 2)),
                      '#pay_date#': dateToStr(date.today() + relativedelta(days=30)),
                      '#rent_stat#': rent_stat,
                      '#sort_code#': rent.sort_code,
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
                             'price_quote': moneyToStr(price_quote, pound=True),
                             '#propaddr#': rent.propaddr,
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
    if ('email' in rent.prdeliverydet) and ('@' not in rent.email):
        messages.append('Payrequest delivery is set to email but there is no valid email address linked to this rent.')
    if not rent.mailaddr:
        messages.append("The mail address is currently 'None'. Please change the mail address "
                        "from mail to agent or link a new agent.")
    return messages


def update_rent_rem(rent_id):
    rent = Rent.query.get(rent_id)
    rent.actype_id = get_actype_id(request.form.get("actype"))
    rent.advarr_id = get_advarr_id(request.form.get("advarr"))
    rent.arrears = strToDec(request.form.get("arrears"))
    # we need code to generate datecode_id from lastrentdate with user choosing sequence:
    # rent.datecode_id = int(request.form.get("datecode_id"))
    rent.deed_id = get_deed_id(request.form.get("deedcode"))
    rent.freq_id = get_freq_id(request.form.get("frequency"))
    rent.landlord_id = get_landlord_id(request.form.get("landlord"))
    rent.lastrentdate = request.form.get("lastrentdate")
    price = request.form.get("price")
    rent.prdelivery_id = get_advarr_id(request.form.get("advarr"))
    rent.price = price if (price and price != 'None') else Decimal(0)
    rent.rentpa = strToDec(request.form.get("rentpa"))
    rent.salegrade_id = get_salegrade_id(request.form.get("salegrade"))
    rent.source = request.form.get("source")
    rent.status_id = get_status_id(request.form.get("status"))
    rent.tenure_id = get_tenure_id(request.form.get("tenure"))
    post_rent(rent)


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
    rent.mailto_id = get_mailto_id(request.form.get("mailto"))
    rent.email = request.form.get("email")
    rent.prdelivery_id = get_prdelivery_id(request.form.get("prdelivery"))
    rent.note = request.form.get("note")
    rent_id = post_rent(rent)

    return rent_id
