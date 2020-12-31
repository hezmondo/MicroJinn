from app import db
from flask import request
from sqlalchemy import desc, func
from app.main.functions import commit_to_database
from app.models import Rental, Rental_statement, Typeadvarr, Typefreq\


def get_rental(id):
    # This method returns "rental"; information about a rental and the list values for various comboboxes,
    rental = Rental.query.join(Typeadvarr).join(Typefreq).with_entities(Rental.id, Rental.rentalcode, Rental.arrears,
                                                                        Rental.startrentdate, Rental.astdate,
                                                                        Rental.lastgastest, Rental.note,
                                                                        Rental.propaddr, Rental.rentpa,
                                                                        Rental.tenantname, Typeadvarr.advarrdet,
                                                                        Typefreq.freqdet).filter(
        Rental.id == id).one_or_none()
    advarrdets = [value for (value,) in Typeadvarr.query.with_entities(Typeadvarr.advarrdet).all()]
    freqdets = [value for (value,) in Typefreq.query.with_entities(Typefreq.freqdet).all()]
    return rental, advarrdets, freqdets


def getrentals():
    rentals = Rental.query.all()
    rentsum = Rental.query.with_entities(func.sum(Rental.rentpa).label('totrent')).filter().first()[0]

    return rentals, rentsum


def get_rentalstatement():
    rentalstatem = Rental_statement.query.all()

    return rentalstatem


def post_rental(id, action):
    if action == "edit":
        rental = Rental.query.get(id)
    else:
        rental = Rental()
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
        Typefreq.query.with_entities(Typefreq.id).filter(Typefreq.freqdet == frequency).one()[0]
    advarr = request.form.get("advarr")
    rental.advarr_id = \
        Typeadvarr.query.with_entities(Typeadvarr.id).filter(Typeadvarr.advarrdet == advarr).one()[0]
    db.session.add(rental)
    db.session.commit()
    id_ = rental.id

    return id_
