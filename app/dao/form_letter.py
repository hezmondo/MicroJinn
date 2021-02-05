from app import db
from flask import request
from app.models import Form_letter, Pr_form, Template, Typedoc
from app.dao.functions import commit_to_database


def delete_form_letter(form_letter_id):
    Form_letter.query.filter_by(id=form_letter_id).delete()
    commit_to_database()


def get_form_letter(form_letter_id):
    form_letter = Form_letter.query.join(Typedoc).join(Template).with_entities(Form_letter.id, Form_letter.code,
                                                                              Form_letter.description,
                                                                              Form_letter.subject, Form_letter.block,
                                                                              Typedoc.desc,
                                                                              Template.desc.label("template")) \
        .filter(Form_letter.id == form_letter_id).one_or_none()
    return form_letter


def get_form_letters(action):
    if request.method == "POST":
        code = request.form.get("code") or ""
        description = request.form.get("description") or ""
        subject = request.form.get("subject") or ""
        block = request.form.get("block") or ""
        form_letters = Form_letter.query.filter(Form_letter.code.ilike('%{}%'.format(code)),
                                               Form_letter.description.ilike('%{}%'.format(description)),
                                               Form_letter.subject.ilike('%{}%'.format(subject)),
                                               Form_letter.block.ilike('%{}%'.format(block))).all()
    elif action == "lease":
        form_letters = Form_letter.query.filter(Form_letter.code.ilike('LEQ-%'))
    else:
        form_letters = Form_letter.query.all()
    return form_letters


def get_templates():
    templates = [value for (value,) in Template.query.with_entities(Template.code).all()]
    return templates


def post_form_letter(form_letter_id):
    if form_letter_id == 0:
        form_letter = Form_letter()
    else:
        form_letter = Form_letter.query.get(form_letter_id)
    form_letter.code = request.form.get("code")
    form_letter.description = request.form.get("description")
    form_letter.subject = request.form.get("subject")
    form_letter.block = request.form.get("block")
    form_letter.bold = request.form.get("bold")
    doctype = request.form.get("doc_type")
    form_letter.doctype_id = \
        Typedoc.query.with_entities(Typedoc.id).filter \
            (Typedoc.desc == doctype).one()[0]
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
    formpayrequest = Pr_form.query.filter(Pr_form.id == form_letter_id).one_or_none()
    return formpayrequest


def get_formpayrequests():
    return Pr_form.query.all()
