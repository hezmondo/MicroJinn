from app import db
from flask import request
from app.models import FormLetter, PrForm, Template, TypeDoc
from app.dao.functions import commit_to_database


def get_form_letter(form_letter_id):
    form_letter = FormLetter.query.join(TypeDoc).join(Template).with_entities(FormLetter.id, FormLetter.code,
                                                                              FormLetter.description,
                                                                              FormLetter.subject, FormLetter.block,
                                                                              TypeDoc.desc,
                                                                              Template.desc.label("template")) \
        .filter(FormLetter.id == form_letter_id).one_or_none()
    return form_letter


def get_form_letters(action):
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
    else:
        form_letters = FormLetter.query.all()
    return form_letters


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


def get_formpayrequest(form_letter_id):
    formpayrequest = PrForm.query.filter(PrForm.id == form_letter_id).one_or_none()
    return formpayrequest


def get_formpayrequests():
    return PrForm.query.all()
