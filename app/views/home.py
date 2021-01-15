from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from app.dao.filter import get_rentobjects
from app.dao.property import get_properties, get_property, post_property, get_proptypes

ho_bp = Blueprint('ho_bp', __name__)

@ho_bp.route('/', methods=['GET', 'POST'])
@ho_bp.route('/home', methods=['GET', 'POST'])
# @login_required
def home():
    filterdict, rentobjects = get_rentobjects("basic", 0)

    return render_template('home.html', filterdict=filterdict, rentobjects=rentobjects)

@ho_bp.route('/properties/<int:rentid>', methods=['GET', 'POST'])
# @login_required
def properties(rentid):
    properties, proptypes = get_properties(rentid)
    print(rentid)

    return render_template('properties.html', rentid=rentid, properties=properties, proptypes=proptypes)

@ho_bp.route('/property/<int:id>', methods=["GET", "POST"])
# @login_required
def property(id):
    if request.method == "POST":
        id = post_property(id)
        return redirect(url_for('ho_bp.property', id=id))
    property = get_property(id) if id != 0 else {"id": 0, "proptype": "house"}
    proptypes = get_proptypes("basic")


    return render_template('property.html', property=property, proptypes=proptypes)
