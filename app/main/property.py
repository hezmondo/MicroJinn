from flask import request
from app.dao.property import get_prop, get_props, post_prop
from app.models import Property, Rent
from app.modeltypes import PropTypes


def dict_search():
    return {'address': request.form.get('address') or "",
            'rentcode': request.form.get('rentcode') or "",
            'proptype': request.form.get('proptype') or "",
            }


def get_properties(rent_id):
    filtr = []
    dict = {}
    if request.method == "POST":
        dict = dict_search()
        if dict.get('address'):
            filtr.append(Property.propaddr.ilike('%{}%'.format(dict.get('address'))))
        if dict.get('rentcode'):
            filtr.append(Rent.rentcode.startswith([dict.get('rentcode')]))
        if dict.get('proptype') and dict.get('proptype') != 'all proptypes':
            filtr.append(Property.proptype_id == PropTypes.get_id(dict['proptype']))
    elif rent_id != 0:
        filtr.append(Property.rent_id == rent_id)
    properties = get_props(filtr)
    for property in properties:
        property.proptype = PropTypes.get_name(property.proptype_id)

    return properties, dict


# def get_properties(rent_id):
#     dict = {}
#     filtr = []
#     if request.method == "POST":
#         dict['address'] = request.form.get("address") or ''
#         if dict['address'] and dict['address'] != '':
#             filtr.append(Property.propaddr.ilike('%{}%'.format(dict['address'])))
#         dict['rentcode'] = request.form.get("rentcode") or ''
#         if dict['rentcode'] and dict['rentcode'] != '':
#             filtr.append(Rent.rentcode.startswith([dict.get('rentcode')]))
#         dict['proptype'] = request.form.get("proptype") or 'all proptypes'
#         if dict['proptype'] and dict['proptype'] != 'all proptypes':
#             filtr.append(Property.proptype_id==PropTypes.get_id(dict['proptype']))
#     elif rent_id != 0:
#         filtr.append(Property.rent_id == rent_id)
#     properties = get_props(filtr)
#     for property in properties:
#         property.proptype = PropTypes.get_name(property.proptype_id)
#
#     return properties, dict


def get_property(prop_id, rent_id, rentcode):
    if prop_id == 0:
        property = {"id": 0, "rentcode": rentcode, "rent_id": rent_id, "proptype": "house"}
    else:
        property = get_prop(prop_id)
        property.proptype = PropTypes.get_name(property.proptype_id)
        property.rentcode = rentcode

    return property


def post_property(prop_id, rent_id):
    if prop_id == 0:
        property = Property()
        property.rent_id = rent_id
    else:
        property = Property.query.get(prop_id)
    property.propaddr = request.form.get("propaddr")
    property.proptype_id = PropTypes.get_id(request.form.get("proptype"))
    prop_id = post_prop(property)

    return prop_id
