from flask import Blueprint, current_app, redirect, render_template, request, url_for, json, send_from_directory
from flask_login import login_required
from app import db
from app.emails import app_send_email
from app.dao.common import get_filters
from app.dao.rent import get_rentcode
from app.dao.form_letter import get_form_id, get_pr_forms
from app.dao.payrequest import get_batch_pay_requests, get_batch_pr_post_html, get_pr_batch, get_pr_batches, get_pr_block, \
    get_pr_file, get_pr_history, get_pr_history_row, post_updated_payrequest, post_updated_payrequest_delivery
from app.main.payrequest import collect_pr_history_data, collect_pr_rent_data, undo_pr_batch, run_batch, \
    save_new_payrequest_from_batch, \
    save_new_payrequest, undo_pr, write_payrequest, write_payrequest_x
from app.main.doc import convert_html_to_pdf
import os

pr_bp = Blueprint('pr_bp', __name__)


@pr_bp.route('/pr_batch/<int:batch_id>', methods=['GET', 'POST'])
def pr_batch(batch_id):
    pr_batch = get_pr_batch(batch_id)
    pay_requests = get_batch_pay_requests(batch_id)

    return render_template('pr_batch.html', pr_batch=pr_batch, pay_requests=pay_requests)


@pr_bp.route('/pr_batch_email/<int:batch_id>', methods=['GET', 'POST'])
def pr_batch_email(batch_id):
    pr_batch = get_pr_batch(batch_id)
    pay_requests = get_batch_pay_requests(batch_id)

    return render_template('pr_batch.html', pr_batch=pr_batch, pay_requests=pay_requests)


@pr_bp.route('/pr_batch_post/<int:batch_id>', methods=['GET', 'POST'])
def pr_batch_post(batch_id):
    pay_requests = get_batch_pr_post_html(batch_id)
    html_complete = ''
    for pay_request in pay_requests:
        html_complete = html_complete + pay_request.block + "<p style='page-break-before: always'></p>"
    convert_html_to_pdf(html_complete, 'pr.pdf')
    workingdir = os.path.abspath(os.getcwd())
    filepath = workingdir + '\\app\\temp_files\\'
    return send_from_directory(filepath, 'pr.pdf')


@pr_bp.route('/pr_batches', methods=['GET', 'POST'])
def pr_batches():
    message = request.args.get('message')
    pr_batches = get_pr_batches()
    return render_template('pr_batches.html', pr_batches=pr_batches, message=message)


@pr_bp.route('/pr_delivery/<int:pr_id>', methods=["GET", "POST"])
@login_required
def pr_delivery(pr_id):
    rent_id = request.args.get('rent_id')
    delivered = request.args.get('delivered')
    delivered = True if delivered == 'True' else False
    try:
        post_updated_payrequest_delivery(delivered, get_pr_history_row(pr_id))
        string = " set to 'delivered'" if delivered else " set to 'undelivered'"
        message = 'Pay request ' + str(pr_id) + string
    except Exception as ex:
        message = f"Unable to update pay request delivery. Database rolled back. Error: {str(ex)}"
        db.session.rollback()
    return redirect(url_for('pr_bp.pr_history', rent_id=rent_id, message=message))


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
        try:
            block, block_email, rent_pr, subject = write_payrequest(rent_id, pr_form_id)
            return render_template('mergedocs/PR.html', block=block, block_email=block_email, rent_pr=rent_pr,
                                   subject=subject)
        except Exception as ex:
            message = f'Unable to write the pay request. Error: {str(ex)}'
            return redirect(url_for('pr_bp.pr_history', rent_id=rent_id, message=message))


@pr_bp.route('/pr_edit_xray/<int:pr_form_id>', methods=["GET", "POST"])
@login_required
def pr_edit_xray(pr_form_id):
    if request.method == "POST":
        rent_id = request.args.get('rent_id')
        try:
            rent_pr = write_payrequest_x(rent_id, pr_form_id)
            return render_template('mergedocs/PRX.html', rent_pr=rent_pr)
        except Exception as ex:
            message = f'Unable to write the pay request. Error: {str(ex)}'
            return redirect(url_for('pr_bp.pr_history', rent_id=rent_id, message=message))


@pr_bp.route('/pr_file/<int:pr_id>', methods=['GET', 'POST'])
@login_required
def pr_file(pr_id):
    if request.method == "POST":
        try:
            block = request.form.get('xinput').replace("£", "&pound;")
            rent_id = post_updated_payrequest(block, pr_id)
            message = 'Pay request #' + str(pr_id) + ' saved successfully'
            return redirect(url_for('pr_bp.pr_history', rent_id=rent_id, message=message))
        except Exception as ex:
            message = f'Unable to update pay request. Database rolled back. Error: {str(ex)}'
            db.session.rollback()
            return redirect(url_for('pr_bp.pr_file', pr_id=pr_id, message=message))
    message = request.args.get('message', type=str)
    can_undo = request.args.get('can_undo', False, type=bool)
    pr_file = get_pr_file(pr_id)
    return render_template('pr_file.html', pr_file=pr_file, can_undo=can_undo, message=message)


@pr_bp.route('/pr_history/<int:rent_id>', methods=['GET', 'POST'])
@login_required
def pr_history(rent_id):
    message = request.args.get('message', type=str)
    pr_history = get_pr_history(rent_id)
    return render_template('pr_history.html', rent_id=rent_id, pr_history=pr_history, message=message)


@pr_bp.route('/pr_print/pay_request_<int:pr_id>', methods=['GET', 'POST'])
def pr_print(pr_id):
    # We generate the pdf from the html in the PrHistory table then display the pdf in a new tab
    try:
        # TODO: Do we want the pr to be set to 'delivered' after the user selects 'print'?
        # If the delivery method is post, we set the pr to 'delivered'
        # update_pr_delivered(pr_id)
        convert_html_to_pdf(get_pr_block(pr_id), 'pr.pdf')
        workingdir = os.path.abspath(os.getcwd())
        filepath = workingdir + '\\app\\temp_files\\'
        return send_from_directory(filepath, 'pr.pdf')
    except Exception as ex:
        message = f'Unable to produce pay request. Error: {str(ex)}'
        return redirect(url_for('pr_bp.file', pr_id=pr_id, message=message))


# Test - Produces pay requests for rents 1 - 100. Pdf saved in jinn\app\temp_files
@pr_bp.route('/pr_test<int:rent_id>', methods=['GET', 'POST'])
def pr_test(rent_id):
    html_tot = ''
    for rent_ids in range(1, 100):
        block, block_email, rent_pr, subject = write_payrequest(rent_ids, 15)
        if rent_pr.mailaddr:
            html = render_template('mergedocs/PR_template.html', block=block, rent_pr=rent_pr, subject=subject)
            html_tot = html_tot + html + "<p style='page-break-before: always'></p>"
            save_new_payrequest_from_batch(html, rent_pr)
    convert_html_to_pdf(html_tot, 'pr.pdf')
    return redirect(url_for('util_bp.actions'))


# Test - Produces pay requests for rents 1 - 100 using PRX. Pdf saved in jinn\app\temp_files
@pr_bp.route('/prx_test<int:rent_id>', methods=['GET', 'POST'])
def prx_test(rent_id):
    html_tot = ''
    for rent_ids in range(1, 100):
        rent_pr = write_payrequest_x(rent_ids, 19)
        if rent_pr.mailaddr:
            html = render_template('mergedocs/PRX_template.html', rent_pr=rent_pr)
            html_tot = html_tot + html + "<p style='page-break-before: always'></p>"
            save_new_payrequest_from_batch(html, rent_pr)
    convert_html_to_pdf(html_tot, 'pr.pdf')
    return redirect(url_for('util_bp.actions'))


@pr_bp.route('/pr_run_batch', methods=['GET', 'POST'])
def pr_run_batch():
    if request.method == 'POST':
        try:
            rent_id_list = json.loads(request.form.get('rent_id_list'))
            runcode = request.form.get('runcode') or 'Unknown Filter'
            pr_template_id = get_form_id(request.form.get('pr_template'))
            pr_batch, pr_complete, pr_error = run_batch(pr_template_id, rent_id_list, runcode)
            pay_requests = get_batch_pay_requests(pr_batch.id)
        except Exception as ex:
            message = f'Unable to produce batch. Error: {str(ex)}'
            return redirect(url_for('pr_bp.pr_batches', message=message))
        return render_template('pr_batch.html', pr_batch=pr_batch, pay_requests=pay_requests, pr_complete=pr_complete,
                               pr_error=pr_error)


@pr_bp.route('/pr_save_send', methods=['GET', 'POST'])
@login_required
def pr_save_send():
    method = request.args.get('method', type=int)
    rent_id = request.args.get('rent_id', type=int)
    if request.method == 'POST':
        pr_history_data = collect_pr_history_data()
        pr_rent_data = collect_pr_rent_data()
        try:
            pr_id = save_new_payrequest(method, pr_history_data, pr_rent_data, rent_id)
        except Exception as ex:
            message = f'Cannot save pay request. Database rolled back. Error:  {str(ex)}'
            db.session.rollback()
            return redirect(url_for('pr_bp.pr_history', rent_id=rent_id, message=message))
        if method == 2:  # delivery: post
            return redirect(url_for('pr_bp.pr_history', rent_id=rent_id))
        else:
            pr_email = request.form.get('pr_email')
            pr_email_addr = request.form.get('pr_email_addr')
            pr_file = get_pr_file(pr_id)
            return render_template('pr_email_edit.html', email_block=pr_email, pr_email_addr=pr_email_addr,
                                   method=method, pr_file=pr_file)


@pr_bp.route('/pr_send_email/<int:pr_id>', methods=['GET', 'POST'])
@login_required
def pr_send_email(pr_id):
    if request.method == 'POST':
        appmail = current_app.extensions['mail']
        rent_id = request.form.get('rent_id')
        html_body = request.form.get('html_body')
        subject = request.form.get('subject')
        recipients = request.form.get('recipients')
        try:
            # attach a pdf of the pr (already saved to the temp_files folder) to the email
            if request.form.get('pr_attached'):
                attachment = Attachment('payrequest for rent ' + get_rentcode(rent_id),
                                        'C:\\Users\\User\\PycharmProjects\\mjinn\\app\\temp_files\\pr.pdf',
                                        'application/pdf')
                response = app_send_email(appmail, recipients, subject, html_body, [attachment])
            else:
                response = app_send_email(appmail, recipients, subject, html_body)
            # Update delivery status of the pay request
            post_updated_payrequest_delivery(True, get_pr_history_row(pr_id))
        except Exception as ex:
            response = f"Email sending failed with error: {str(ex)}"
        return redirect(url_for('pr_bp.pr_history', rent_id=rent_id, message=response))


@pr_bp.route('/pr_start', methods=['GET', 'POST'])
@login_required
def pr_start():
    message = request.args.get('message')
    filters = get_filters(1)
    return render_template('pr_start.html', filters=filters, message=message)


@pr_bp.route('/pr_undo/<int:pr_id>', methods=['GET', 'POST'])
@login_required
def pr_undo(pr_id):
    if request.method == 'POST':
        message, rent_id = undo_pr(pr_id)
        return redirect(url_for('pr_bp.pr_history', rent_id=rent_id, message=message))


@pr_bp.route('/pr_undo_batch/<int:batch_id>', methods=['GET', 'POST'])
@login_required
def pr_undo_batch(batch_id):
    try:
        undo_pr_batch(batch_id)
        message = 'Batch ' + str(batch_id) + ' successfully undone.'
    except Exception as ex:
        message = f"Undo batch failed with error: {str(ex)}"
    return redirect(url_for('pr_bp.pr_batches', message=message))


# The attachment class makes it easy to add attachments to emails. We can move this if its scope will grow beyond
# payrequests
class Attachment:
    def __init__(self, file_name, file_location, file_type):
        self.file_name = file_name
        self.file_type = file_type
        self.file_location = file_location
