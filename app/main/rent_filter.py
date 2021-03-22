from flask import request
from app.dao.common import AcTypes, PrDeliveryTypes, SaleGrades, Statuses, Tenures
from app.main.functions import strToDate
from app.models import Agent, Landlord, Rent


def get_filter_advanced(fdict):
    # first unpack filter values submitted from advanced queries page and insert them into the dictionary
    if request.method == "POST":
        for key, value in fdict.items():
            if key in ("actype", "landlord", "prdelivery", "salegrade", "status", "tenure"):
                val = request.form.getlist(key)
            else:
                val = request.form.get(key) or ""
            print(key, val)
            fdict[key] = val
    filtr = []
    # now iterate through all key values - this can surely be refactored?
    for key, value in fdict.items():
        if key == "rentcode" and value and value != "":
            filtr.append(Rent.rentcode.startswith([value]))
        elif key == "agentdetail" and value and value != "":
            filtr.append(Agent.detail.ilike('%{}%'.format(value)))
        # elif key == "propaddr" and value and value != "":
        #     filtr.append()
        elif key == "source" and value and value != "":
            filtr.append(Rent.source.ilike('%{}%'.format(value)))
        elif key == "tenantname" and value and value != "":
            filtr.append(Rent.tenantname.ilike('%{}%'.format(value)))
        elif key == "actype":
            if value and value != "" and value != [] and value != ["all actypes"]:
                ids = []
                for i in range(len(value)):
                    ids.append(AcTypes.get_id(value[i]))
                filtr.append(Rent.actype_id.in_(ids))
            else: fdict[key] = ["all actypes"]
        elif key == "agentmailto":
            if value and value == "exclude":
                filtr.append(Rent.mailto_id.notin_(1, 2))
            elif key == "agentmailto" and value and value == "only":
                filtr.append(Rent.mailto_id.in_(1, 2))
            else: fdict[key] = "include"
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
        elif key == "enddate" and value and value != "":
            filtr.append(Rent.lastrentdate <= strToDate('{}'.format(value)))
        elif key == "landlord":
            if value and value != "" and value != [] and value != ["all landlords"]:
                filtr.append(Landlord.name.in_(value))
            else: fdict[key] = ["all landlords"]
        elif key == "prdelivery":
            if value and value != "" and value != [] and value != ["all prdeliveries"]:
                ids = []
                for i in range(len(value)):
                    ids.append(PrDeliveryTypes.get_id(value[i]))
                    filtr.append(Rent.prdelivery_id.in_(ids))
            else: fdict[key] = ["all prdeliveries"]
        # elif key == "rentpa" and value and value != "":
        #     filtr.append(Rent.rentpa == strToDec('{}'.format(value)))
        # elif key == "rentperiods" and value and value != "":
        #     filtr.append(Rent.rentpa == strToDec('{}'.format(value)))
        elif key == "salegrade":
            if value and value != "" and value != [] and value != ["all salegrades"]:
                ids = []
                for i in range(len(value)):
                    ids.append(SaleGrades.get_id(value[i]))
                    filtr.append(Rent.salegrade_id.in_(ids))
            else:
                fdict[key] = ["all salegrades"]
        elif key == "status":
            if value and value != "" and value != [] and value != ["all statuses"]:
                ids = []
                for i in range(len(value)):
                    ids.append(Statuses.get_id(value[i]))
                filtr.append(Rent.status_id.in_(ids))
            else:
                fdict[key] = ["all statuses"]
        elif key == "tenure":
            if value and value != "" and value != [] and value != ["all tenures"]:
                ids = []
                for i in range(len(value)):
                    ids.append(Tenures.get_id(value[i]))
                    filtr.append(Rent.tenure_id.in_(ids))
            else:
                fdict[key] = ["all tenures"]

    return filtr, fdict

