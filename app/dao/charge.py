from app import db
from datetime import date
from flask import request
from app.main.functions import strToDec
from sqlalchemy import func
from app.models import Charge, ChargeType, Rent


def add_charge(rent_id, recovery_charge_amount, chargetype_id, charge_details):
    new_charge = Charge(chargetype_id=chargetype_id, chargestartdate=date.today(),
                        chargetotal=recovery_charge_amount, chargedetail=charge_details,
                        chargebalance=recovery_charge_amount, rent_id=rent_id)
    db.session.add(new_charge)
    db.session.flush()
    return new_charge.id


def get_charge(charge_id):
    rentcode = request.args.get('rentcode', "XNEWX", type=str)
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
            Charge.query.join(Rent).join(ChargeType).with_entities(Charge.id, Rent.id.label("rent_id"), Rent.rentcode,
                                                                   ChargeType.chargedesc, Charge.chargestartdate,
                                                                   Charge.chargetotal, Charge.chargedetail,
                                                                   Charge.chargebalance) \
                .filter(Charge.id == charge_id).one_or_none()
    chargedescs = [value for (value,) in ChargeType.query.with_entities(ChargeType.chargedesc).all()]

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

    charges = Charge.query.join(Rent).join(ChargeType).with_entities(Charge.id, Rent.rentcode, ChargeType.chargedesc,
                                                                     Charge.chargestartdate, Charge.chargetotal,
                                                                     Charge.chargedetail, Charge.chargebalance) \
        .filter(*qfilter).order_by(Rent.rentcode).all()

    return charges


def get_charge_start_date(rent_id):
    return db.session.execute(func.mjinn.newest_charge(rent_id)).scalar()


def get_charge_type(chargetype_id):
    return db.session.query(ChargeType.chargedesc).filter_by(id=chargetype_id).scalar()


# TODO: Can refactor this into get_charges()
def get_rent_charge_details(rent_id):
    qfilter = [Charge.rent_id == rent_id]
    charges = Charge.query.join(Rent).join(ChargeType).with_entities(Charge.id, Rent.rentcode, ChargeType.chargedesc,
                                                                     Charge.chargestartdate, Charge.chargetotal,
                                                                     Charge.chargedetail, Charge.chargebalance) \
        .filter(*qfilter).all()
    return charges


def get_total_charges(rent_id):
    return Charge.query.with_entities(Charge.chargetotal).filter_by(rent_id=rent_id).all()


def post_charge(charge_id):
    # new charge for id 0, otherwise existing charge:
    if charge_id == 0:
        charge = Charge()
        charge.id = 0
        charge.rent_id = int(request.form.get("rent_id"))
    else:
        charge = Charge.query.get(charge_id)
    charge.chargetype_id = \
        ChargeType.query.with_entities(ChargeType.id).filter(
            ChargeType.chargedesc == request.form.get("chargedesc")).one()[0]
    charge.chargestartdate = request.form.get("chargestartdate")
    charge.chargetotal = strToDec(request.form.get("chargetotal"))
    charge.chargedetail = request.form.get("chargedetail")
    charge.chargebalance = strToDec(request.form.get("chargebalance"))
    db.session.add(charge)
    db.session.flush()
    rent_id = charge.rent_id
    db.session.commit()

    return rent_id
