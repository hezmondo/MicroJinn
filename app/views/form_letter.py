from flask import Blueprint, render_template, redirect, request
from flask_login import login_required
from app.dao.form_letter import get_formletter, get_formletters, get_templates, post_formletter

fo_bp = Blueprint('fo_bp', __name__)

@fo_bp.route('/form_letter/<int:id>', methods=['GET', 'POST'])
@login_required
def form_letter(id):
    action = request.args.get('action', "view", type=str)
    if request.method == "POST":
        id_ = post_formletter(id, action)
        return redirect('/form_letter/{}?action=view'.format(id_))
    formletter = get_formletter(id)
    templates = get_templates()

    return render_template('form_letter.html', action=action, formletter=formletter, templates=templates)

@fo_bp.route('/form_letters', methods=['GET'])
def form_letters():
    formletters = get_formletters("normal")

    return render_template('form_letters.html', formletters=formletters)
