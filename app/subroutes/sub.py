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
from app.subroutes.get import filteragents, filtercharges, filteremailaccs, filterextrents, filterheadrents, \
    filterincome, filterlandlords, filterrentobjs, getagent, getcharge, getemailacc, \
    getextrent, getlandlord, getrentobj
from app.subroutes.post import postagent, postcharge, postemailacc, postlandlord, postrentobj


def subagents():
    if request.method == "POST":
        agd = request.form["address"]
        age = request.form["email"]
        agn = request.form["notes"]
    else:
        agd = "Jones"
        age = ""
        agn = ""
    agents = filteragents(agd, age, agn)
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


def subdeleteitem(id):
    item = request.args.get('item', "view", type=str)
    if item == "agent":
        agent = Agent.query.get(id)
        db.session.delete(agent)
        db.session.commit()
    elif item == "charge":
        charge = Charge.query.get(id)
        db.session.delete(charge)
        db.session.commit()
    elif item == "emailacc":
        emailacc = Emailaccount.query.get(id)
        db.session.delete(emailacc)
        db.session.commit()
        # return redirect('/emailaccs')
    elif item == "landlord":
        landlord = Landlord.query.get(id)
        if landlord:
            db.session.delete(landlord)
            db.session.commit()
    elif item == "rentprop":
        delete_rent = Rent.query.get(id)
        delete_property = Property.query.filter(Property.rent_id == id).first()
        if delete_property:
            db.session.delete(delete_property)
            db.session.delete(delete_rent)
            db.session.commit()
    return


def subemailaccp(id):
    if request.method == "POST":
        postemailacc(id)
    else:
        pass
    emailacc = getemailacc(id)
    return emailacc


def subemailaccs():
    emailaccs = filteremailaccs()
    return emailaccs


def subextrentp(id):
    extrent = getextrent(id)
    return extrent


def subextrents():
    extrents = filterextrents()
    return extrents


def subheadrents():
    headrents = filterheadrents()
    return headrents


def subincome():
    income = filterincome()
    return income


def subindex():
    if request.method == "POST":
        rcd = request.form["rentcode"]
        ten = request.form["tenantname"]
        pop = request.form["propaddr"]
        rentobjs = filterrentobjs(rcd, ten, pop)
    else:
        rentobjs = filterrentobjs("ZWEF", "", "")
    return rentobjs

def sublandlords():
    landlords = filterlandlords()
    return landlords



def sublandlordp(id):
    if request.method == "POST":
        postlandlord(id)
    else:
        pass
    landlord, managers, emailaccs, bankaccs = getlandlord(id)
    return landlord, managers, emailaccs, bankaccs


def submoney():
    money = None
    return money


def subpayrequests():
    payrequests = None
    return payrequests


def subproperties():
    properties = None
    return properties


def subrentobjp(id):
    action = request.args.get('action', "view", type=str)
    if request.method == "POST":
        postrentobj(id)
    else:
        pass
    rentobj, actypedets, advarrdets, deedcodes, freqdets, landlords, mailtodets, \
    proptypedets, salegradedets, statusdets, tenuredets = getrentobj(id)
    # totcharges = Rent.query.join(Charge).with_entities(func.sum(Charge.chargebalance).label("totcharges")). \
    #     filter(Rent.id == id) \
    #         .one_or_none()

    return action, rentobj, actypedets, advarrdets, deedcodes, freqdets, landlords, mailtodets, \
                       proptypedets, salegradedets, statusdets, tenuredets




