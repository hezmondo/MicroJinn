from flask import Blueprint, render_template,  request
from flask_login import login_required
from app.dao.form_letter import get_form_letters
from app.main.mail import get_mail_pack, writeMail

mail_bp = Blueprint('mail_bp', __name__)


@mail_bp.route('/mail_dialog/<int:rent_id>', methods=["GET", "POST"])
@login_required
def mail_dialog(rent_id):
    action = request.args.get('action', "all", type=str)
    form_letters = get_form_letters(action)
    mail_pack = get_mail_pack(rent_id)
    return render_template('mail_dialog.html', action=action, form_letters=form_letters, mail_pack=mail_pack)


@mail_bp.route('/mail_edit/<int:form_letter_id>', methods=["GET", "POST"])
@login_required
def mail_edit(form_letter_id):
    template = request.args.get('template', "LTS", type=str)
    method = request.args.get('method', "email", type=str)
    if request.method == "POST":
        form_letter_id = form_letter_id
        income_id = request.form.get('income_id') or 0
        rent_id = request.form.get('rent_id')
        block, doctype_id, leasedata, rent, subject, variables = writeMail(rent_id, template, form_letter_id, income_id)
        mailaddr = request.form.get('mailaddr')
        sent_to = rent.email if method == "email" else mailaddr[0:25]
        summary = f"{method}-{template}-to-{sent_to}"[0:25]
        mailaddr = mailaddr.split(", ")
        return render_template(f"mergedocs/{template}.html", block=block, doctype_id=doctype_id, summary=summary,
                               leasedata=leasedata, mailaddr=mailaddr, method=method, rent=rent, subject=subject,
                               variables=variables)


