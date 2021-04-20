from app import db
from sqlalchemy.orm import contains_eager,load_only
from app.dao.database import commit_to_database
from app.models import Property, Rent


def get_props(filtr):
    return db.session.query(Property).join(Rent).options(
        contains_eager('rent').load_only('rentcode')) \
        .filter(*filtr).order_by(Property.propaddr).limit(20).all()


def get_props_all():
    return db.session.query(Property).join(Rent).options(
        contains_eager('rent').load_only('rentcode')) \
        .order_by(Property.propaddr).limit(20).all()


def get_prop(prop_id):
    return db.session.query(Property).filter_by(id=prop_id).one()


def get_propaddrs(rent_id):
    return db.session.query(Property).filter_by(rent_id=rent_id).options(load_only('propaddr')).all()


def post_prop(property):
    db.session.add(property)
    db.session.flush()
    prop_id = property.id
    commit_to_database()

    return prop_id
