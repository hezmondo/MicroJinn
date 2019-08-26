from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import asc, desc, extract, func, literal, and_, or_
from werkzeug.urls import url_parse

from app import app, db
from app.email import send_password_reset_email
from app.forms import EditProfileForm, LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import Agent, Charge, Chargetype, Datef2, Datef4, Extmanager, Extrent, Income, Incomealloc, \
    Landlord, Manager, Property, Rent, Typeactype, Typeadvarr, Typebankacc, Typedeed, Typefreq, Typemailto, \
    Typepayment, Typeproperty, Typesalegrade, Typestatus, Typetenure, User, Emailaccount
from app.subroutes.get import filteragents, filtercharges, filterrentobjs, getagent, getcharge, getemailacc, \
    getlandlord, getrentobj
from app.subroutes.post import postagent, postcharge, postemailacc, postlandlord, postrentobj


def subagents():
    if request.method == "POST":
        agents = filteragents("post")
    else:
        agents = filteragents("get")
    return agents


def subagentp(id):
    if request.method == "POST":
        postagent(id)
    else:
        pass
    agent = getagent(id)
    return agent


def subcharges():
    rentcode = request.args.get('rentcode', "view", type=str)
    if request.method == "POST":
        rcd = request.form["rentcode"]
        cdt = request.form["chargedetails"]
    elif not rentcode == "view":
        rcd = rentcode
    else:
        rcd = ""
    cdt = ""
    charges = filtercharges(rcd, cdt)
    return charges


def subchargep(id):
    if request.method == "POST":
        postcharge(id)
    else:
        pass
    charge, chargedescs = getcharge(id)
    return charge, chargedescs


def subemailaccp(id):
    if request.method == "POST":
        postemailacc(id, action="edit")
    else:
        pass
    emailacc = getemailacc(id)

    return render_template('emailaccpage.html', title='Email account', emailacc=emailacc)


def subindex():
    if request.method == "POST":
        rcd = request.form["rentcode"]
        ten = request.form["tenantname"]
        pop = request.form["propaddr"]
        rentobjs = filterrentobjs(rcd, ten, pop)
    else:
        rentobjs = filterrentobjs("ZWEF", "", "")
    return rentobjs


def sublandlordp(id):
    action = request.args.get('action', "view", type=str)
    if request.method == "POST":
        postlandlord(id, action)
    else:
        pass
    landlord, managers, emailaccs, bankaccs= getlandlord(id)
    return landlord, managers, emailaccs, bankaccs


def subrentobjp(id):
    action = request.args.get('action', "view", type=str)
    if request.method == "POST":
        postrentobj(id, action)
    else:
        pass
    rentobj, actypedets, advarrdets, deedcodes, freqdets, landlords, mailtodets, \
    proptypedets, salegradedets, statusdets, tenuredets = getrentobj(id)
    # totcharges = Rent.query.join(Charge).with_entities(func.sum(Charge.chargebalance).label("totcharges")). \
    #     filter(Rent.id == id) \
    #         .one_or_none()

    return action, rentobj, actypedets, advarrdets, deedcodes, freqdets, landlords, mailtodets, \
                       proptypedets, salegradedets, statusdets, tenuredets




