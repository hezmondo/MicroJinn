# from datetime import datetime
import datetime
from dateutil.relativedelta import relativedelta
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse

from app import app, db
from app.email import send_password_reset_email
from app.forms import EditProfileForm, LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm, \
    JinnForm, RentForm
from app.models import Agent, Charge, Chargetype, Datef2, Datef4, Extmanager, Extrent, Income, Incomealloc, \
    Landlord, Manager, Property, Rent, Typeactype, Typeadvarr, Typebankacc, Typedeed, Typefreq, Typemailto, \
    Typepayment, Typeproperty, Typesalegrade, Typestatus, Typetenure, User
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
                .filter(Rent.id == ('{}'.format(idr))) \
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
        new_id = \
            Property.query \
                .join(Rent) \
            .with_entities(Rent.id).filter(Property.propaddr == property.propaddr).first()[0]

        return redirect('/editrent/{}'.format(new_id))
    else:
        rentdet, actypedets, advarrdets, deedcodes, freqdets, landlords, mailtodets, proptypedets, salegradedets, \
        statusdets, tenuredets = getvalues(id, "clone")

    return render_template('editrent.html', title='Clone rent', rent=rentdet, actypedets=actypedets,
                           advarrdets=advarrdets, deedcodes=deedcodes, freqdets=freqdets, landlords=landlords,
                           mailtodets=mailtodets, proptypedets=proptypedets, salegradedets=salegradedets,
                           statusdets=statusdets, tenuredets=tenuredets)


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
        thischarge = Charge.query.get(id)
        thischarge.chargetype_id = \
            Chargetype.query.with_entities(Chargetype.id).filter(
                Chargetype.chargedesc == request.form["chargedesc"]).first()[0]
        thischarge.chargestartdate = request.form["chargestartdate"]
        thischarge.chargetotal = request.form["chargetotal"]
        thischarge.chargedetails = request.form["chargedetails"]
        thischarge.chargebalance = request.form["chargebalance"]
        db.session.commit()
        return redirect('/editcharge/{}'.format(id))
    else:
        chargedet = \
            Charge.query \
                .join(Rent) \
                .join(Chargetype) \
                .with_entities(Charge.id, Rent.rentcode, Charge.chargetype_id, Chargetype.chargedesc,
                               Charge.chargestartdate, Charge.chargetotal, Charge.chargedetails, Charge.chargebalance) \
                .filter(Charge.id == ('{}'.format(id))) \
                .first()
        if chargedet is None:
            flash('N')
            return redirect(url_for('login'))
        chargedescs = Chargetype.query.with_entities(Chargetype.chargedesc).all()
        chargedescs = [value for (value,) in chargedescs]

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

    return render_template('editrent.html', title='Edit rent', rent=rentdet, actypedets=actypedets,
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


@app.route('/deleterentprop/<int:id>')
def deleteitem(id):
    delete_rent = Rent.query.get(id)
    delete_property = Property.query.filter(Property.rent_id == ('{}'.format(id))).first()
    if delete_property is not None:
        db.session.delete(delete_property)
    db.session.delete(delete_rent)
    db.session.commit()

    return redirect(url_for('index'))


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == "POST":
        rcd = request.form["rentcode"]
        ten = request.form["tenantname"]
        pop = request.form["propaddr"]
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
    else:
        rents = []
    return render_template('homepage.html', title='JinnHome', rents=rents)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
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
        new_id = \
            Property.query \
                .join(Rent) \
            .with_entities(Rent.id).filter(Property.propaddr == property.propaddr).first()[0]

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


@app.route('/rentpage')
@login_required
def rentpage():
    rentid = 111
    rentdet = \
        Property.query \
            .join(Rent) \
            .join(Landlord) \
            .outerjoin(Agent) \
            .with_entities(Rent.id, Rent.rentcode, Rent.tenantname, Rent.mailto_id, Rent.rentpa, Rent.arrears,
                           Rent.advarr_id, Rent.lastrentdate, Rent.freq_id, Rent.datecode, Rent.actype_id,
                           Rent.tenure_id, Rent.source, Rent.deed_id, Rent.status_id, Rent.salegrade_id, Rent.price,
                           Rent.note, Rent.email, Property.propaddr, Landlord.name, Agent.agdetails) \
            .filter(Rent.id == ('{}'.format(rentid))) \
            .first()
    if rentdet is None:
        flash('Invalid rent code')
        return redirect(url_for('login'))
    return render_template('rentpage.html', rents=rentdet)

def savechanges(id, type):
    if type == "edit":
        rent = Rent.query.get(id)
        property = Property.query.filter(Property.rent_id == id).first()
        agent = Agent.query.filter(Agent.id == rent.agent_id).first()
    else:
        rent = Rent()
        property = Property()
        agent = Agent()
    actype = request.form["actype"]
    rent.actype_id = \
        Typeactype.query.with_entities(Typeactype.id).filter(Typeactype.actypedet == actype).first()[0]
    advarr = request.form["advarr"]
    rent.advarr_id = \
        Typeadvarr.query.with_entities(Typeadvarr.id).filter(Typeadvarr.advarrdet == advarr).first()[0]
    rent.arrears = request.form["arrears"]

    # we will write code later to generate datecode from lastrentdate!:
    rent.datecode = request.form["datecode"]

    deedtype = request.form["deedtype"]
    rent.deed_id = \
        Typedeed.query.with_entities(Typedeed.id).filter(Typedeed.deedcode == deedtype).first()[0]
    rent.email = request.form["email"]
    frequency = request.form["frequency"]
    rent.freq_id = \
        Typefreq.query.with_entities(Typefreq.id).filter(Typefreq.freqdet == frequency).first()[0]
    landlord = request.form["landlord"]
    rent.landlord_id = \
        Landlord.query.with_entities(Landlord.id).filter(Landlord.name == landlord).first()[0]
    rent.lastrentdate = request.form["lastrentdate"]
    mailto = request.form["mailto"]
    rent.mailto_id = \
        Typemailto.query.with_entities(Typemailto.id).filter(Typemailto.mailtodet == mailto).first()[0]
    rent.note = request.form["note"]
    rent.price = request.form["price"]
    rent.rentpa = request.form["rentpa"]
    salegrade = request.form["salegrade"]
    rent.salegrade_id = \
        Typesalegrade.query.with_entities(Typesalegrade.id).filter(Typesalegrade.salegradedet == salegrade).first()[
            0]
    rent.source = request.form["source"]
    status = request.form["status"]
    rent.status_id = \
        Typestatus.query.with_entities(Typestatus.id).filter(Typestatus.statusdet == status).first()[0]
    rent.tenantname = request.form["tenantname"]
    tenure = request.form["tenure"]
    rent.tenure_id = \
        Typetenure.query.with_entities(Typetenure.id).filter(Typetenure.tenuredet == tenure).first()[0]
    agent.agdetails = request.form["agent"]
    property.propaddr = request.form["propaddr"]
    proptype = request.form["proptype"]
    property.typeprop_id = \
        Typeproperty.query.with_entities(Typeproperty.id).filter(Typeproperty.proptypedet == proptype).first()[0]
    return rent, property, agent


def getvalues(id, type):
    if type == "clone" or type == "edit":
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
                .with_entities(Rent.id, Rent.rentcode, Rent.arrears, Rent.datecode, Rent.email, Rent.lastrentdate,
                               Rent.note, Rent.price, Rent.rentpa, Rent.source, Rent.tenantname,
                               Agent.agdetails, Landlord.name, Property.propaddr, Typeactype.actypedet,
                               Typeadvarr.advarrdet, Typedeed.deedcode, Typefreq.freqdet, Typemailto.mailtodet,
                               Typeproperty.proptypedet, Typesalegrade.salegradedet, Typestatus.statusdet,
                               Typetenure.tenuredet) \
                .filter(Rent.id == ('{}'.format(id))) \
                .first()
        if rentdet is None:
            flash('Invalid rent code')
            return redirect(url_for('login'))
    else:
        rentdet = None
    actypedets = Typeactype.query.with_entities(Typeactype.actypedet).all()
    actypedets = [value for (value,) in actypedets]
    advarrdets = Typeadvarr.query.with_entities(Typeadvarr.advarrdet).all()
    advarrdets = [value for (value,) in advarrdets]
    deedcodes = Typedeed.query.with_entities(Typedeed.deedcode).all()
    deedcodes = [value for (value,) in deedcodes]
    freqdets = Typefreq.query.with_entities(Typefreq.freqdet).all()
    freqdets = [value for (value,) in freqdets]
    landlords = Landlord.query.with_entities(Landlord.name).all()
    landlords = [value for (value,) in landlords]
    mailtodets = Typemailto.query.with_entities(Typemailto.mailtodet).all()
    mailtodets = [value for (value,) in mailtodets]
    proptypedets = Typeproperty.query.with_entities(Typeproperty.proptypedet).all()
    proptypedets = [value for (value,) in proptypedets]
    salegradedets = Typesalegrade.query.with_entities(Typesalegrade.salegradedet).all()
    salegradedets = [value for (value,) in salegradedets]
    statusdets = Typestatus.query.with_entities(Typestatus.statusdet).all()
    statusdets = [value for (value,) in statusdets]
    tenuredets = Typetenure.query.with_entities(Typetenure.tenuredet).all()
    tenuredets = [value for (value,) in tenuredets]
    return rentdet, actypedets, advarrdets, deedcodes, freqdets, landlords, mailtodets, proptypedets, \
            salegradedets, statusdets, tenuredets


def replace_users(dictum, key_to_find, definition):
    for key in dictum.keys():
        if key == key_to_find:
            current_dict[key] = definition


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
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
