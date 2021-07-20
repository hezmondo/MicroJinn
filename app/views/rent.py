from flask import Blueprint, render_template, redirect, request, url_for
from flask_login import login_required
from app import db
from app.dao.common import get_filters
from app.dao.rent import delete_rent_filter, get_rent_external
from app.main.common import get_combodict_rent, mpost_search
from app.main.rent import collect_rents_advanced_html_elements, get_rentp, mget_recent_searches, get_rents_basic_sql, \
    mget_rents_errors_list, get_rents_external, rent_validation, update_landlord, update_rent_rem, \
    update_tenant, mpost_rent_filter, mget_rents_advanced, mget_rents_advanced_from_search
from app.main.rent_filter import dict_advanced
rent_bp = Blueprint('rent_bp', __name__)


@rent_bp.route('/delete_filter<int:item_id>', methods=['GET', 'POST'])
def delete_filter(item_id):
    method = request.args.get('method')
    delete_rent_filter(item_id)
    if method == 'payrequest':
        return redirect(url_for('pr_bp.pr_start'))
    else:
        return redirect(url_for('rent_bp.rents_advanced', filtr_id=0, method=method))


@rent_bp.route('/load_filter', methods=['GET', 'POST'])
def load_filter():
    # load predefined filters from jstore for filter
    jfilters = get_filters(2)

    return render_template('load_filter.html', jfilters=jfilters)


@rent_bp.route('/rent/<int:rent_id>', methods=['GET', 'POST'])
# @login_required
def rent(rent_id):
    nav = request.args.get('nav', '', type=str)
    nav_id = request.args.get('nav_id', type=int)
    message = request.args.get('message', '', type=str)
    combodict = get_combodict_rent()
    # gather rent combobox values
    rent = get_rentp(rent_id) if rent_id != 0 else {"id": 0}    # get full enhanced rent pack
    # basic validation check for mail and email variables
    messages = rent_validation(rent, message)

    return render_template('rent.html', rent=rent, combodict=combodict, messages=messages, nav=nav, nav_id=nav_id)


@rent_bp.route('/rent_external/<int:rent_external_id>', methods=["GET"])
@login_required
def rent_external(rent_external_id):  # view external rent from home rents page
    rent_external = get_rent_external(rent_external_id)

    return render_template('rent_external.html', rent_external=rent_external)


@rent_bp.route('/rents_advanced/<int:filtr_id>', methods=['GET', 'POST'])
@login_required
def rents_advanced(filtr_id):  # get rents for advanced queries page and pr page
    message = request.args.get('message', '', type=str)
    action = request.args.get('action', 'query', type=str)
    method = request.args.get('method', 'rent', type=str)
    rents = []
    if request.method == 'POST':
        if action == 'save':
            try:
                filtr_id = mpost_rent_filter()
                message = "Filter saved successfully."
            except Exception as ex:
                message = f"Unable to save filter. Database rolled back. Error: {str(ex)}"
                db.sesssion.rollback()
            return redirect(url_for('rent_bp.rents_advanced', filtr_id=filtr_id, action='load', method=method,
                                    message=message))
        else:
            fdict, rents = mget_rents_advanced_from_search()
    if action == 'load':
        fdict, rents = mget_rents_advanced(filtr_id)
    else:
        fdict = dict_advanced()
    rents, are_errors = mget_rents_errors_list(rents)
    combodict, fdict, jfilters, pr_defaults, pr_template_codes = collect_rents_advanced_html_elements(fdict, method)
    return render_template('rents_advanced.html', action=action, combodict=combodict, filtr_id=filtr_id,
                           fdict=fdict, jfilters=jfilters, method=method, pr_defaults=pr_defaults,
                           pr_template_codes=pr_template_codes, rents=rents, are_errors=are_errors,
                           message=message)


@rent_bp.route('/', methods=['GET', 'POST'])
@rent_bp.route('/rents_basic', methods=['GET', 'POST'])
@login_required
def rents_basic():  # get rents_basic for home rents_basic page with simple search option
    fdict, rents = get_rents_basic_sql()
    if request.method == "POST":
        # We save the search if it is not already in the recent_search table and if there are values in the dictionary
        if not all(value == '' for value in fdict.values()):
            mpost_search(fdict, 'rent')
    recent_searches = mget_recent_searches('rent')
    return render_template('rents_basic.html', fdict=fdict, rents=rents, recent_searches=recent_searches)


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


# update rent details from rent page based on action (from tenant/landlord/edit_rent modal)
@rent_bp.route('/rent_update/<int:rent_id>', methods=['GET', 'POST'])
# @login_required
def rent_update(rent_id):
    action = request.args.get('action', type=str)
    message = ''
    try:
        if action == 'landlord':
            update_landlord(rent_id)
        elif action == 'tenant':
            update_tenant(rent_id)
        elif action == 'rent':
            update_rent_rem(rent_id)
    except Exception as ex:
        message = f"Update rent failed. Database rolled back. Error:  {str(ex)}"
        db.session.rollback()
    return redirect(url_for('rent_bp.rent', rent_id=rent_id, message=message))