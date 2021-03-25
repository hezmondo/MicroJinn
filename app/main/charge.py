from app import db
from datetime import date
from flask import request
from app.main.functions import strToDec
from sqlalchemy import func
from app.dao.charge import get_charge, get_charges
from app.dao.common import get_charge_types
from app.models import Charge, ChargeType, Rent


def mget_charge(charge_id):
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
    else: charge = get_charge(charge_id)
    chargedescs = [chargetype.chargedesc for chargetype in get_charge_types()]

    return charge, chargedescs


def mget_charges(rent_id):
    filtr = []
    if request.method == "POST":
        rcd = request.form.get("rentcode") or ""
        cdt = request.form.get("chargedetail") or ""
        filtr.append(Rent.rentcode.startswith([rcd]))
        filtr.append(Charge.chargedetail.ilike('%{}%'.format(cdt)))
    elif rent_id and rent_id != "0":
        filtr.append(Charge.rent_id == rent_id)
    charges = get_charges(filtr)

    return charges


def mget_charges_rent(rent_id):
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
