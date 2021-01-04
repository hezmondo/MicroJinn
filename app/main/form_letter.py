from app import db
from flask import request
from sqlalchemy import desc, func
from app.main.functions import commit_to_database
from app.models import Form_letter, Pr_form, Template, Typedoc\


def get_formletter(id):
    formletter = Form_letter.query.join(Typedoc).join(Template).with_entities(Form_letter.id, Form_letter.code,
                                                                              Form_letter.description,
                                                                              Form_letter.subject, Form_letter.block,
                                                                              Typedoc.desc,
                                                                              Template.desc.label("template")) \
        .filter(Form_letter.id == id).one_or_none()

    return formletter


def get_formletters(action):
    if request.method == "POST":
        code = request.form.get("code") or ""
        description = request.form.get("description") or ""
        subject = request.form.get("subject") or ""
        block = request.form.get("block") or ""
        formletters = Form_letter.query.filter(Form_letter.code.ilike('%{}%'.format(code)),
                                               Form_letter.description.ilike('%{}%'.format(description)),
                                               Form_letter.subject.ilike('%{}%'.format(subject)),
                                               Form_letter.block.ilike('%{}%'.format(block))).all()
    elif action == "lease":
        formletters = Form_letter.query.filter(Form_letter.code.ilike('LEQ-%'))
    else:
        formletters = Form_letter.query.all()

    return formletters


def post_formletter(id, action):
    if action == "edit":
        formletter = Form_letter.query.get(id)
    else:
        formletter = Form_letter()
    formletter.code = request.form.get("code")
    formletter.description = request.form.get("description")
    formletter.subject = request.form.get("subject")
    formletter.block = request.form.get("block")
    formletter.bold = request.form.get("bold")
    doctype = request.form.get("doc_type")
    formletter.doctype_id = \
        Typedoc.query.with_entities(Typedoc.id).filter \
            (Typedoc.desc == doctype).one()[0]
    template = request.form.get("template")
    formletter.template_id = \
        Template.query.with_entities(Template.id).filter \
            (Template.code == template).one()[0]
    db.session.add(formletter)
    db.session.commit()
    id_ = formletter.id

    return id_


def get_formpayrequest(id):
    formpayrequest = Pr_form.query.filter(Pr_form.id == id).one_or_none()
    return formpayrequest


def get_formpayrequests():
    return Pr_form.query.all()
