from app import db
from flask import request
from app.dao.functions import commit_to_database

from app.models import Property, Typeproperty


def get_property(id):
    if id == 0:
        property = Property()
        property.id = 0
        property.typeprop_id = 4
    else:
        property = Property.query.get(id)
    if request.method == "POST":
        property = post_property(property)
    proptypes = [value for (value,) in Typeproperty.query.with_entities(Typeproperty.proptypedet).all()]
    proptypeid = property.typeprop_id
    proptype = Typeproperty.query.with_entities(Typeproperty.proptypedet).filter \
                    (Typeproperty.id == proptypeid).one()[0]
    return property, proptypes, proptype


def post_property(property):
    propaddr = request.form.get("propaddr")
    property.propaddr = propaddr
    proptype = request.form.get("proptype")
    property.typeprop_id = Typeproperty.query.with_entities(Typeproperty.id).filter \
            (Typeproperty.proptypedet == proptype).one()[0]
    db.session.add(property)
    commit_to_database()
    property = Property.query.filter(Property.propaddr == propaddr).first()

    return property



