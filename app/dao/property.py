from app import db
from flask import request
from app.dao.functions import commit_to_database
from app.models import Property, Rent, Typeproperty


def get_properties(rentid):
    qfilter = []
    if rentid != 0:
        qfilter.append(Property.rent_id == rentid)
    if request.method == "POST":
        rentcode = request.form.get("rentcode")
        if rentcode and rentcode != "":
            qfilter.append(Rent.rentcode.startswith([rentcode]))
        address = request.form.get("address")
        if address and address != "":
            qfilter.append(Property.propaddr.ilike('%{}%'.format(address)))
        proptype = request.form.get("proptype")
        if rentcode and rentcode != "":
            qfilter.append(Typeproperty.detail.ilike('%{}%'.format(proptype)))

    properties = Property.query.join(Rent).join(Typeproperty).with_entities(Property.id, Property.rent_id,
                    Rent.rentcode, Property.propaddr, Typeproperty.detail) \
            .filter(*qfilter).order_by(Property.propaddr).limit(50).all()
    proptypes = get_proptypes("plus")

    return properties, proptypes


def get_property(id):
    property = Property.query.join(Rent).join(Typeproperty).with_entities(Property.propaddr, Property.id, Typeproperty.detail,
                               Property.rent_id, Rent.rentcode, ) \
        .filter(Property.id == id).one_or_none()

    return property


def get_proptypes(type):
    proptypes = [value for (value,) in Typeproperty.query.with_entities(Typeproperty.detail).all()]
    if type == "plus":
        # add "all" as an option
        proptypes.insert(0, "all proptypes")

    return proptypes


def post_property(id):
    propaddr = request.form.get("propaddr")
    property = Property() if id == 0 else Property.query.get(id)
    property.propaddr = propaddr
    proptype = request.form.get("proptype")
    property.typeprop_id = Typeproperty.query.with_entities(Typeproperty.id).filter \
            (Typeproperty.detail == proptype).one()[0]
    db.session.add(property)
    db.session.flush()
    _id = property.id
    commit_to_database()

    return _id



