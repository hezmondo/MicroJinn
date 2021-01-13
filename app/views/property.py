from flask import redirect, render_template,  request
from flask_login import login_required
from app.views import bp
from app.dao.property import get_property


@bp.route('/properties', methods=['GET', 'POST'])
# @login_required
def properties():
    properties = None

    return render_template('properties.html', properties=properties)


@bp.route('/property/<int:id>', methods=["GET", "POST"])
# @login_required
def property(id):
    property, proptypes, proptype = get_property(id)

    return render_template('property.html', property=property, proptypes=proptypes, proptype=proptype)
