from flask import Blueprint, redirect, render_template,  request
from flask_login import login_required
from app.dao.filter import get_filters
from app.dao.form_letter import get_formpayrequests
from app.dao.mail import write_payrequest

pr_bp = Blueprint('pr_bp', __name__)

@pr_bp.route('/pr_dialog/<int:id>', methods=["GET", "POST"])
@login_required
def pr_dialog(id):
    formpayrequests = get_formpayrequests()

    return render_template('pr_dialog.html', formpayrequests=formpayrequests, rent_id=id)


@pr_bp.route('/pr_edit/<int:id>', methods=["GET", "POST"])
@login_required
def pr_edit(id):
    method = request.args.get('method', "email", type=str)
    if request.method == "POST":
        # formpayrequest_id is the id of the pr template
        formpayrequest_id = id
        rent_id = request.form.get('rent_id')
        # TODO: passing both totdue and totdue_string with money formatting. Is there a better way?
        addressdata, block, rentobject, subject, \
            table_rows, totdue, totdue_string = write_payrequest(rent_id, formpayrequest_id)
        mailaddr = request.form.get('mailaddr')
        # TODO: Do we want a specific PR code to begin the summary?
        summary = "PR" + "-" + method + "-" + mailaddr[0:25]
        mailaddr = mailaddr.split(", ")

        return render_template('mergedocs/PR.html', addressdata=addressdata, block=block, mailaddr=mailaddr,
                               method=method, rentobject=rentobject, subject=subject, summary=summary, table_rows=table_rows,
                               totdue=totdue, totdue_string=totdue_string)


@pr_bp.route('/pr_start', methods=['GET', 'POST'])
@login_required
def pr_start():
    filters = get_filters(1)

    return render_template('pr_start.html', filters=filters)
