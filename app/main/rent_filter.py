from datetime import date
from dateutil.relativedelta import relativedelta
from flask import request
from math import ceil
from sqlalchemy import select
from sqlalchemy.orm import aliased
from app.models import Agent, Charge, Landlord, Property, Rent
from app.modeltypes import AcTypes, PrDeliveryTypes, SaleGrades, Statuses, Tenures
from app.main.functions import strToDec


def dict_basic():
    return {'agentdetail': request.form.get('agentdetail') or "",
            'propaddr': request.form.get('propaddr') or "",
            'rentcode': request.form.get('rentcode') or "",
            'source': request.form.get('source') or "",
            'tenantname': request.form.get('tenantname') or ""}


def dict_advanced():
    dict = dict_basic()
    dict['actype'] = request.form.getlist('actype') or ['all actypes']
    dict['agentmailto'] = request.form.get('agentmailto') or 'include'
    dict['modifier_arrears'] = request.form.get('modifier_arrears') or ''
    dict['arrears'] = request.form.get('arrears') or ''
    dict['modifier_date'] = request.form.get('modifier_date') or ''
    dict['enddate'] = request.form.get('enddate') or ''
    dict['charges'] = request.form.get('charges') or 'include'
    dict['emailable'] = request.form.get('emailable') or 'include'
    dict['landlord'] = request.form.getlist('landlord') or ['all landlords']
    dict['prdelivery'] = request.form.getlist('prdelivery') or ['all prdeliveries']
    dict['modifier_rentpa'] = request.form.get('modifier_rentpa') or ''
    dict['rentpa'] = request.form.get('rentpa') or ''
    dict['modifier_rentperiods'] = request.form.get('modifier_rentperiods') or ''
    dict['rentperiods'] = request.form.get('rentperiods') or ''
    dict['runsize'] = request.form.get('runsize') or ''
    dict['salegrade'] = request.form.getlist('salegrade') or ['all salegrades']
    dict['status'] = request.form.getlist('status') or ['all statuses']
    dict['tenure'] = request.form.getlist('tenure') or ['all tenures']

    return dict


def filter_advanced(dict):
    filtr = filter_basic(dict)
    # first resolve basic dict keys and then deal with advanced dict keys
    if dict['actype'] and dict['actype'] != ['all actypes']:
        ids = []
        for i in range(len(dict['actype'])):
            ids.append(AcTypes.get_id(dict['actype'][i]))
        filtr.append(Rent.actype_id.in_(ids))
    if dict['agentmailto'] and dict['agentmailto'] == "exclude":
        filtr.append(Rent.mailto_id.notin_((1, 2)))
    elif dict['agentmailto'] and dict['agentmailto'] == "only":
        filtr.append(Rent.mailto_id.in_((1, 2)))
    if dict['emailable'] and dict['emailable'] == "exclude":
        filtr.append(Rent.email.notilike('%@%') | Rent.email.is_(None))
    elif dict['emailable'] and dict['emailable'] == "only":
        filtr.append(Rent.email.ilike('%@%'))
    if dict['charges'] and dict['charges'] == "exclude":
        alias_charge = aliased(Charge)
        filtr.append(~select(alias_charge).where(Rent.id == alias_charge.rent_id).exists())
    elif dict['charges'] and dict['charges'] == "only":
        filtr.append(Charge.rent_id == Rent.id)
    if dict['arrears'] and dict['arrears'] != "":
        if dict['modifier_arrears'] == '=':
            filtr.append(Rent.arrears == strToDec(dict['arrears']))
        if dict['modifier_arrears'] == '<':
            filtr.append(Rent.arrears < strToDec(dict['arrears']))
        if dict['modifier_arrears'] == '<=':
            filtr.append(Rent.arrears <= strToDec(dict['arrears']))
        if dict['modifier_arrears'] == '>':
            filtr.append(Rent.arrears > strToDec(dict['arrears']))
        if dict['modifier_arrears'] == '>=':
            filtr.append(Rent.arrears >= strToDec(dict['arrears']))
    if dict['rentpa'] and dict['rentpa'] != "":
        if dict['modifier_rentpa'] == '=':
            filtr.append(Rent.rentpa == strToDec(dict['rentpa']))
        if dict['modifier_rentpa'] == '<':
            filtr.append(Rent.rentpa < strToDec(dict['rentpa']))
        if dict['modifier_rentpa'] == '<=':
            filtr.append(Rent.rentpa <= strToDec(dict['rentpa']))
        if dict['modifier_rentpa'] == '>':
            filtr.append(Rent.rentpa > strToDec(dict['rentpa']))
        if dict['modifier_rentpa'] == '>=':
            filtr.append(Rent.rentpa >= strToDec(dict['rentpa']))
    if dict['rentperiods'] and dict['rentperiods'] != "":
        if dict['modifier_rentperiods'] == '=':
            filtr.append(Rent.arrears == dict['rentperiods'] * Rent.rentpa / Rent.freq_id)
        if dict['modifier_rentperiods'] == '<':
            filtr.append(Rent.arrears < dict['rentperiods'] * Rent.rentpa / Rent.freq_id)
        if dict['modifier_rentperiods'] == '<=':
            filtr.append(Rent.arrears <= dict['rentperiods'] * Rent.rentpa / Rent.freq_id)
        if dict['modifier_rentperiods'] == '>':
            filtr.append(Rent.arrears > dict['rentperiods'] * Rent.rentpa / Rent.freq_id)
        if dict['modifier_rentperiods'] == '>=':
            filtr.append(Rent.arrears >= dict['rentperiods'] * Rent.rentpa / Rent.freq_id)
    if dict['enddate'] and dict['enddate'] != "":
        if dict['modifier_date'] == '=':
            filtr.append(Rent.lastrentdate == (dict['enddate']))
        if dict['modifier_date'] == '<':
            filtr.append(Rent.lastrentdate < (dict['enddate']))
        if dict['modifier_date'] == '<=':
            filtr.append(Rent.lastrentdate <= (dict['enddate']))
        if dict['modifier_date'] == '>':
            filtr.append(Rent.lastrentdate > (dict['enddate']))
        if dict['modifier_date'] == '>=':
            filtr.append(Rent.lastrentdate >= (dict['enddate']))
    if dict['landlord'] and dict['landlord'] != ['all landlords']:
        filtr.append(Landlord.name.in_(dict['landlord']))
    if dict['prdelivery'] and dict['prdelivery'] != ['all prdeliveries']:
        ids = []
        for i in range(len(dict['prdelivery'])):
            ids.append(PrDeliveryTypes.get_id(dict['prdelivery'][i]))
        filtr.append(Rent.prdelivery_id.in_(ids))
    if dict['salegrade'] and dict['salegrade'] != ['all salegrades']:
        ids = []
        for i in range(len(dict['salegrade'])):
            ids.append(SaleGrades.get_id(dict['salegrade'][i]))
        filtr.append(Rent.salegrade_id.in_(ids))
    if dict['status'] and dict['status'] != ['all statuses']:
        ids = []
        for i in range(len(dict['status'])):
            ids.append(Statuses.get_id(dict['status'][i]))
        filtr.append(Rent.status_id.in_(ids))
    if dict['tenure'] and dict['tenure'] != ['all tenures']:
        ids = []
        for i in range(len(dict['tenure'])):
            ids.append(Tenures.get_id(dict['tenure'][i]))
        filtr.append(Rent.tenure_id.in_(ids))

    return filtr


def filter_basic(dict):
    filtr = []
    # create simple filter for rents (home) and rents external pages
    if dict.get('agentdetail'):
        filtr.append(Agent.detail.ilike('%{}%'.format(dict.get('agentdetail'))))
    if dict.get('propaddr'):
        filtr.append(Property.propaddr.ilike('%{}%'.format(dict.get('propaddr'))))
    if dict.get('rentcode'):
        filtr.append(Rent.rentcode.startswith([dict.get('rentcode')]))
    if dict.get('source'):
        filtr.append(Rent.source.ilike('%{}%'.format(dict.get('source'))))
    if dict.get('tenantname'):
        filtr.append(Rent.tenantname.ilike('%{}%'.format(dict.get('tenantname'))))

    return filtr


def filter_basic_sql_1():
    return """ SELECT r.id, r.rentcode, r.tenantname, r.rentpa, r.arrears, r.lastrentdate, r.source, r.status_id, 
                r.freq_id, r.datecode_id, a.detail, total_owing(r.id) AS 'owing', 
                next_rent_date(r.id, 1) as 'nextrentdate',
                (SELECT GROUP_CONCAT(DISTINCT propaddr SEPARATOR '; ')
                FROM property 
                WHERE rent_id = r.id 
                GROUP BY rent_id) as propaddr
                FROM rent r 
                LEFT JOIN agent a 
                ON a.id = r.agent_id 
                LEFT JOIN property p 
                ON p.rent_id = r.id """


def filter_basic_sql_2(dict, id_list):
    if id_list:
        sql2 = " r.id IN {}".format(tuple(id_list))
    else:
        agentdetail_sql = " a.detail LIKE '%{}%' ".format(dict.get('agentdetail')) if dict.get('agentdetail') else ""
        # todo additional filter for amount owing:  owingSql = " {} <= Owing AND
        #  Owing <= {}".format(owing - money(0.03), owing + money(0.03)) if owing is not None else ""
        propaddr_sql = " propaddr LIKE '%{}%' ".format(dict.get('propaddr')) if dict.get('propaddr') else ""
        rentcode_sql = " r.rentcode LIKE '{}%' ".format(dict.get('rentcode')) if dict.get('rentcode') else ""
        source_sql = " r.source LIKE '%{}%' ".format(dict.get('source')) if dict.get('source') else ""
        tenantname_sql = " r.tenantname LIKE '%{}%' ".format(dict.get('tenantname')) if dict.get('tenantname') else ""
        sql2 = " AND " \
            .join([sql for sql in [rentcode_sql, tenantname_sql, source_sql, agentdetail_sql, propaddr_sql] if sql])
    sql2 = "WHERE " + sql2 + " GROUP BY r.id LIMIT 50" if sql2 else " GROUP BY r.id LIMIT 50"

    return sql2
