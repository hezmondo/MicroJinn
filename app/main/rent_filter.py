from datetime import date
from dateutil.relativedelta import relativedelta
from flask import request
from app.main.functions import strToDate
from app.models import Agent, Property, Rent
from app.modeltypes import AcTypes, PrDeliveryTypes, SaleGrades, Statuses, Tenures


def filter_advanced(dict):
    fdict, filtr = filter_basic(dict)   # gets interpreted filter for basic dict keys
    # now unpack filter values for the additional dict keys
    dict['actype'] = request.form.getlist('actype') or ['all actypes']
    if dict['actype'] and dict['actype'] != [] and dict['actype'] != ['all actypes']:
        ids = []
        for i in range(len(dict['actype'])):
            ids.append(AcTypes.get_id(dict['actype'][i]))
        filtr.append(Rent.actype_id.in_(ids))
    dict['agentmailto'] = request.form.get('agentmailto') or 'include'
    if dict['agentmailto'] and dict['agentmailto'] == "exclude":
        filtr.append(Rent.mailto_id.notin_(1, 2))
    elif dict['agentmailto'] and dict['agentmailto'] == "only":
        filtr.append(Rent.mailto_id.in_(1, 2))
        # elif key == "arrears" and value and value != "":
        #     filtr.append(Rent.arrears == strToDec('{}'.format(value)))
        # I will get to this when I do
        # elif key == "charges" and value == "exclude":
        #     filtr.append(Rent.mailto_id.notin_(1, 2))
        # elif key == "charges" and value == "only":
        #     filtr.append(Rent.mailto_id.in_(1, 2))
        # elif key == "emailable" and value == "exclude":
        #     filtr.append(Rent.mailto_id.notin_(1, 2))
        # elif key == "emailable" and value == "only":
        #     filtr.append(Rent.mailto_id.in_(1, 2))
        dict['enddate'] = request.form.get('enddate') or date.today() + relativedelta(days=50)
        filtr.append(Rent.lastrentdate <= strToDate('{}'.format(dict['enddate'])))
        dict['landlord'] = request.form.getlist('landlord') or ['all landlords']
        if dict['landlord'] and dict['landlord'] != [] and dict['landlord'] != ['all landlords']:
            filtr.append(Rent.name.in_(dict['landlord']))
        dict['prdelivery'] = request.form.getlist('prdelivery') or ['all prdeliveries']
        if dict['prdelivery'] and dict['prdelivery'] != [] and dict['prdelivery'] != ['all prdeliveries']:
            ids = []
            for i in range(len(dict['prdelivery'])):
                ids.append(PrDeliveryTypes.get_id(dict['prdelivery'][i]))
            filtr.append(Rent.prdelivery_id.in_(ids))
        # elif key == "rentpa" and value and value != "":
        #     filtr.append(Rent.rentpa == strToDec('{}'.format(value)))
        # elif key == "rentperiods" and value and value != "":
        #     filtr.append(Rent.rentpa == strToDec('{}'.format(value)))
        dict['salegrade'] = request.form.getlist('salegrade') or ['all salegrades']
        if dict['salegrade'] and dict['salegrade'] != [] and dict['salegrade'] != ['all salegrades']:
            ids = []
            for i in range(len(dict['salegrade'])):
                ids.append(SaleGrades.get_id(dict['salegrade'][i]))
            filtr.append(Rent.salegrade_id.in_(ids))
        dict['status'] = request.form.getlist('status') or ['all statuses']
        if dict['status'] and dict['status'] != [] and dict['status'] != ['all statuses']:
            ids = []
            for i in range(len(dict['status'])):
                ids.append(Statuses.get_id(dict['status'][i]))
            filtr.append(Rent.status_id.in_(ids))
        dict['tenure'] = request.form.getlist('tenure') or ['all tenures']
        if dict['tenure'] and dict['tenure'] != [] and dict['tenure'] != ['all tenures']:
            ids = []
            for i in range(len(dict['tenure'])):
                ids.append(Tenures.get_id(dict['tenure'][i]))
            filtr.append(Rent.tenure_id.in_(ids))

    return dict, filtr


def filter_basic(dict):
    filtr = []
    dict['agentdetail'] = request.form.get('agentdetail') or ''
    dict['propaddr'] = request.form.get('propaddr') or ''
    dict['rentcode'] = request.form.get('rentcode') or ''
    dict['source'] = request.form.get('source') or ''
    dict['tenantname'] = request.form.get('tenantname') or ''
    if dict.get('agentdetail') and dict.get('agentdetail') != "":
        filtr.append(Agent.detail.ilike('%{}%'.format(dict.get('agentdetail'))))
    if dict.get('propaddr') and dict.get('propaddr') != "":
        filtr.append(Property.propaddr.ilike('%{}%'.format(dict.get('propaddr'))))
    if dict.get('rentcode') and dict.get('rentcode') != "":
        filtr.append(Rent.rentcode.startswith([dict.get('rentcode')]))
    if dict.get('source') and dict.get('source') != "":
        filtr.append(Rent.source.ilike('%{}%'.format(dict.get('source'))))
    if dict.get('tenantname') and dict.get('tenantname') != "":
        filtr.append(Rent.tenantname.ilike('%{}%'.format(dict.get('tenantname'))))

    return dict, filtr
