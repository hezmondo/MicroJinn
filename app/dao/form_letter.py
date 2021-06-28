from app import db
import json
from sqlalchemy import select
from sqlalchemy.orm import load_only
from app.models import FormLetter, User
from app.dao.database import commit_to_database
from flask_login import current_user
from app.dao.doc import get_typedoc_id


def get_form_id(form_letter_code):
    form = db.session.query(FormLetter).filter_by(code=form_letter_code).options(load_only('id')).one_or_none()
    return form.id


def get_form_letter(form_letter_id):
    return FormLetter.query.filter_by(id=form_letter_id).first()


def get_form_letters_all():
    return db.session.execute(select(FormLetter).order_by(FormLetter.code)).scalars().all()


def get_form_letters_from_search(filtr):
    return db.session.execute(select(FormLetter).where(*filtr)).scalars().all()


def get_form_letters_lease():
    return db.session.execute(
        select(FormLetter).where(FormLetter.code.ilike('LEQ-%')).order_by(FormLetter.code)).scalars().all()


def get_form_letters_other():
    return db.session.execute(select(FormLetter).where(FormLetter.code.notilike('PR-%'),
                                                       FormLetter.code.notilike('AC-%'),
                                                       FormLetter.code.notilike('LEQ-%')).order_by(
        FormLetter.code)).scalars().all()


def get_form_letters_pr():
    return db.session.execute(
        select(FormLetter).where(FormLetter.doctype_id == 2).order_by(FormLetter.code)).scalars().all()


def get_pr_form_code(pr_form_id):
    return db.session.query(FormLetter).filter_by(id=pr_form_id).options(load_only('code')).one_or_none()


def get_pr_form_essential(pr_form_id):
    return db.session.query(FormLetter).filter_by(id=pr_form_id).options(load_only('code', 'block', 'subject')) \
        .one_or_none()


def get_pr_email_form():
    return db.session.query(FormLetter).filter_by(code='EPR').options(load_only('block')).one_or_none()


def get_pr_forms():
    return FormLetter.query.filter(FormLetter.doctype_id == 2).all()


def get_pr_form_codes():
    pr_forms = db.session.query(FormLetter).filter_by(doctype_id=2).options(load_only('code')).all()
    pr_template_codes = []
    for pr_form in pr_forms:
        pr_template_codes.append(pr_form.code)
    return pr_template_codes


def post_form_letter(form_letter):
    db.session.add(form_letter)
    commit_to_database()
    return form_letter.id
