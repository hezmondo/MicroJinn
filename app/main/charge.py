from app import db
from datetime import date
from flask import request
from app.main.functions import commit_to_database, strToDec

from app.models import Charge, Chargetype, Rent\


def get_charge(id):
    rentcode = request.args.get('rentcode', "XNEWX" , type=str)
    rentid = int(request.args.get('rentid', "0", type=str))
    # new charge has id = 0
    if id == 0:
        charge = {
            'id': 0,
            'rentid': rentid,
            'rentcode': rentcode,
            'chargedesc': "notice fee",
            'chargestartdate': date.today()
        }
    else:
        charge = \
            Charge.query.join(Rent).join(Chargetype).with_entities(Charge.id, Rent.id.label("rentid"), Rent.rentcode,
                   Chargetype.chargedesc, Charge.chargestartdate, Charge.chargetotal, Charge.chargedetail,
                       Charge.chargebalance) \
                    .filter(Charge.id == id).one_or_none()
    chargedescs = [value for (value,) in Chargetype.query.with_entities(Chargetype.chargedesc).all()]

    return charge, chargedescs


def get_charges(rentid):
    qfilter = []
    if request.method == "POST":
        rcd = request.form.get("rentcode") or ""
        cdt = request.form.get("chargedetail") or ""
        qfilter.append(Rent.rentcode.startswith([rcd]))
        qfilter.append(Charge.chargedetail.ilike('%{}%'.format(cdt)))
    elif rentid != "0":
        qfilter.append(Charge.rent_id == rentid)

    charges = Charge.query.join(Rent).join(Chargetype).with_entities(Charge.id, Rent.rentcode, Chargetype.chargedesc,
                     Charge.chargestartdate, Charge.chargetotal, Charge.chargedetail, Charge.chargebalance) \
            .filter(*qfilter).all()

    return charges


def post_charge(id):
    # new charge for id 0, otherwise existing charge:
    if id == 0:
        charge = Charge()
        charge.id = 0
        charge.rent_id = int(request.form.get("rentid"))
    else:
        charge = Charge.query.get(id)
    charge.chargetype_id = \
        Chargetype.query.with_entities(Chargetype.id).filter(
            Chargetype.chargedesc == request.form.get("chargedesc")).one()[0]
    charge.chargestartdate = request.form.get("chargestartdate")
    charge.chargetotal = strToDec(request.form.get("chargetotal"))
    charge.chargedetail = request.form.get("chargedetail")
    charge.chargebalance = strToDec(request.form.get("chargebalance"))
    rent_id = charge.rent_id
    db.session.add(charge)
    db.session.commit()

    return rent_id
