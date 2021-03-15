from app import db
from flask import request
from app.models import FormLetter, TypeDoc
from app.dao.common import get_doctype
from app.dao.database import commit_to_database


def get_form_letter(form_letter_id):  #returns all Rent member variables as a mutable dict
    form_letter = FormLetter.query.filter_by(id=form_letter_id).first()
    form_letter.doctype = get_doctype(form_letter.doctype_id)
    return form_letter


def get_form_letters(action='all'):
    if request.method == "POST":
        code = request.form.get("code") or ""
        description = request.form.get("description") or ""
        subject = request.form.get("subject") or ""
        block = request.form.get("block") or ""
        form_letters = FormLetter.query.filter(FormLetter.code.ilike('%{}%'.format(code)),
                                               FormLetter.description.ilike('%{}%'.format(description)),
                                               FormLetter.subject.ilike('%{}%'.format(subject)),
                                               FormLetter.block.ilike('%{}%'.format(block))).all()
    elif action == "lease":
        form_letters = FormLetter.query.filter(FormLetter.code.ilike('LEQ-%'))
    elif action == "all":
        form_letters = FormLetter.query.all()
    else:
        form_letters = FormLetter.query.filter(FormLetter.code.notilike('PR-%'),
                           FormLetter.code.notilike('AC-%'), FormLetter.code.notilike('LEQ-%')).all()

    return form_letters


def get_email_form_by_code(code):
    email_form = FormLetter.query.filter(FormLetter.code == code).one_or_none()
    return email_form


def get_pr_form(pr_form_id):
    pr_form = FormLetter.query.filter(FormLetter.id == pr_form_id).one_or_none()

    return pr_form


def get_pr_forms():

    return FormLetter.query.filter(FormLetter.doctype_id == 2).all()


def get_templates():
    templates = [value for (value,) in Template.query.with_entities(Template.code).all()]

    return templates


def post_form_letter(form_letter_id):
    if form_letter_id == 0:
        form_letter = FormLetter()
    else:
        form_letter = FormLetter.query.get(form_letter_id)
    form_letter.code = request.form.get("code")
    form_letter.description = request.form.get("description")
    form_letter.subject = request.form.get("subject")
    form_letter.block = request.form.get("block")
    form_letter.bold = request.form.get("bold")
    doctype = request.form.get("doc_type")
    form_letter.doctype_id = \
        TypeDoc.query.with_entities(TypeDoc.id).filter \
            (TypeDoc.desc == doctype).one()[0]
    template = request.form.get("template")
    form_letter.template_id = \
        Template.query.with_entities(Template.id).filter \
            (Template.code == template).one()[0]
    db.session.add(form_letter)
    db.session.flush()
    form_letter_id = form_letter.id
    commit_to_database()

    return form_letter_id

