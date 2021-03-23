from flask import Blueprint, render_template, redirect, request, url_for
from flask_login import login_required
from app.dao.common import get_filters
from app.dao.rent import get_rent_external
from app.main.common import get_combodict_filter, get_combodict_rent
from app.main.rent import get_rentp, get_rents_advanced, get_rents_basic, get_rents_external, get_rent_strings, \
    rent_validation, update_rent_rem, update_tenant

rent_bp = Blueprint('rent_bp', __name__)


@rent_bp.route('/load_filter', methods=['GET', 'POST'])
def load_filter():
    # load predefined filters from jstore for filter
    jfilters = get_filters(2)

    return render_template('load_filter.html', jfilters=jfilters)


@rent_bp.route('/rent/<int:rent_id>', methods=['GET', 'POST'])
# @login_required
def rent(rent_id):
    message = request.args.get('message', '', type=str)
    if request.method == "POST":
        rent_id = update_rent_rem(rent_id)
        return redirect(url_for('rent_bp.rent', rent_id=rent_id))
    combodict = get_combodict_rent()
    # gather rent combobox values
    rent = get_rentp(rent_id) if rent_id != 0 else {"id": 0}    # get full enhanced rent pack
    # basic validation check for mail and email variables
    messages = rent_validation(rent, message)
    rentstats = get_rent_strings(rent, 'rent')

    return render_template('rent.html', rent=rent, combodict=combodict, rentstats=rentstats, messages=messages)


@rent_bp.route('/', methods=['GET', 'POST'])
@rent_bp.route('/rents_basic', methods=['GET', 'POST'])
@login_required
def rents_basic():  # get rents_basic for home rents_basic page with simple search option
    fdict, rents = get_rents_basic()

    return render_template('rents_basic.html', fdict=fdict, rents=rents)


@rent_bp.route('/rent_external/<int:rent_external_id>', methods=["GET"])
@login_required
def rent_external(rent_external_id):  # view external rent from home rents page
    rent_external = get_rent_external(rent_external_id)

    return render_template('rent_external.html', rent_external=rent_external)


@rent_bp.route('/rents_advanced/<int:filtr_id>', methods=['GET', 'POST'])
@login_required
def rents_advanced(filtr_id):  # get rents for advanced queries page and pr page
    action = request.args.get('action', "query", type=str)
    combodict = get_combodict_filter()    # get combobox values with "all" added as an option
    fdict, rents = get_rents_advanced(action, filtr_id)   # get filter values and rent objects

    return render_template('rents_advanced.html', action=action, combodict=combodict, filtr_id=filtr_id,
                           fdict=fdict, rents=rents)


@rent_bp.route('/rents_external', methods=['GET', 'POST'])
@login_required
def rents_external():  # get external rents for home rents page with simple search option
    fdict, rents = get_rents_external()

    return render_template('rents_external.html', fdict=fdict, rents=rents)


@rent_bp.route('/tenant/<int:rent_id>', methods=['GET', 'POST'])
# @login_required
def tenant(rent_id):    # update tenant details from rent page
    update_tenant(rent_id)

    return redirect(url_for('rent_bp.rent', rent_id=rent_id))
