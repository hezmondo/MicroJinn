from flask import Blueprint, redirect, render_template, request, url_for, json
from flask_login import login_required
from app.dao.common import get_filters
from app.dao.form_letter import get_pr_forms
from app.dao.payrequest import get_pr_file, get_pr_history, post_updated_payrequest
from app.main.payrequest import serialize_pr_save_data, save_new_payrequest, \
    undo_pr, write_payrequest, write_payrequest_x, write_payrequest_email

pr_bp = Blueprint('pr_bp', __name__)


@pr_bp.route('/pr_dialog/<int:rent_id>', methods=["GET", "POST"])
@login_required
def pr_dialog(rent_id):
    pr_forms = get_pr_forms()
    return render_template('pr_dialog.html', pr_forms=pr_forms, rent_id=rent_id)


@pr_bp.route('/pr_edit/<int:pr_form_id>', methods=["GET", "POST"])
@login_required
def pr_edit(pr_form_id):
    if request.method == "POST":
        rent_id = request.args.get('rent_id')
        block, pr_save_data, rent_pr, subject, table_rows = write_payrequest(rent_id, pr_form_id)
        # TODO: what property address do we use for rents with multiple properties if not the agent address?
        # propaddr = '; '.join(each.propaddr.strip() for each in rent_pr.propaddrs)
        if not rent_pr.mailaddr:
            message = 'Cannot complete payrequest, Please update mail address.'
            return redirect(url_for('rent_bp.rent', rent_id=rent_id, message=message))
        pr_save_data = serialize_pr_save_data(pr_save_data)
        return render_template('mergedocs/PR.html', pr_save_data=pr_save_data,
                               block=block, rent_pr=rent_pr, subject=subject,
                               table_rows=table_rows)


# TODO: finish next week
@pr_bp.route('/pr_edit_xray/<int:pr_form_id>', methods=["GET", "POST"])
@login_required
def pr_edit_xray(pr_form_id):
    if request.method == "POST":
        rent_id = request.args.get('rent_id')
        pr_save_data, rent_pr, table_rows = write_payrequest_x(rent_id, pr_form_id)
        pr_save_data = serialize_pr_save_data(pr_save_data)
        return render_template('mergedocs/PRX.html', pr_save_data=pr_save_data, rent_pr=rent_pr,
                               table_rows=table_rows)


# TODO: improve pr_file editing functionality (beyond edit summary/block)
@pr_bp.route('/pr_file/<int:pr_id>', methods=['GET', 'POST'])
@login_required
def pr_file(pr_id):
    method = request.args.get('method', type=str)
    if request.method == "POST":
        block = request.form.get('xinput').replace("£", "&pound;")
        rent_id = post_updated_payrequest(block, pr_id)
        return redirect(url_for('pr_bp.pr_history', rent_id=rent_id))
    pr_file = get_pr_file(pr_id)
    if method == 'email':
        pr_save_data = json.loads(request.args.get('pr_save_data'))
        email_block = write_payrequest_email(pr_save_data)
        return render_template('pr_file.html', email_block=email_block, method=method, pr_file=pr_file)
    return render_template('pr_file.html', pr_file=pr_file)


@pr_bp.route('/pr_history/<int:rent_id>', methods=['GET', 'POST'])
@login_required
def pr_history(rent_id):
    message = request.args.get('message', type=str)
    pr_history = get_pr_history(rent_id)
    return render_template('pr_history.html', rent_id=rent_id, pr_history=pr_history, message=message)


# @bp.route('/pr_main/<int:id>', methods=['GET', 'POST'])
# @login_required
# def pr_main(id):
#     actypes, floads, options, prdeliveries, salegradedets = get_queryoptions_advanced()
#     landlords, statusdets, tenuredets = get_queryoptions_common()
#     if id == 0:
#         rentprops = get_rentobjs_filter(1)
#     else:
#         rentprops = get_rentobjs_filter(id)
#
#     return render_template('pr_main.html', actypes=actypes, floads=floads, options=options,
#                            prdeliveries=prdeliveries, salegradedets=salegradedets, landlords=landlords,
#                            statusdets=statusdets, tenuredets=tenuredets, rentprops=rentprops)


@pr_bp.route('/pr_save_send', methods=['GET', 'POST'])
@login_required
def pr_save_send():
    method = request.args.get('method', type=str)
    if request.method == 'POST':
        pr_id, pr_save_data, rent_id = save_new_payrequest(method)
        if method == 'post':
            return redirect(url_for('pr_bp.pr_history', rent_id=rent_id))
        else:
            pr_save_data = serialize_pr_save_data(pr_save_data)
            return redirect(url_for('pr_bp.pr_file', pr_id=pr_id, pr_save_data=pr_save_data, method='email'))


@pr_bp.route('/pr_start', methods=['GET', 'POST'])
@login_required
def pr_start():
    filters = get_filters(1)
    return render_template('pr_start.html', filters=filters)


@pr_bp.route('/pr_undo/<int:pr_id>', methods=['GET', 'POST'])
@login_required
def pr_undo(pr_id):
    if request.method == 'POST':
        message, rent_id = undo_pr(pr_id)
        return redirect(url_for('pr_bp.pr_history', rent_id=rent_id, message=message))
