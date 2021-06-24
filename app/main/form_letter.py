from flask import request
from app.dao.form_letter import get_form_letter, get_form_letters_from_search, get_form_letters_all, \
    get_form_letters_lease, get_form_letters_other, post_form_letter
from app.dao.common import get_doctype
from app.dao.doc import get_typedoc_id
from app.models import FormLetter


def mbuild_form_letter_from_form(form_letter):
    form_letter.code = request.form.get("code")
    form_letter.description = request.form.get("description")
    form_letter.subject = request.form.get("subject")
    form_letter.block = request.form.get("block")
    form_letter.bold = request.form.get("bold")
    form_letter.doctype_id = get_typedoc_id(request.form.get("doc_type"))
    form_letter.template = request.form.get("template")
    return form_letter


def mget_form_letter(form_letter_id):  # returns all Rent member variables as a mutable dict
    form_letter = get_form_letter(form_letter_id)
    form_letter.doctype = get_doctype(form_letter.doctype_id)
    return form_letter


def mget_form_letters(action='all'):
    if action == 'all':
        return get_form_letters_all()
    elif action == 'lease':
        return get_form_letters_lease()
    else:
        return get_form_letters_other()


def mget_form_letters_dict():
    return {'code': request.form.get("code") or "",
            'description': request.form.get("description") or "",
            'subject': request.form.get("subject") or "",
            'block': request.form.get("block") or ""}


def mget_form_letters_from_search():
    fdict = mget_form_letters_dict()
    form_letters = get_form_letters_from_search(fdict)
    return form_letters, fdict


def mpost_form_letter(form_letter_id):
    form_letter = mbuild_form_letter_from_form(get_form_letter(form_letter_id))
    return post_form_letter(form_letter)


def mpost_form_letter_new():
    form_letter = mbuild_form_letter_from_form(FormLetter())
    return post_form_letter(form_letter)

