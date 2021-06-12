from app import db
from flask import request
from sqlalchemy.orm import load_only
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


def get_pr_form_code(pr_form_id):
    return db.session.query(FormLetter).filter_by(id=pr_form_id).options(load_only('code')).one_or_none()


def get_pr_form_essential(pr_form_id):
    return db.session.query(FormLetter).filter_by(id=pr_form_id).options(load_only('code', 'block', 'subject'))\
        .one_or_none()


def get_pr_email_form():
    return db.session.query(FormLetter).filter_by(code='EPR').options(load_only('block')).one_or_none()


def get_pr_forms():
    return FormLetter.query.filter(FormLetter.doctype_id == 2).all()


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
    form_letter.template = request.form.get("template")
    db.session.add(form_letter)
    db.session.flush()
    form_letter_id = form_letter.id
    commit_to_database()

    return form_letter_id

