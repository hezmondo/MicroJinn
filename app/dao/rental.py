import sqlalchemy
from app import db
from flask import request
from sqlalchemy import func
from app.models import Rental, RentalStat, TypeAdvArr, TypeFreq\


def get_rental(rental_id):
    # This method returns "rental"; information about a rental and the list values for various comboboxes,
    rental = Rental.query.\
        join(TypeAdvArr).\
        join(TypeFreq).\
        with_entities(Rental.id, Rental.rentalcode, Rental.arrears, Rental.startrentdate, Rental.astdate,
                      Rental.lastgastest, Rental.note, Rental.propaddr, Rental.rentpa, Rental.tenantname,
                      TypeAdvArr.advarrdet, TypeFreq.freqdet) \
        .filter(Rental.id == rental_id).one_or_none()
    advarrdets = [value for (value,) in TypeAdvArr.query.with_entities(TypeAdvArr.advarrdet).all()]
    freqdets = [value for (value,) in TypeFreq.query.with_entities(TypeFreq.freqdet).all()]

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
    frequency = request.form.get("frequency")
    rental.freq_id = \
        TypeFreq.query.with_entities(TypeFreq.id).filter(TypeFreq.freqdet == frequency).one()[0]
    advarr = request.form.get("advarr")
    rental.advarr_id = \
        TypeAdvArr.query.with_entities(TypeAdvArr.id).filter(TypeAdvArr.advarrdet == advarr).one()[0]
    db.session.add(rental)
    db.session.flush()
    rental_id = rental.id
    db.session.commit()

    return rental_id
