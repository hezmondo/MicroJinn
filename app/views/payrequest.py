from flask import Blueprint, current_app, redirect, render_template, request, url_for, json, send_from_directory
from flask_login import login_required
from app.email import app_send_email
from app.dao.common import get_filters
from app.dao.form_letter import get_pr_forms
from app.dao.payrequest import get_pr_block, get_pr_file, get_pr_history, post_updated_payrequest
from app.main.payrequest import collect_pr_history_data, collect_pr_rent_data, serialize_pr_save_data, save_new_payrequest, \
    save_new_payrequest_x, undo_pr, write_payrequest, write_payrequest_x, write_payrequest_email
from app.dao.doc import convert_html_to_pdf
import os

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


@pr_bp.route('/pr_edit_xray/<int:pr_form_id>', methods=["GET", "POST"])
@login_required
def pr_edit_xray(pr_form_id):
    if request.method == "POST":
        rent_id = request.args.get('rent_id')
        rent_pr = write_payrequest_x(rent_id, pr_form_id)
        return render_template('mergedocs/PRX.html', rent_pr=rent_pr)


# TODO: remove email method or update pr creation via doReplace
@pr_bp.route('/pr_file/<int:pr_id>', methods=['GET', 'POST'])
@login_required
def pr_file(pr_id):
    method = request.args.get('method', type=str)
    if request.method == "POST":
        try:
            block = request.form.get('xinput').replace("£", "&pound;")
            rent_id = post_updated_payrequest(block, pr_id)
            message = 'Pay request #' + str(pr_id) + ' saved successfully'
            return redirect(url_for('pr_bp.pr_history', rent_id=rent_id, message=message))
        except Exception as ex:
            message = f'Unable to update pay request. Database write failed with error: {str(ex)}'
            return redirect(url_for('pr_bp.pr_file', pr_id=pr_id, message=message))
    message = request.args.get('message', type=str)
    can_undo = request.args.get('can_undo', False, type=bool)
    pr_file = get_pr_file(pr_id)
    if method == 'email':
        pr_save_data = json.loads(request.args.get('pr_save_data'))
        email_block = write_payrequest_email(pr_save_data)
        return render_template('pr_file.html', email_block=email_block, method=method, pr_file=pr_file)
    return render_template('pr_file.html', pr_file=pr_file, can_undo=can_undo, message=message)


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


@pr_bp.route('/pr_print/pay_request_<int:pr_id>', methods=['GET', 'POST'])
def pr_print(pr_id):
    # We generate the pdf from the html in the PrHistory table then display the pdf in a new tab
    convert_html_to_pdf(get_pr_block(pr_id), 'pr.pdf')
    workingdir = os.path.abspath(os.getcwd())
    filepath = workingdir + '\\app\\temp_files\\'
    return send_from_directory(filepath, 'pr.pdf')


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


@pr_bp.route('/pr_save_send_x', methods=['GET', 'POST'])
@login_required
def pr_save_send_x():
    method = request.args.get('method', type=str)
    rent_id = request.args.get('rent_id', type=int)
    if request.method == 'POST':
        pr_history_data = collect_pr_history_data()
        pr_rent_data = collect_pr_rent_data()
        pr_id = save_new_payrequest_x(method, pr_history_data, pr_rent_data, rent_id)
        if method == 'post':
            return redirect(url_for('pr_bp.pr_history', rent_id=rent_id))
        else:
            pr_email = request.form.get('pr_email')
            pr_email_addr = request.form.get('pr_email_addr')
            pr_file = get_pr_file(pr_id)
            return render_template('pr_email_edit.html', email_block=pr_email, pr_email_addr=pr_email_addr,
                                   method=method, pr_file=pr_file)


@pr_bp.route('/pr_send_email', methods=['GET', 'POST'])
@login_required
def pr_send_email():
    if request.method == 'POST':
        appmail = current_app.extensions['mail']
        rent_id = request.form.get('rent_id')
        html_body = request.form.get('html_body')
        subject = request.form.get('subject')
        recipients = request.form.get('recipients')
        # attach a pdf of the pr (aleady saved to the temp_files folder) to the email
        if request.form.get('pr_attached'):
            attachment = Attachment('payrequest for rent ' + rent_id,
                                    'C:\\Users\\User\\PycharmProjects\\mjinn\\app\\temp_files\\pr.pdf',
                                    'application/pdf')
            response = app_send_email(appmail, recipients, subject, html_body, [attachment])
        else:
            response = app_send_email(appmail, recipients, subject, html_body)
        return redirect(url_for('pr_bp.pr_history', rent_id=rent_id, message=response))


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


# The attachment class makes it easy to add attachments to emails. We can move this if its scope will grow beyond
# payrequests
class Attachment:
    def __init__(self, file_name, file_location, file_type):
        self.file_name = file_name
        self.file_type = file_type
        self.file_location = file_location