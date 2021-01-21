from flask import Blueprint, redirect, render_template,  request
from flask_login import login_required
from app.dao.filter import get_filters
from app.dao.payrequest import get_pr_data, get_pr_forms, get_pr_file, get_pr_history, post_pr_file
from app.dao.mail import write_payrequest

pr_bp = Blueprint('pr_bp', __name__)


@pr_bp.route('/pr_dialog/<int:rent_id>', methods=["GET", "POST"])
@login_required
def pr_dialog(rent_id):
    pr_forms = get_pr_forms()

    return render_template('pr_dialog.html', pr_forms=pr_forms, rent_id=id)


@pr_bp.route('/pr_edit/<int:pr_form_id>', methods=["GET", "POST"])
@login_required
def pr_edit(pr_form_id):
    if request.method == "POST":
        method = request.args.get('method', "email", type=str)
        rent_id = request.form.get('rent_id')
        # TODO: Avoid passing both totdue and totdue_string - include money formatting in html template?
        # TODO: All hidden variables can be passed in a single json object
        block, pr_data, rent_pr, table_rows, totdue_string = write_payrequest(rent_id, pr_form_id)

        mailaddr = request.form.get('mailaddr')
        summary = pr_data.get('pr_code') + "-" + method + "-" + mailaddr[0:25]
        mailaddr = mailaddr.split(", ")

        pr_data = get_pr_data(pr_data)

        return render_template('mergedocs/PR.html', pr_data=pr_data, block=block, mailaddr=mailaddr,
                               method=method, rent_pr=rent_pr, summary=summary, table_rows=table_rows,
                               totdue_string=totdue_string)


# TODO: improve pr_file editing functionality (beyond edit summary/block)
@pr_bp.route('/pr_file/<int:pr_id>', methods=['GET', 'POST'])
@login_required
def pr_file(pr_id):
    if request.method == "POST":
        rent_id = post_pr_file(pr_id)

        return redirect('/pr_history/{}'.format(rent_id))

    pr_file = get_pr_file(pr_id)

    return render_template('pr_file.html', pr_file=pr_file)


@pr_bp.route('/pr_history/<int:rent_id>', methods=['GET', 'POST'])
def pr_history(rent_id):
    pr_history = get_pr_history(rent_id)

    return render_template('pr_history.html', rent_id=rent_id, pr_history=pr_history)


# @bp.route('/pr_main/<int:id>', methods=['GET', 'POST'])
# @login_required
# def pr_main(id):
#     actypedets, floads, options, prdeliveries, salegradedets = get_queryoptions_advanced()
#     landlords, statusdets, tenuredets = get_queryoptions_common()
#     if id == 0:
#         rentprops = get_rentobjs_filter(1)
#     else:
#         rentprops = get_rentobjs_filter(id)
#
#     return render_template('pr_main.html', actypedets=actypedets, floads=floads, options=options,
#                            prdeliveries=prdeliveries, salegradedets=salegradedets, landlords=landlords,
#                            statusdets=statusdets, tenuredets=tenuredets, rentprops=rentprops)


@pr_bp.route('/pr_start', methods=['GET', 'POST'])
@login_required
def pr_start():
    filters = get_filters(1)

    return render_template('pr_start.html', filters=filters)
