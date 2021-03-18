from app import db
from flask import request
from sqlalchemy.orm import joinedload, load_only
from app.dao.database import commit_to_database
from app.main.common import get_proptype, get_proptype_id, get_proptypes
from app.models import Property, Rent


def get_properties(rent_id):
    qfilter = []
    if request.method == "POST":
        rentcode = request.form.get("rentcode")
        if rentcode and rentcode != "":
            qfilter.append(Rent.rentcode.startswith([rentcode]))
        address = request.form.get("address")
        if address and address != "":
            qfilter.append(Property.propaddr.ilike('%{}%'.format(address)))
        # p_type_id = get_proptype_id(request.form.get("proptype"))
        # if rentcode and rentcode != "":
        #     qfilter.append(Property.proptype_id == p_type_id)
    elif rent_id != 0:
        qfilter.append(Property.rent_id == rent_id)
    properties = db.session.query(Property).options(joinedload('rent').load_only('rentcode')) \
        .filter(*qfilter).order_by(Property.propaddr).limit(50).all()
    for property in properties:
        property.proptype = get_proptype(property.proptype_id)
    proptypes = get_prop_types("plus")

    return properties, proptypes


def get_property(propertyid, rent_id):
    if propertyid == 0:
        rentcode = db.session.query(Rent).filter_by(id=rent_id).options(load_only('rentcode')).one_or_none()[0]
        return {"id": 0, "rentcode": rentcode, "rent_id": rent_id, "proptype_id": 4}
    else:
        return db.session.query(Property).filter_by(id=propertyid).one()


def get_propertyaddrs(rent_id):
    return db.session.query(Property).filter_by(rent_id=rent_id).options(load_only('propaddr')).all()


def get_prop_types(type):
    proptypes = get_proptypes()
    if type == "plus":
        # add "all" as an option
        proptypes.insert(0, "all proptypes")

    return proptypes


def post_property(propertyid, rent_id):
    if propertyid == 0:
        property = Property()
        property.rent_id = rent_id
    else:
        property = Property.query.get(propertyid)
    propaddr = request.form.get("propaddr")
    property.propaddr = propaddr
    property.proptype_id = get_proptype_id(request.form.get("proptype"))
    db.session.add(property)
    db.session.flush()
    propertyid = property.id
    commit_to_database()

    return propertyid



