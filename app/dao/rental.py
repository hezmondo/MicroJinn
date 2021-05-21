import datetime
import sqlalchemy
from flask import request
from sqlalchemy import func
from app import db
from app.main.functions import strToDate
from app.modeltypes import AdvArr, Freqs
from app.models import Rental, RentalStat


def get_rental(rental_id):
    # This method returns "rental"; information about a rental
    rental = db.session.query(Rental).filter_by(id=rental_id).first()
    rental.freqdet= Freqs.get_name(rental.freq_id)

    return rental


def getrentals():
    rentals = Rental.query.all()
    rentsum = Rental.query.with_entities(func.sum(Rental.rentpa).label('totrent')).filter().first()[0]

    return rentals, rentsum


def get_rentalstatement(rental_id):
    today = datetime.date.today()
    db.session.execute(sqlalchemy.text("CALL pop_rental_statement(:x, :y)"), params={'x': rental_id, 'y': today })
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
    rental.freq_id = Freqs.get_id(request.form.get("frequency"))
    advarrdet = request.form.get("advarr")
    rental.advarr_id = AdvArr.get_id(advarrdet)
    db.session.add(rental)
    db.session.flush()
    rental_id = rental.id
    db.session.commit()

    return rental_id
