from flask import Blueprint, render_template, redirect, request, url_for
from flask_login import login_required
from app.dao.common import get_doc_types
from app.main.form_letter import mget_form_letter, mget_form_letters_from_search, mpost_form_letter, mpost_form_letter_new
from app.dao.form_letter import get_form_letters_all

form_letter_bp = Blueprint('form_letter_bp', __name__)


@form_letter_bp.route('/form_letter/<int:form_letter_id>', methods=['GET', 'POST'])
@login_required
def form_letter(form_letter_id):
    if request.method == "POST":
        try:
            form_letter_id = mpost_form_letter_new() if form_letter_id == 0 else mpost_form_letter(form_letter_id)
            return redirect(url_for('form_letter_bp.form_letter', form_letter_id=form_letter_id))
        except Exception as ex:
            message = f'Unable to save the letter. Error: {str(ex)}'
            return redirect(url_for('form_letter_bp.form_letters', message=message))
    doc_types = [typedoc.desc for typedoc in get_doc_types()]
    form_letter = mget_form_letter(form_letter_id) if form_letter_id != 0 else ''
    variables = list_variables()
    return render_template('form_letter.html', doc_types=doc_types, form_letter=form_letter, variables=variables)


@form_letter_bp.route('/form_letters', methods=['GET', 'POST'])
def form_letters():
    message = request.args.get('message')
    fdict = {}
    if request.method == 'POST':
        form_letters, fdict = mget_form_letters_from_search()
    else:
        form_letters = get_form_letters_all()
    return render_template('form_letters.html', form_letters=form_letters, fdict=fdict, message=message)


# TODO: These variables are hardcoded, rather than obtained from the get_variables code. With this method they'll
#  need to be updated here when variables are changed
def list_variables():
    lease_variables = ['#unexpired#', '#rent_code#', '#relativity#', '#tot_val#', '#unimpvalue#',
                       '#impvalue#', '#leq200R#', '#leq200P#', '#gr_new#']
    mail_variables = ['#acc_name#', '#acc_num#', '#advarr#', '#arrears#', '#arrears_start_date#',
                      '#arrears_end_date#', '#bank_name#', '#charges_stat#', '#hashcode#', '#landlord_name#',
                      '#lastrentdate#', '#manageraddr#', '#manageraddr2#', '#managername#',
                      '#nextrentdate#', '#rent_owing#', '#paidtodate#', '#payamount#', '#paydate#', '#payer#',
                      '#paytypedet#', '#periodly#', '#propaddr#', '#rentcode#', '#rentgale#', '#rent_owing#',
                      '#rentpa#', '#rent_type#', '#sort_code#', '#tenantname#', '#today#',
                      '#totcharges#', '#totdue#']
    return {'lease_variables': lease_variables,
            'mail_variables': mail_variables}


