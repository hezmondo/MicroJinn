# from datetime import datetime
import datetime
from dateutil.relativedelta import relativedelta
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import asc, desc, extract, func, literal, and_, or_
from werkzeug.urls import url_parse

from app import app, db
from app.email import send_password_reset_email
from app.forms import EditProfileForm, LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm, \
    JinnForm, RentForm
from app.models import Agent, Charge, Chargetype, Datef2, Datef4, Extmanager, Extrent, Income, Incomealloc, \
    Landlord, Manager, Property, Rent, Typeactype, Typeadvarr, Typebankacc, Typedeed, Typefreq, Typemailto, \
    Typepayment, Typeproperty, Typesalegrade, Typestatus, Typetenure, User, Emailaccount
from app.tables import Results


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.datetime.utcnow()
        db.session.commit()


@app.route('/chargepage/<int:id>', methods=["POST", "GET"])
@login_required
def chargepage(id):
    if request.method == "POST":
        rcd = request.form["rentcode"]
        cdt = request.form["chargedetails"]
        charges = \
            Charge.query \
                .join(Rent) \
                .join(Chargetype) \
                .with_entities(Charge.id, Rent.rentcode, Chargetype.chargedesc, Charge.chargestartdate,
                               Charge.chargetotal, Charge.chargedetails, Charge.chargebalance) \
                .filter(Rent.rentcode.startswith([rcd]),
                        Charge.chargedetails.ilike('%{}%'.format(cdt))) \
                .all()
    else:
        idr = id
        charges = \
            Charge.query \
                .join(Rent) \
                .join(Chargetype) \
                .with_entities(Charge.id, Rent.rentcode, Chargetype.chargedesc, Charge.chargestartdate,
                               Charge.chargetotal, Charge.chargedetails, Charge.chargebalance) \
                .filter(Rent.id == idr) \
                .all()

    return render_template('chargepage.html', title='Charges', charges=charges)


@app.route('/clonerent/<int:id>', methods=["POST", "GET"])
@login_required
def clonerent(id):
    if request.method == "POST":
        rent, property, agent = savechanges(id, "clone")
        rent.rentcode = request.form["rentcode"]
        rent.prop_rent.append(property)

        # lots of challenges: this should deal with a new agent, but not to connect to an existing agent
        if agent and agent.agdetails != "None":
            agent.rent_agent.append(rent)
            db.session.add(agent)

        db.session.add(rent)
        db.session.commit()
        # `rent.id` gets updated to hold the INSERTed id
        new_id = rent.id

        return redirect('/editrent/{}'.format(new_id))
    else:
        rentdet, actypedets, advarrdets, deedcodes, freqdets, landlords, mailtodets, proptypedets, salegradedets, \
        statusdets, tenuredets = getvalues(id, "clone")

    return render_template('rentpage.html', action="clone", title='Clone rent', rent=rentdet, actypedets=actypedets,
                           advarrdets=advarrdets, deedcodes=deedcodes, freqdets=freqdets, landlords=landlords,
                           mailtodets=mailtodets, proptypedets=proptypedets, salegradedets=salegradedets,
                           statusdets=statusdets, tenuredets=tenuredets)


@app.route('/deleterentprop/<int:id>')
def deleterentprop(id):
    delete_rent = Rent.query.get(id)
    delete_property = Property.query.filter(Property.rent_id == id).first()
    if delete_property is not None:
        db.session.delete(delete_property)
    db.session.delete(delete_rent)
    db.session.commit()

    return redirect(url_for('index'))


@app.route('/signin/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username

    return render_template('edit_profile.html', title='Edit Profile', form=form)


@app.route('/editcharge/<int:id>', methods=["POST", "GET"])
@login_required
def editcharge(id):
    if request.method == "POST":
        charge = Charge.query.get(id)
        charge.chargetype_id = \
            Chargetype.query.with_entities(Chargetype.id).filter(
                Chargetype.chargedesc == request.form["chargedesc"]).one()[0]
        charge.chargestartdate = request.form["chargestartdate"]
        charge.chargetotal = request.form["chargetotal"]
        charge.chargedetails = request.form["chargedetails"]
        charge.chargebalance = request.form["chargebalance"]
        db.session.commit()
        return redirect('/editcharge/{}'.format(id))
    else:
        chargedet = \
            Charge.query \
                .join(Rent) \
                .join(Chargetype) \
                .with_entities(Charge.id, Rent.rentcode, Charge.chargetype_id, Chargetype.chargedesc,
                               Charge.chargestartdate, Charge.chargetotal, Charge.chargedetails, Charge.chargebalance) \
                .filter(Charge.id == id) \
                .one_or_none()
        if chargedet is None:
            flash('N')
            return redirect(url_for('login'))
        chargedescs = [value for (value,) in Chargetype.query.with_entities(Chargetype.chargedesc).all()]

    return render_template('editcharge.html', chargedescs=chargedescs, charge=chargedet)


@app.route('/editrent/<int:id>', methods=["POST", "GET"])
@login_required
def editrent(id):
    if request.method == "POST":
        rent, property, agent = savechanges(id, "edit")

        # lots of challenges: I have allowed for editing an existing agent, but not switching to another or new agent

        db.session.commit()

        return redirect('/editrent/{}'.format(id))
    else:
        rentdet, actypedets, advarrdets, deedcodes, freqdets, landlords, mailtodets, proptypedets, salegradedets, \
        statusdets, tenuredets = getvalues(id, "edit")
        # totcharges = Rent.query.join(Charge).with_entities(func.sum(Charge.chargebalance).label("totcharges")). \
        #     filter(Rent.id == id) \
        #         .one_or_none()

    return render_template('rentpage.html', action="edit", title='Edit rent', rent=rentdet, actypedets=actypedets,
                           advarrdets=advarrdets, deedcodes=deedcodes, freqdets=freqdets, landlords=landlords,
                           mailtodets=mailtodets, proptypedets=proptypedets, salegradedets=salegradedets,
                           statusdets=statusdets, tenuredets=tenuredets)


@app.route('/externalrent', methods=['GET', 'POST'])
@login_required
def externalrent():
    if request.method == "POST":
        rcd = request.form["rentcode"]
        pop = request.form["propaddr"]
        rents = []
    else:
        rcd = "lus"
        pop = ""
        rents = []
    rents = \
        Extrent.query \
            .join(Extmanager) \
            .with_entities(Extrent.id, Extrent.rentcode, Extrent.propaddr, Extrent.owner, Extrent.tenantname,
                           Extrent.rentpa, Extrent.arrears, Extrent.lastrentdate, Extmanager.codename) \
            .filter(Extrent.rentcode.startswith([rcd]),
                    Extrent.propaddr.ilike('%{}%'.format(pop))) \
            .all()
    return render_template('externalrent.html', title='ExternalRents', rents=rents)


def getrents(rcd, ten, pop):
    rents = \
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

    return rents


def getvalues(id, action):
    if action == "clone" or action == "edit":
        rentdet = \
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
                .join(Charge) \
                .with_entities(Rent.id, Rent.rentcode, Rent.arrears, Rent.datecode, Rent.email, Rent.lastrentdate,
                               Rent.note, Rent.price, Rent.rentpa, Rent.source, Rent.tenantname,
                               Agent.agdetails, Landlord.name, Property.propaddr, Typeactype.actypedet,
                               Typeadvarr.advarrdet, Typedeed.deedcode, Typefreq.freqdet, Typemailto.mailtodet,
                               Typeproperty.proptypedet, Typesalegrade.salegradedet, Typestatus.statusdet,
                               Typetenure.tenuredet,func.sum(Charge.chargebalance).label("totcharges")) \
                .filter(Rent.id == id) \
                .one_or_none()
        if rentdet is None:
            flash('Invalid rent code')
            return redirect(url_for('login'))
    elif action == "new":
        rentdet = None
    else:
        raise ValueError("getvalues(): Unrecognised value for 'action' (\"{}\")".format(action))

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

    return rentdet, actypedets, advarrdets, deedcodes, freqdets, landlords, mailtodets, proptypedets, \
           salegradedets, statusdets, tenuredets


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        rcd = request.form["rentcode"]
        ten = request.form["tenantname"]
        pop = request.form["propaddr"]
        rents = getrents(rcd, ten, pop)
    else:
        rcd = "ZCAS"
        rents = getrents(rcd, "", "")
    return render_template('index.html', title='Rent and property search page', rents=rents)


@app.route('/landlordpage/<int:id>', methods=["POST", "GET"])
@login_required
def landlordpage(id):
    if request.method == "POST":
        name = request.form["name"]
        addr = request.form["address"]
        taxdate = request.form["taxdate"]
        manager = request.form["manager"]
        return
    else:
        idl = id
        landlord = \
            Landlord.query.join(Manager) \
                .with_entities(Landlord.id, Landlord.name, Landlord.addr, Landlord.taxdate, Manager.name) \
                .filter(Landlord.id == idl) \
                .one_or_none()

    return render_template('landlordpage.html', title='Landlord', landlord=landlord)


@app.route('/landlords', methods=['GET', 'POST'])
@login_required
def landlords():
    if request.method == "POST":
        return

    else:
        landlords = \
            Landlord.query.join(Manager) \
                .with_entities(Landlord.id, Landlord.name, Landlord.addr, Landlord.taxdate,
                               Manager.name.label("manager")) \
                .all()

    return render_template('landlords.html', title='Landlords', landlords=landlords)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).one_or_none()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('/signin/login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/newrent', methods=['GET', 'POST'])
def newrent():
    id = 0
    if request.method == "POST":
        rent, property, agent = savechanges(id, "new")
        rent.rentcode = request.form["rentcode"]
        rent.prop_rent.append(property)

        # lots of challenges: this should deal with a new agent, but not to connect to an existing agent
        if agent and agent.agdetails != "None":
            agent.rent_agent.append(rent)
            db.session.add(agent)

        db.session.add(rent)
        db.session.commit()
        # `rent.id` gets updated to hold the INSERTed id
        new_id = rent.id

        return redirect('/editrent/{}'.format(new_id))
    else:
        rentdet, actypedets, advarrdets, deedcodes, freqdets, landlords, mailtodets, proptypedets, salegradedets, \
        statusdets, tenuredets = getvalues(id, "new")

    return render_template('newrent.html', title='New rent', actypedets=actypedets, advarrdets=advarrdets,
                           deedcodes=deedcodes, freqdets=freqdets, landlords=landlords, mailtodets=mailtodets,
                           proptypedets=proptypedets, salegradedets=salegradedets, statusdets=statusdets,
                           tenuredets=tenuredets)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('signin/register.html', title='Register', form=form)


@app.route('/rentpage/<int:id>', methods=["GET"])
@login_required
def rentpage(id):
    rentdet, actypedets, advarrdets, deedcodes, freqdets, landlords, mailtodets, proptypedets, salegradedets, \
    statusdets, tenuredets = getvalues(id, "edit")
    # totcharges = Rent.query.join(Charge).with_entities(func.sum(Charge.chargebalance).label("totcharges")). \
    #     filter(Rent.id == id) \
    #         .one_or_none()

    return render_template('rentpage.html', action="view", title='View rent', rent=rentdet, actypedets=actypedets,
                           advarrdets=advarrdets, deedcodes=deedcodes, freqdets=freqdets, landlords=landlords,
                           mailtodets=mailtodets, proptypedets=proptypedets, salegradedets=salegradedets,
                           statusdets=statusdets, tenuredets=tenuredets)


def savechanges(id, action):
    if action == "edit":
        rent = Rent.query.get(id)
        property = Property.query.filter(Property.rent_id == id).first()
        agent = Agent.query.filter(Agent.id == rent.agent_id).first()
    else:
        rent = Rent()
        property = Property()
        agent = Agent()

    actype = request.form["actype"]
    rent.actype_id = \
        Typeactype.query.with_entities(Typeactype.id).filter(Typeactype.actypedet == actype).one()[0]
    advarr = request.form["advarr"]
    rent.advarr_id = \
        Typeadvarr.query.with_entities(Typeadvarr.id).filter(Typeadvarr.advarrdet == advarr).one()[0]
    rent.arrears = request.form["arrears"]

    # we will write code later to generate datecode from lastrentdate!:
    rent.datecode = request.form["datecode"]

    deedtype = request.form["deedtype"]
    rent.deed_id = \
        Typedeed.query.with_entities(Typedeed.id).filter(Typedeed.deedcode == deedtype).one()[0]
    rent.email = request.form["email"]
    frequency = request.form["frequency"]
    rent.freq_id = \
        Typefreq.query.with_entities(Typefreq.id).filter(Typefreq.freqdet == frequency).one()[0]
    landlord = request.form["landlord"]
    rent.landlord_id = \
        Landlord.query.with_entities(Landlord.id).filter(Landlord.name == landlord).one()[0]
    rent.lastrentdate = request.form["lastrentdate"]
    mailto = request.form["mailto"]
    rent.mailto_id = \
        Typemailto.query.with_entities(Typemailto.id).filter(Typemailto.mailtodet == mailto).one()[0]
    rent.note = request.form["note"]
    rent.price = request.form["price"]
    rent.rentpa = request.form["rentpa"]
    salegrade = request.form["salegrade"]
    rent.salegrade_id = \
        Typesalegrade.query.with_entities(Typesalegrade.id).filter(Typesalegrade.salegradedet == salegrade).one()[0]
    rent.source = request.form["source"]
    status = request.form["status"]
    rent.status_id = \
        Typestatus.query.with_entities(Typestatus.id).filter(Typestatus.statusdet == status).one()[0]
    rent.tenantname = request.form["tenantname"]
    tenure = request.form["tenure"]
    rent.tenure_id = \
        Typetenure.query.with_entities(Typetenure.id).filter(Typetenure.tenuredet == tenure).one()[0]

    agent.agdetails = request.form["agent"]

    property.propaddr = request.form["propaddr"]
    proptype = request.form["proptype"]
    property.typeprop_id = \
        Typeproperty.query.with_entities(Typeproperty.id).filter(Typeproperty.proptypedet == proptype).one()[0]

    return rent, property, agent

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).one_or_none()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('/signin/reset_password_request.html', title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))

    return render_template('/signin/reset_password.html', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    return render_template('/signin/user.html', user=user)


@app.route('/agents', methods=['GET', 'POST'])
@login_required
def agents():
    if request.method == "POST":
        # rcd = request.form["rentcode"]
        # ten = request.form["tenantname"]
        # pop = request.form["propaddr"]
        # rents = getrents(rcd, ten, pop)
        return redirect(url_for('agents'))
    else:
    #     rcd = "ZCAS"
    #     rents = getrents(rcd, "", "")

        return render_template('agents.html', title='Agents')


@app.route('/headrents', methods=['GET', 'POST'])
@login_required
def headrents():
    if request.method == "POST":
        # rcd = request.form["rentcode"]
        # ten = request.form["tenantname"]
        # pop = request.form["propaddr"]
        # rents = getrents(rcd, ten, pop)
        return redirect(url_for('headrents'))
    else:
    #     rcd = "ZCAS"
    #     rents = getrents(rcd, "", "")

        return render_template('headrents.html', title='Headrents')


@app.route('/income', methods=['GET', 'POST'])
@login_required
def income():
    if request.method == "POST":
        # rcd = request.form["rentcode"]
        # ten = request.form["tenantname"]
        # pop = request.form["propaddr"]
        # rents = getrents(rcd, ten, pop)
        return redirect(url_for('income'))
    else:
    #     rcd = "ZCAS"
    #     rents = getrents(rcd, "", "")
        return render_template('income.html', title='Income')

@app.route('/money', methods=['GET', 'POST'])
@login_required
def money():
    if request.method == "POST":
        # rcd = request.form["rentcode"]
        # ten = request.form["tenantname"]
        # pop = request.form["propaddr"]
        # rents = getrents(rcd, ten, pop)
        return redirect(url_for('money'))
    else:
    #     rcd = "ZCAS"
    #     rents = getrents(rcd, "", "")

        return render_template('money.html', title='Money')


@app.route('/payrequests', methods=['GET', 'POST'])
@login_required
def payrequests():
    if request.method == "POST":
        # rcd = request.form["rentcode"]
        # ten = request.form["tenantname"]
        # pop = request.form["propaddr"]
        # rents = getrents(rcd, ten, pop)
        return redirect(url_for('payrequests'))
    else:
    #     rcd = "ZCAS"
    #     rents = getrents(rcd, "", "")

        return render_template('payrequests.html', title='Payrequests')


@app.route('/properties', methods=['GET', 'POST'])
@login_required
def properties():
    if request.method == "POST":
        # rcd = request.form["rentcode"]
        # ten = request.form["tenantname"]
        # pop = request.form["propaddr"]
        # rents = getrents(rcd, ten, pop)
        return redirect(url_for('properties'))
    else:
    #     rcd = "ZCAS"
    #     rents = getrents(rcd, "", "")

        return render_template('properties.html', title='Properties')


@app.route('/utilities', methods=['GET', 'POST'])
@login_required
def utilities():
    if request.method == "POST":
        # rcd = request.form["rentcode"]
        # ten = request.form["tenantname"]
        # pop = request.form["propaddr"]
        # rents = getrents(rcd, ten, pop)
        return redirect(url_for('utilities'))
    else:
    # rcd = "ZCAS"
    #     rents = getrents(rcd, "", "")

        return render_template('utilities.html', title='utilities')

