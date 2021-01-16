from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from app.dao.filter import get_rent_s
from app.dao.property import get_properties, get_property, post_property, get_proptypes

home_bp = Blueprint('home_bp', __name__)

@home_bp.route('/', methods=['GET', 'POST'])
@home_bp.route('/home', methods=['GET', 'POST'])
# @login_required
def home():
    filterdict, rent_s = get_rent_s("basic", 0)

    return render_template('home.html', filterdict=filterdict, rent_s=rent_s)

@home_bp.route('/properties/<int:rentid>', methods=['GET', 'POST'])
# @login_required
def properties(rentid):
    properties, proptypes = get_properties(rentid)
    print(rentid)

    return render_template('properties.html', rentid=rentid, properties=properties, proptypes=proptypes)

@home_bp.route('/property/<int:id>', methods=["GET", "POST"])
# @login_required
def property(id):
    rentid = int(request.args.get('rentid', "0", type=str))
    if request.method == "POST":
        id = post_property(id, rentid)

        return redirect(url_for('home_bp.property', id=id))

    property_ = get_property(id, rentid)
    proptypes = get_proptypes("basic")

    return render_template('property.html', property_=property_, proptypes=proptypes)
