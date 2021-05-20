from app import db
from datetime import date
from flask import request
from app.main.functions import strToDec
from sqlalchemy.orm import joinedload
from app.models import Charge, ChargeType, Rent


def add_charge(rent_id, recovery_charge_amount, chargetype_id, charge_details):
    new_charge = Charge(chargetype_id=chargetype_id, chargestartdate=date.today(),
                        chargetotal=recovery_charge_amount, chargedetail=charge_details,
                        chargebalance=recovery_charge_amount, rent_id=rent_id)
    db.session.add(new_charge)
    db.session.flush()
    return new_charge.id


def get_charge(charge_id):
    return db.session.query(Charge).filter_by(id=charge_id).one_or_none()


def get_charge_descs():
    return [value for (value,) in ChargeType.query.with_entities(ChargeType.chargedesc).all()]


def get_charges(filtr):
    return db.session.query(Charge).join(Rent) \
        .options(joinedload('rent').load_only('rentcode'),
                 joinedload('chargetype').load_only('chargedesc')) \
        .filter(*filtr).all()


def get_charge_type(chargetype_id):
    return db.session.query(ChargeType.chargedesc).filter_by(id=chargetype_id).scalar()


def get_charges_rent(rent_id):
    return db.session.query(Charge).join(Rent) \
        .options(joinedload('rent').load_only('rentcode'),
                 joinedload('chargetype').load_only('chargedesc')) \
        .filter(Charge.rent_id == rent_id).all()


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
