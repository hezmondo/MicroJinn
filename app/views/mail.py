from flask import redirect, render_template,  request
from flask_login import login_required
from app.views import bp
from app.dao.form_letter import get_formletters
from app.dao.mail import writeMail


@bp.route('/mail_dialog/<int:id>', methods=["GET", "POST"])
@login_required
def mail_dialog(id):
    action = request.args.get('action', "normal", type=str)
    formletters = get_formletters(action)

    return render_template('mail_dialog.html', action=action, formletters=formletters, rent_id=id)


@bp.route('/mail_edit/<int:id>', methods=["GET", "POST"])
@login_required
def mail_edit(id):
    method = request.args.get('method', "email", type=str)
    action = request.args.get('action', "normal", type=str)
    if request.method == "POST":
            # print(request.form)
        formletter_id = id
        rent_id = request.form.get('rent_id')
        addressdata, block, leasedata, rentobject, subject, doctype, dcode = writeMail(rent_id, 0, formletter_id,
                                                                                    action)
        mailaddr = request.form.get('mailaddr')
        summary = dcode + "-" + method + "-" + mailaddr[0:25]
        mailaddr = mailaddr.split(", ")

        return render_template('mergedocs/LTS.html', addressdata=addressdata, block=block, doctype=doctype,
                               summary=summary, leasedata=leasedata, mailaddr=mailaddr,
                               method=method, rentobject=rentobject, subject=subject)
