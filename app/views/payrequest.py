from app.dao.filter import get_filters
from app.dao.form_letter import get_pr_forms
from app.dao.payrequest import get_pr_file, get_pr_history, post_new_payrequest, post_updated_payrequest
from app.dao.rent import get_rent_addrs
from app.main.payrequest import serialize_pr_save_data, write_payrequest, write_payrequest_email
from flask import Blueprint, redirect, render_template,  request, url_for, json
from flask_login import login_required
from app.forms import PrPostForm

pr_bp = Blueprint('pr_bp', __name__)


@pr_bp.route('/pr_dialog/<int:rent_id>', methods=["GET", "POST"])
@login_required
def pr_dialog(rent_id):
    pr_forms = get_pr_forms()
    rent_addrs = get_rent_addrs(rent_id)

    return render_template('pr_dialog.html', pr_forms=pr_forms, rent_id=rent_id, rent_addrs=rent_addrs)


@pr_bp.route('/pr_edit/<int:pr_form_id>', methods=["GET", "POST"])
@login_required
def pr_edit(pr_form_id):
    if request.method == "POST":
        rent_id = request.args.get('rent_id')
        # TODO: Avoid passing both totdue and totdue_string - include money formatting in html template?
        block, pr_save_data, rent_mail, subject, table_rows, \
            totdue_string = write_payrequest(rent_id, pr_form_id)
        pr_form = PrPostForm()
        rent_addrs = get_rent_addrs(rent_id)
        mailaddr = rent_addrs.mailaddr.split(", ")
        pr_form.mailaddr.choices = [rent_addrs.mailaddr, (rent_addrs.tenantname + ', ' + rent_addrs.propaddr),
                                    ('The owner/occupier, ' + rent_addrs.propaddr)]
        if pr_form.validate_on_submit():
            return redirect(url_for('pr_save_send', rent_id=rent_mail.id))
        pr_save_data = serialize_pr_save_data(pr_save_data)

        return render_template('mergedocs/PR.html', mailaddr=mailaddr, pr_save_data=pr_save_data, pr_form=pr_form,
                               block=block, rent_mail=rent_mail, subject=subject,
                               table_rows=table_rows, totdue_string=totdue_string)


# TODO: improve pr_file editing functionality (beyond edit summary/block)
@pr_bp.route('/pr_file/<int:pr_id>', methods=['GET', 'POST'])
@login_required
def pr_file(pr_id):
    method = request.args.get('method', type=str)
    if request.method == "POST":
        rent_id = post_updated_payrequest(pr_id)
        return redirect(url_for('pr_bp.pr_history', rent_id=rent_id))
    pr_file = get_pr_file(pr_id)
    if method == 'email':
        pr_save_data = json.loads(request.args.get('pr_save_data'))
        email_block = write_payrequest_email(pr_save_data)
        return render_template('pr_file.html', email_block=email_block, method=method, pr_file=pr_file)

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


@pr_bp.route('/pr_save_send', methods=['GET', 'POST'])
def pr_save_send():
    method = request.args.get('method', type=str)
    if request.method == 'POST':
        pr_id, pr_save_data, rent_id = post_new_payrequest(method)
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
