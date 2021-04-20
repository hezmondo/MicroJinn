from flask import request
from app.dao.property import get_prop, get_props, get_props_all, post_prop
from app.models import Property, Rent
from app.modeltypes import PropTypes


def mget_properties_dict():
    return {'address': request.form.get('address') or "",
            'rentcode': request.form.get('rentcode') or "",
            'proptype': request.form.get('proptype') or ""}


def mget_filter():
    filtr = []
    fdict = mget_properties_dict()
    if fdict.get('address'):
        filtr.append(Property.propaddr.ilike('%{}%'.format(fdict.get('address'))))
    if fdict.get('rentcode'):
        filtr.append(Rent.rentcode.startswith([fdict.get('rentcode')]))
    if fdict.get('proptype') and fdict.get('proptype') != 'all proptypes':
        filtr.append(Property.proptype_id == PropTypes.get_id(fdict['proptype']))

    return fdict, filtr


def mget_filter_rent_id(rent_id):
    return [Property.rent_id == rent_id]


def mget_properties_from_filter(filtr):
    return mget_properties_with_type_names(get_props(filtr))


def mget_properties_all():
    return mget_properties_with_type_names(get_props_all())


def mget_properties_from_rent_id(rent_id):
    return mget_properties_with_type_names(get_props([Property.rent_id == rent_id]))


def mget_property(prop_id, rent_id):
    if prop_id == 0:
        property = {"id": 0, "rentcode": '', "rent_id": rent_id, "proptype": "house"}
    else:
        property = get_prop(prop_id)
        property.proptype = PropTypes.get_name(property.proptype_id)

    return property


def mget_properties_with_type_names(properties):
    for property in properties:
        property.proptype = PropTypes.get_name(property.proptype_id)

    return properties


def mpost_new_property(rent_id, propaddr, proptype_id):
    property = Property()
    property.rent_id = rent_id
    property.propaddr = propaddr
    property.proptype_id = proptype_id
    prop_id = post_prop(property)

    return prop_id


def mpost_property(prop_id, propaddr, proptype_id):
    property = get_prop(prop_id)
    property.propaddr = propaddr
    property.proptype_id = proptype_id
    prop_id = post_prop(property)

    return prop_id
