from app import db
from flask import request
from app.dao.functions import commit_to_database
from app.models import Property, Rent, TypeProperty


def get_properties(rent_id):
    qfilter = []
    if rent_id != 0:
        qfilter.append(Property.rent_id == rent_id)
    if request.method == "POST":
        rentcode = request.form.get("rentcode")
        if rentcode and rentcode != "":
            qfilter.append(Rent.rentcode.startswith([rentcode]))
        address = request.form.get("address")
        if address and address != "":
            qfilter.append(Property.propaddr.ilike('%{}%'.format(address)))
        proptype = request.form.get("proptype")
        if rentcode and rentcode != "":
            qfilter.append(TypeProperty.detail.ilike('%{}%'.format(proptype)))

    properties = Property.query.join(Rent).join(TypeProperty).with_entities(Property.id, Property.rent_id,
                                                                            Rent.rentcode, Property.propaddr, TypeProperty.detail) \
            .filter(*qfilter).order_by(Property.propaddr).limit(50).all()
    proptypes = get_proptypes("plus")

    return properties, proptypes


def get_property(id, rent_id):
    if id == 0:
        rentcode = Rent.query.with_entities(Rent.rentcode) \
            .filter(Rent.id==rent_id).one_or_none()[0]
        property_ = {"id": 0, "rentcode": rentcode, "rent_id": rent_id, "typeprop_id": 4}
    else:
        property_ = Property.query.join(Rent).join(TypeProperty).with_entities(Property.propaddr, Property.id, TypeProperty.detail,
                                                                               Property.rent_id, Rent.rentcode, ) \
            .filter(Property.id == id).one_or_none()

    return property_


def get_proptypes(type):
    proptypes = [value for (value,) in TypeProperty.query.with_entities(TypeProperty.detail).all()]
    if type == "plus":
        # add "all" as an option
        proptypes.insert(0, "all proptypes")

    return proptypes


def post_property(property_id, rent_id):
    if property_id == 0:
        property = Property()
        property.rent_id = rent_id
    else:
        property = Property.query.get(property_id)
    propaddr = request.form.get("propaddr")
    property.propaddr = propaddr
    proptype = request.form.get("proptype")
    property.typeprop_id = TypeProperty.query.with_entities(TypeProperty.id).filter \
            (TypeProperty.detail == proptype).one()[0]
    db.session.add(property)
    db.session.flush()
    property_id = property.id
    commit_to_database()

    return property_id



