from app import db
from datetime import date
from flask import request
from app.dao.functions import commit_to_database, strToDec

from app.models import Charge, Chargetype, Rent\


def delete_charge(charge_id):
    Charge.query.filter_by(id=charge_id).delete()
    commit_to_database()


def get_charge(charge_id):
    rentcode = request.args.get('rentcode', "XNEWX" , type=str)
    rent_id = int(request.args.get('rent_id', "0", type=str))
    # new charge has id = 0
    if charge_id == 0:
        charge = {
            'id': 0,
            'rent_id': rent_id,
            'rentcode': rentcode,
            'chargedesc': "notice fee",
            'chargestartdate': date.today()
        }
    else:
        charge = \
            Charge.query.join(Rent).join(Chargetype).with_entities(Charge.id, Rent.id.label("rent_id"), Rent.rentcode,
                   Chargetype.chargedesc, Charge.chargestartdate, Charge.chargetotal, Charge.chargedetail,
                       Charge.chargebalance) \
                    .filter(Charge.id == charge_id).one_or_none()
    chargedescs = [value for (value,) in Chargetype.query.with_entities(Chargetype.chargedesc).all()]

    return charge, chargedescs


def get_charges(rent_id):
    qfilter = []
    if request.method == "POST":
        rcd = request.form.get("rentcode") or ""
        cdt = request.form.get("chargedetail") or ""
        qfilter.append(Rent.rentcode.startswith([rcd]))
        qfilter.append(Charge.chargedetail.ilike('%{}%'.format(cdt)))
    elif rent_id != "0":
        qfilter.append(Charge.rent_id == rent_id)

    charges = Charge.query.join(Rent).join(Chargetype).with_entities(Charge.id, Rent.rentcode, Chargetype.chargedesc,
                     Charge.chargestartdate, Charge.chargetotal, Charge.chargedetail, Charge.chargebalance) \
            .filter(*qfilter).order_by(Rent.rentcode).all()

    return charges


def post_charge(charge_id):
    # new charge for id 0, otherwise existing charge:
    if charge_id == 0:
        charge = Charge()
        charge.id = 0
        charge.rent_id = int(request.form.get("rent_id"))
    else:
        charge = Charge.query.get(charge_id)
    charge.chargetype_id = \
        Chargetype.query.with_entities(Chargetype.id).filter(
            Chargetype.chargedesc == request.form.get("chargedesc")).one()[0]
    charge.chargestartdate = request.form.get("chargestartdate")
    charge.chargetotal = strToDec(request.form.get("chargetotal"))
    charge.chargedetail = request.form.get("chargedetail")
    charge.chargebalance = strToDec(request.form.get("chargebalance"))
    db.session.add(charge)
    db.session.flush()
    rent_id = charge.rent_id
    db.session.commit()

    return rent_id
