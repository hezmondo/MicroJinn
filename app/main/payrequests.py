import sqlalchemy
from sqlalchemy import func, select
from app.models import Rent
from app import db
from datetime import date

def forward_rents(rentprops):
    for rent_prop in rentprops:
        rent = Rent.query.get(rent_prop.id)
        update_last_rent_date(rent)
        update_arrears(rent)
        db.session.commit()
    return


def update_arrears(rent):
    previous_arrears = rent.arrears
    rent_pa = rent.rentpa
    freq_id = rent.freq_id
    new_arrears = previous_arrears + (rent_pa / freq_id)
    rent.arrears = new_arrears
    return


# Arguments for next_rent_date: (rentid int, rentype int, periods int) RETURNS list of dates
def update_last_rent_date(rent):
    query = db.session.query(func.mjinn.next_rent_date(rent.id, 1, 1)).all()[0]
    for last_rent_date in query:
        rent.lastrentdate = last_rent_date
    return