from flask import request
from app.dao.form_letter import get_form_letter, get_form_letters_from_search, get_form_letters_all, \
    get_form_letters_lease, get_form_letters_other, post_form_letter
from app.dao.common import get_doctype, get_user_settings, post_user_settings
from app.dao.doc import get_typedoc_id
from app.models import FormLetter


def mbuild_form_letter_from_form(form_letter):
    form_letter.code = request.form.get("code")
    form_letter.description = request.form.get("description")
    form_letter.subject = request.form.get("subject")
    form_letter.block = request.form.get("block")
    form_letter.doctype_id = get_typedoc_id(request.form.get("doc_type"))
    form_letter.template = request.form.get("template")
    return form_letter


def mbuild_search_filter(fdict):
    filtr = []
    if fdict.get('code') != '':
        filtr.append(FormLetter.code.ilike(f"%{fdict.get('code')}%"))
    if fdict.get('description') != '':
        filtr.append(FormLetter.description.ilike(f"%{fdict.get('description')}%"))
    if fdict.get('subject') != '':
        filtr.append(FormLetter.subject.ilike(f"%{fdict.get('subject')}%"))
    if fdict.get('block') != '':
        filtr.append(FormLetter.block.ilike(f"%{fdict.get('block')}%"))
    if fdict.get('doc_type') != 'all doc types':
        filtr.append(FormLetter.doctype_id == get_typedoc_id(fdict.get('doc_type')))
    return filtr


def clone_form_letter(form_letter_id):
    form_letter = get_form_letter(form_letter_id)
    form_letter_copy = FormLetter()
    form_letter_copy.code = form_letter.code + ' copy'
    form_letter_copy.description = form_letter.description
    form_letter_copy.subject = form_letter.subject
    form_letter_copy.block = form_letter.block
    form_letter_copy.doctype_id = form_letter.doctype_id
    form_letter_copy.template = form_letter.template
    return post_form_letter(form_letter_copy)


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
            'block': request.form.get("block") or "",
            'doc_type': request.form.get("doc_type")}


def mget_form_letters_from_search():
    fdict = mget_form_letters_dict()
    filtr = mbuild_search_filter(fdict)
    form_letters = get_form_letters_from_search(filtr) if filtr else get_form_letters_all()
    return form_letters, fdict


def mget_pr_defaults():
    settings = get_user_settings()
    return {'pr_default': settings.get('pr_default'),
            'pr_email_default': settings.get('pr_email_default')} if settings else ''


def mpost_form_letter(form_letter_id):
    form_letter = mbuild_form_letter_from_form(get_form_letter(form_letter_id))
    return post_form_letter(form_letter)


def mpost_form_letter_new():
    form_letter = mbuild_form_letter_from_form(FormLetter())
    return post_form_letter(form_letter)


def msave_pr_defaults():
    defaults = {'pr_default': request.form.get('pr_default'),
                'pr_email_default': request.form.get('pr_email_default')}
    settings = get_user_settings()
    if not settings:
        settings = defaults
    else:
        settings.update(defaults)
    post_user_settings(settings)
