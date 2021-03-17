import sqlalchemy
from app import db
from flask import request
from sqlalchemy import func
from app.main.common import get_advarr_id, get_advarr_types, get_freq, get_freq_id, get_freqs
from app.models import Rental, RentalStat


def get_rental(rental_id):
    # This method returns "rental"; information about a rental and the list values for various comboboxes,
    rental = db.session.query(Rental).filter_by(id=rental_id).first()
    rental.freqdet= get_freq(rental.freq_id)
    advarrdets = get_advarr_types()
    freqdets = get_freqs()

    return rental, advarrdets, freqdets


def getrentals():
    rentals = Rental.query.all()
    rentsum = Rental.query.with_entities(func.sum(Rental.rentpa).label('totrent')).filter().first()[0]

    return rentals, rentsum


def get_rentalstatement(rental_id):
    db.session.execute(sqlalchemy.text("CALL pop_rental_statement(:x)"), params={"x": rental_id})
    db.session.commit()
    rentalstatement = RentalStat.query.all()

    return rentalstatement


def post_rental(rental_id):
    if rental_id == 0:
        rental = Rental()
    else:
        rental = Rental.query.get(rental_id)
    rental.propaddr = request.form.get("propaddr")
    rental.tenantname = request.form.get("tenantname")
    rental.rentpa = request.form.get("rentpa")
    rental.arrears = request.form.get("arrears")
    rental.startrentdate = request.form.get("startrentdate")
    if rental.astdate:
        rental.astdate = request.form.get("astdate")
    rental.lastgastest = request.form.get("lastgastest")
    rental.note = request.form.get("note")
    rental.freq_id = get_freq_id(request.form.get("frequency"))
    advarrdet = request.form.get("advarr")
    rental.advarr_id = get_advarr_id(advarrdet)
    db.session.add(rental)
    db.session.flush()
    rental_id = rental.id
    db.session.commit()

    return rental_id
