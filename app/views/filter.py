from flask import redirect, render_template,  request
from flask_login import login_required
from app.views import bp
from app.dao.common import get_combodict
from app.dao.filter import get_filters, get_rent_s


@bp.route('/load_filter', methods=['GET', 'POST'])
def load_filter():
    # load predefined filters from jstore for queries
    jfilters = get_filters(2)

    return render_template('load_filter.html', jfilters=jfilters)


@bp.route('/queries/<int:id>', methods=['GET', 'POST'])
def queries(id):
    # allows the selection of rent objects using multiple filter inputs for query and pr_query
    action = request.args.get('action', "query", type=str)
    combodict = get_combodict("enhanced")
    #gather combobox values, with "all" added as an option, in a dictionary
    filterdict, rent_s = get_rent_s(action, id)
    #gather filter values and selected rent objects in two dictionaries

    return render_template('queries.html', action=action, combodict=combodict, filterdict=filterdict,
                                             rent_s=rent_s)
