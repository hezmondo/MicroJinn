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
    return render_template('form_letter.html', form_letter=form_letter, templates=templates)


@form_letter_bp.route('/form_letters', methods=['GET'])
def form_letters():
    form_letters = get_form_letters("normal")
    return render_template('form_letters.html', form_letters=form_letters)
