from flask import Blueprint, render_template, redirect, request
from flask_login import login_required
from app.dao.form_letter import get_formletter, get_formletters, get_templates, post_formletter

formletter_bp = Blueprint('formletter_bp', __name__)

@formletter_bp.route('/form_letter/<int:form_id>', methods=['GET', 'POST'])
@login_required
def form_letter(form_id):
    action = request.args.get('action', "view", type=str)
    if request.method == "POST":
        id_ = post_formletter(form_id, action)
        return redirect('/form_letter/{}?action=view'.format(id_))
    formletter = get_formletter(form_id)
    templates = get_templates()

    return render_template('form_letter.html', action=action, formletter=formletter, templates=templates)

@formletter_bp.route('/form_letters', methods=['GET'])
def form_letters():
    formletters = get_formletters("normal")

    return render_template('form_letters.html', formletters=formletters)
