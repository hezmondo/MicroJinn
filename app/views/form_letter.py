from flask import Blueprint, render_template, redirect, request, url_for
from flask_login import login_required
from app.dao.form_letter import get_form_letter, get_form_letters, get_templates, post_form_letter

form_letter_bp = Blueprint('form_letter_bp', __name__)


@form_letter_bp.route('/form_letter/<int:form_letter_id>', methods=['GET', 'POST'])
@login_required
def form_letter(form_letter_id):
    if request.method == "POST":
        form_letter_id = post_form_letter(form_letter_id)
        return redirect(url_for('form_letter_bp.form_letter', form_letter_id=form_letter_id))
    form_letter = get_form_letter(form_letter_id)
    templates = get_templates()
    variables = list_variables()
    return render_template('form_letter.html', form_letter=form_letter, templates=templates, variables=variables)


@form_letter_bp.route('/form_letters', methods=['GET'])
def form_letters():
    form_letters = get_form_letters("all")
    return render_template('form_letters.html', form_letters=form_letters)


# TODO: These variables are hardcoded, rather than obtained from the get_variables code. With this method they'll
#  need to be updated here when variables are changed
def list_variables():
    lease_variables = ['#unexpired#', '#rent_code#', '#relativity#', '#tot_val#', '#unimpvalue#',
                       '#impvalue#', '#leq200R#', '#leq200P#', '#gr_new#']
    mail_variables = ['#acc_name#', '#acc_num#', '#advarr#', '#arrears#', '#arrears_start_date#',
                      '#arrears_end_date#', '#bank_name#', '#hashcode#', '#landlord_name#',
                      '#lastrentdate#', '#manageraddr#', '#manageraddr2#', '#managername#',
                      '#nextrentdate#', '#periodly#', '#propaddr#', '#rentcode#', '#rentgale#',
                      '#rentpa#', '#rent_type#', '#sort_code#', '#tenantname#', '#today#',
                      '#totcharges#', '#totdue#']
    return {'lease_variables': lease_variables,
            'mail_variables': mail_variables}


