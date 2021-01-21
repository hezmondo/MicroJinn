from flask import Blueprint, redirect, render_template,  request
from flask_login import login_required
from app.dao.common import get_combodict
from app.dao.filter import get_filters, get_rent_s

filter_bp = Blueprint('filter_bp', __name__)


@filter_bp.route('/load_filter', methods=['GET', 'POST'])
def load_filter():
    # load predefined filters from jstore for filter
    jfilters = get_filters(2)

    return render_template('load_filter.html', jfilters=jfilters)


@filter_bp.route('/filter/<int:id>', methods=['GET', 'POST'])
def filter(id):
    # allows the selection of rent objects using multiple filter inputs for query and pr_query
    action = request.args.get('action', "query", type=str)
    combodict = get_combodict("enhanced")
    #gather combobox values, with "all" added as an option, in a dictionary
    filterdict, rent_s = get_rent_s(action, id)
    #gather filter values and selected rent objects in two dictionaries

    return render_template('filter.html', action=action, combodict=combodict, filterdict=filterdict,
                                             rent_s=rent_s)
