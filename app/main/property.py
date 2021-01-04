from app import db
from flask import request
from app.main.functions import commit_to_database

from app.models import Property, Typeproperty


def get_property(id):
    property = Property.query.join(Typeproperty).with_entities(Property.id, Property.propaddr,
                   Typeproperty.proptypedet).filter(Property.id == id).one_or_none()
    proptypedets = [value for (value,) in Typeproperty.query.with_entities(Typeproperty.proptypedet).all()]

    return property, proptypedets


def post_property(id, action):
    if action == "edit":
        property = Property.query.get(id)
    else:
        property = Property()
    property.propaddr = request.form.get("propaddr")
    proptypedet = request.form.get("proptypedet")
    property.typeprop_id = \
        Typeproperty.query.with_entities(Typeproperty.id).filter \
            (Typeproperty.proptypedet == proptypedet).one()[0]
    db.session.add(property)
    db.session.commit()
    id_ = property.id

    return id_



