# from datetime import datetime
import datetime
from dateutil.relativedelta import relativedelta
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


def filteragents(agd, age, agn):
    agents = \
        Agent.query \
            .with_entities(Agent.id, Agent.agdetails, Agent.agemail, Agent.agnotes) \
            .filter(Agent.agdetails.ilike('%{}%'.format(agd)),
                    Agent.agemail.ilike('%{}%'.format(age)),
                    Agent.agnotes.ilike('%{}%'.format(agn))) \
            .all()

    return agents

def filtercharges(rcd, cdt):
    charges = \
        Charge.query \
            .join(Rent) \
            .join(Chargetype) \
            .with_entities(Charge.id, Rent.rentcode, Chargetype.chargedesc, Charge.chargestartdate,
                           Charge.chargetotal, Charge.chargedetails, Charge.chargebalance) \
            .filter(Rent.rentcode.startswith([rcd]),
                    Charge.chargedetails.ilike('%{}%'.format(cdt))) \
            .all()

    return charges


def filteremailaccs():
    emailaccs = \
        Emailaccount.query \
            .with_entities(Emailaccount.id, Emailaccount.smtp_server, Emailaccount.smtp_user,
                           Emailaccount.smtp_sendfrom, Emailaccount.imap_sentfolder, Emailaccount.imap_draftfolder) \
            .all()
    return emailaccs


def filterextrents():
    if request.method == "POST":
        rcd = request.form["rentcode"]
        ten = request.form["tenantname"]
        pop = request.form["propaddr"]
    else:
        rcd = "lus"
        ten = ""
        pop = ""
    extrents = \
        Extrent.query \
            .join(Extmanager) \
            .with_entities(Extrent.id, Extrent.rentcode, Extrent.propaddr, Extrent.tenantname, Extrent.owner,
                           Extrent.rentpa, Extrent.arrears, Extrent.lastrentdate, Extrent.source, Extrent.status,
                           Extmanager.codename, Extrent.agentdetails) \
            .filter(Extrent.rentcode.startswith([rcd]),
                    Extrent.tenantname.ilike('%{}%'.format(ten)),
                    Extrent.propaddr.ilike('%{}%'.format(pop))) \
            .all()

    return extrents

def filterheadrents():
#     if request.method == "POST":
        # hrcd = request.form["headrentcode"]
        # agd = request.form["agentdetails"]
        # pop = request.form["propaddr"]
    # else:
        # headrents = getheadrents("", "COMP", "")
    headrents = None
    return headrents


def filterincome():
    # if request.method == "POST":
        # rcd = request.form["rentcode"]
        # ten = request.form["tenantname"]
        # pop = request.form["propaddr"]
        # rents = getrents(rcd, ten, pop)
    #     return redirect(url_for('income'))
    # else:
    #     rcd = "ZCAS"
    #     rents = getrents(rcd, "", "")
    income = None
    return income


def filterlandlords():
    landlords = \
        Landlord.query.join(Manager) \
            .with_entities(Landlord.id, Landlord.name, Landlord.addr, Landlord.taxdate,
                           Manager.name.label("manager")) \
            .all()
    return landlords


def filterrentobjs(rcd, ten, pop):
    rentobjs = \
        Property.query \
            .join(Rent) \
            .join(Landlord) \
            .outerjoin(Agent) \
            .with_entities(Rent.id, Rent.rentcode, Rent.tenantname, Rent.rentpa, Rent.arrears, Rent.lastrentdate,
                           Property.propaddr, Landlord.name, Agent.agdetails) \
            .filter(Rent.rentcode.startswith([rcd]),
                    Rent.tenantname.ilike('%{}%'.format(ten)),
                    Property.propaddr.ilike('%{}%'.format(pop))) \
            .all()
    return rentobjs


def getagent(id):
    ida = id
    agent = \
        Agent.query \
            .with_entities(Agent.id, Agent.agdetails, Agent.agemail, Agent.agnotes) \
            .filter(Agent.id == ida) \
            .one_or_none()
    if agent is None:
        flash('Invalid agent code')
        return redirect(url_for('agents'))
    return agent


def getcharge(id):
    charge = \
        Charge.query \
            .join(Rent) \
            .join(Chargetype) \
            .with_entities(Charge.id, Rent.rentcode, Chargetype.chargedesc, Charge.chargestartdate,
                           Charge.chargetotal, Charge.chargedetails, Charge.chargebalance) \
            .filter(Charge.id == id) \
            .one_or_none()
    chargedescs = [value for (value,) in Chargetype.query.with_entities(Chargetype.chargedesc).all()]
    return charge, chargedescs


def getemailacc(id):
    if id > 0:
        # existing emailacc
        emailacc = \
            Emailaccount.query \
                .with_entities(Emailaccount.id, Emailaccount.smtp_server, Emailaccount.smtp_port,
                               Emailaccount.smtp_timeout, Emailaccount.smtp_debug, Emailaccount.smtp_tls,
                               Emailaccount.smtp_user, Emailaccount.smtp_password, Emailaccount.smtp_sendfrom,
                               Emailaccount.imap_server, Emailaccount.imap_port, Emailaccount.imap_tls,
                               Emailaccount.imap_user, Emailaccount.imap_password, Emailaccount.imap_sentfolder,
                               Emailaccount.imap_draftfolder) \
                .filter(Emailaccount.id == id) \
                .one_or_none()
    else:
        # new emailacc
        emailacc = {
            'id': 0,
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'smtp_timeout': 20,
            'smtp_debug': 0,
            'smtp_tls': 0,
            'smtp_user': 'hesmaloney@gmail.com',
            'smtp_password': 'abcdefgh',
            'smtp_sendfrom': 'hesmaloney@gmail.com',
            'imap_server': 'imap.gmail.com',
            'imap_port': 993,
            'imap_tls': 0,
            'imap_user': '',
            'imap_password': 'abcdefgh',
            'imap_sentfolder': 'Sent',
            'imap_draftfolder': 'Draft'
        }
    return emailacc


def getextrent(id):
    # if request.method == "POST":
    #
    #     return redirect(url_for('index'))
    # else:
    # pass
    extrent = \
        Extrent.query \
            .join(Extmanager) \
            .with_entities(Extrent.rentcode, Extrent.propaddr, Extrent.tenantname, Extrent.owner,
                           Extrent.rentpa, Extrent.arrears, Extrent.lastrentdate, Extrent.source,
                           Extmanager.codename, Extrent.agentdetails) \
            .filter(Extrent.id == id) \
                .one_or_none()
    if extrent is None:
        flash('N')
        return redirect(url_for('index'))
    return extrent


def getlandlord(id):
    if id > 0:
        # existing landlord
        landlord = \
            Landlord.query.join(Manager).join(Emailaccount).join(Typebankacc) \
                .with_entities(Landlord.id, Landlord.name, Landlord.addr, Landlord.taxdate,
                               Manager.name.label("manager"), Emailaccount.smtp_server, Typebankacc.accnum) \
                .filter(Landlord.id == id) \
                .one_or_none()
        if landlord is None:
            flash('Invalid landlord id')
            return redirect('/landlords')
    else:
        # new landlord
        landlord = {
            'id': 0,
            'taxdate': "2000-04-05"
        }
    managers = [value for (value,) in Manager.query.with_entities(Manager.name).all()]
    emailaccs = [value for (value,) in Emailaccount.query.with_entities(Emailaccount.smtp_server).all()]
    bankaccs = [value for (value,) in Typebankacc.query.with_entities(Typebankacc.accnum).all()]
    return landlord, managers, emailaccs, bankaccs


def getrentobj(id):
    # This method returns a "rentobj" object
    # information about a rent, plus its related property/agent/landlord stuff
    # plus all the list values to offer for various comboboxes
    # all of this is to be shown in rentobjpage.html
    # that allows either editing etc. of an existing rent (whose `id` is specified)
    # (in which case we fetch the rent info to edit)
    # or it allows creation of a new rent (signified by id==0)
    # (in which case for the rent info we have to "invent" an object
    # with the same attributes as would have been fetched from the database
    # but with "blanks", or default values, as desired for creating a new rent
    # --- seems like Flask is happy for it not even to have the fields which will be referenced
    # so just put in any defaults desired)
    if id > 0:
        # existing rent
        rentobj = \
            Property.query \
                .join(Rent) \
                .join(Landlord) \
                .outerjoin(Agent) \
                .join(Typeactype) \
                .join(Typeadvarr) \
                .join(Typedeed) \
                .join(Typefreq) \
                .join(Typemailto) \
                .join(Typeproperty) \
                .join(Typesalegrade) \
                .join(Typestatus) \
                .join(Typetenure) \
                .with_entities(Rent.id, Rent.rentcode, Rent.arrears, Rent.datecode, Rent.email, Rent.lastrentdate,
                               Rent.note, Rent.price, Rent.rentpa, Rent.source, Rent.tenantname,
                               Agent.agdetails, Landlord.name, Property.propaddr, Typeactype.actypedet,
                               Typeadvarr.advarrdet, Typedeed.deedcode, Typefreq.freqdet, Typemailto.mailtodet,
                               Typeproperty.proptypedet, Typesalegrade.salegradedet, Typestatus.statusdet,
                               Typetenure.tenuredet) \
                .filter(Rent.id == id) \
                .one_or_none()
        if rentobj is None:
            flash('Invalid rent code')
            return redirect(url_for('login'))
    else:
        # new rent
        rentobj = {
            'id': 0
        }

    actypedets = [value for (value,) in Typeactype.query.with_entities(Typeactype.actypedet).all()]
    advarrdets = [value for (value,) in Typeadvarr.query.with_entities(Typeadvarr.advarrdet).all()]
    deedcodes = [value for (value,) in Typedeed.query.with_entities(Typedeed.deedcode).all()]
    freqdets = [value for (value,) in Typefreq.query.with_entities(Typefreq.freqdet).all()]
    landlords = [value for (value,) in Landlord.query.with_entities(Landlord.name).all()]
    mailtodets = [value for (value,) in Typemailto.query.with_entities(Typemailto.mailtodet).all()]
    proptypedets = [value for (value,) in Typeproperty.query.with_entities(Typeproperty.proptypedet).all()]
    salegradedets = [value for (value,) in Typesalegrade.query.with_entities(Typesalegrade.salegradedet).all()]
    statusdets = [value for (value,) in Typestatus.query.with_entities(Typestatus.statusdet).all()]
    tenuredets = [value for (value,) in Typetenure.query.with_entities(Typetenure.tenuredet).all()]

    return rentobj, actypedets, advarrdets, deedcodes, freqdets, landlords, mailtodets, proptypedets, \
           salegradedets, statusdets, tenuredets
