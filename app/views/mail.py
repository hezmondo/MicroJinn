from flask import Blueprint, render_template,  request
from flask_login import login_required
from app.dao.rent_ import get_rent_mail
from app.dao.form_letter import get_formletters
from app.dao.mail import writeMail

mail_bp = Blueprint('mail_bp', __name__)


@mail_bp.route('/mail_dialog/<int:rent_id>', methods=["GET", "POST"])
@login_required
def mail_dialog(rent_id):
    action = request.args.get('action', "normal", type=str)
    formletters = get_formletters(action)
    rent_mail = get_rent_mail(rent_id)

    return render_template('mail_dialog.html', action=action, formletters=formletters, rent_mail=rent_mail)


@mail_bp.route('/mail_edit/<int:form_id>', methods=["GET", "POST"])
@login_required
def mail_edit(form_id):
    method = request.args.get('method', "email", type=str)
    action = request.args.get('action', "normal", type=str)
    if request.method == "POST":
            # print(request.form)
        formletter_id = form_id
        rent_id = request.form.get('rent_id')
        addressdata, block, leasedata, rent_, subject, doctype, dcode = writeMail(rent_id, 0, formletter_id,
                                                                                    action)
        mailaddr = request.form.get('mailaddr')
        summary = dcode + "-" + method + "-" + mailaddr[0:25]
        mailaddr = mailaddr.split(", ")

        return render_template('mergedocs/LTS.html', addressdata=addressdata, block=block, doctype=doctype,
                               summary=summary, leasedata=leasedata, mailaddr=mailaddr,
                               method=method, rent_=rent_, subject=subject)
