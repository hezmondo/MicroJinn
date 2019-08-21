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


@app.route('/agents', methods=['GET', 'POST'])
@login_required
def agents():
    if request.method == "POST":
        agd = request.form["address"]
        age = request.form["email"]
        agn = request.form["notes"]
        agents = filteragents(agd, age, agn)
    else:
        agd = "Jones"
        agents = filteragents(agd, "", "")

    return render_template('agents.html', title='Agent search page', agents=agents)


@app.route('/agentpage/<int:id>', methods=["GET", "POST"])
@login_required
def agentpage(id):
    if request.method == "POST":
        agent = Agent.query.get(id)
        agent.agdetails = request.form["address"]
        agent.agemail = request.form["email"]
        agent.agnotes = request.form["notes"]
        db.session.commit()

        return redirect(url_for('agents'))

    else:
        ida = id
        agent = \
            Agent.query \
                .with_entities(Agent.id, Agent.agdetails, Agent.agemail, Agent.agnotes) \
                .filter(Agent.id == ida) \
                .one_or_none()
        if agent is None:
            flash('Invalid agent code')
            return redirect(url_for('agents'))

        return render_template('agentpage.html', title='Agent', agent=agent)


@app.route('/chargepage/<int:id>', methods=["GET"])
@login_required
def chargepage(id):
    idr = id
    charges = \
        Charge.query \
            .join(Rent) \
            .join(Chargetype) \
            .with_entities(Charge.id, Rent.rentcode, Chargetype.chargedesc, Charge.chargestartdate,
                           Charge.chargetotal, Charge.chargedetails, Charge.chargebalance) \
            .filter(Rent.id == idr) \
            .all()

    return render_template('charges.html', title='Charges', charges=charges)


@app.route('/charges', methods=['GET', 'POST'])
def charges():
    if request.method == "POST":
        rcd = request.form["rentcode"]
        cdt = request.form["chargedetails"]
    else:
        rcd = ""
        cdt = ""
    charges = filtercharges(rcd, cdt)

    return render_template('charges.html', title='Charges page', charges=charges)


@app.route('/clonerentprop/<int:id>', methods=["POST", "GET"])
@login_required
def clonerentprop(id):
    if request.method == "POST":
        rent, property, agent = postrentprop(id, "clone")
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

        return redirect('/editrentprop/{}'.format(new_id))
    else:
        rentprop, actypedets, advarrdets, deedcodes, freqdets, landlords, mailtodets, proptypedets, salegradedets, \
        statusdets, tenuredets = getrentpropvalues(id, action="clone")

    return render_template('rentproppage.html', action="clone", title='Clone rent', rentprop=rentprop, actypedets=actypedets,
                           advarrdets=advarrdets, deedcodes=deedcodes, freqdets=freqdets, landlords=landlords,
                           mailtodets=mailtodets, proptypedets=proptypedets, salegradedets=salegradedets,
                           statusdets=statusdets, tenuredets=tenuredets)


@app.route('/deleteagent/<int:id>')
def deleteagent(id):
    agent = Agent.query.get(id)
    db.session.delete(agent)
    db.session.commit()

    return redirect(url_for('agents'))


@app.route('/deleteemailacc/<int:id>')
def deleteemailacc(id):
    emailacc = Emailaccount.query.get(id)
    db.session.delete(emailacc)
    db.session.commit()

    return redirect(url_for('emailaccs'))


@app.route('/deleterentprop/<int:id>')
def deleterentprop(id):
    delete_rent = Rent.query.get(id)
    delete_property = Property.query.filter(Property.rent_id == id).first()
    if delete_property:
        db.session.delete(delete_property)
    db.session.delete(delete_rent)
    db.session.commit()

    return redirect(url_for('index'))


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


@app.route('/editrentprop/<int:id>', methods=["POST", "GET"])
@login_required
def editrentprop(id):
    if request.method == "POST":
        postrentprop(id, "edit")

        return redirect('/editrentprop/{}'.format(id))
    else:
        rentprop, actypedets, advarrdets, deedcodes, freqdets, landlords, mailtodets, proptypedets, salegradedets, \
        statusdets, tenuredets = getrentpropvalues(id, action="edit")
        # totcharges = Rent.query.join(Charge).with_entities(func.sum(Charge.chargebalance).label("totcharges")). \
        #     filter(Rent.id == id) \
        #         .one_or_none()

    return render_template('rentproppage.html', action="edit", title='Edit rent', rentprop=rentprop, actypedets=actypedets,
                           advarrdets=advarrdets, deedcodes=deedcodes, freqdets=freqdets, landlords=landlords,
                           mailtodets=mailtodets, proptypedets=proptypedets, salegradedets=salegradedets,
                           statusdets=statusdets, tenuredets=tenuredets)


@app.route('/emailaccpage/<int:id>', methods=["POST", "GET"])
@login_required
def emailaccpage(id):
    if request.method == "POST":
        emailacc = postemailacc(id, action="edit")
        db.session.add(emailacc)
        db.session.commit()

        return redirect('/emailaccpage/{}'.format(id))

    else:
        ide = id
        managers = [value for (value,) in Manager.query.with_entities(Manager.name).all()]
        emailaccs = [value for (value,) in Emailaccount.query.with_entities(Emailaccount.smtp_server).all()]
        bankaccs = [value for (value,) in Typebankacc.query.with_entities(Typebankacc.accnum).all()]
        emailacc = \
            Emailaccount.query \
                .with_entities(Emailaccount.id, Emailaccount.smtp_server, Emailaccount.smtp_port,
                               Emailaccount.smtp_timeout, Emailaccount.smtp_debug, Emailaccount.smtp_tls,
                               Emailaccount.smtp_user, Emailaccount.smtp_password, Emailaccount.smtp_sendfrom,
                               Emailaccount.imap_server, Emailaccount.imap_port, Emailaccount.imap_tls,
                               Emailaccount.imap_user, Emailaccount.imap_password, Emailaccount.imap_sentfolder,
                               Emailaccount.imap_draftfolder) \
                .filter(Emailaccount.id == ide) \
                .one_or_none()

    return render_template('emailaccpage.html', title='Email account', emailacc=emailacc)


@app.route('/emailaccs', methods=['GET'])
def emailaccs():
    emailaccs = \
        Emailaccount.query \
            .with_entities(Emailaccount.id, Emailaccount.smtp_server, Emailaccount.smtp_user,
                           Emailaccount.smtp_sendfrom, Emailaccount.imap_sentfolder, Emailaccount.imap_draftfolder) \
            .all()

    return render_template('emailaccs.html', title='Email accounts', emailaccs=emailaccs)


@app.route('/externalrent', methods=['GET', 'POST'])
@login_required
def externalrent():
    if request.method == "POST":
        rcd = request.form["rentcode"]
        ten = request.form["tenantname"]
        pop = request.form["propaddr"]
    else:
        rcd = "lus"
        ten = ""
        pop = ""
    rent = \
        Extrent.query \
            .join(Extmanager) \
            .with_entities(Extrent.id, Extrent.rentcode, Extrent.propaddr, Extrent.tenantname, Extrent.owner,
                           Extrent.rentpa, Extrent.arrears, Extrent.lastrentdate, Extrent.source, Extrent.status,
                           Extmanager.codename, Extrent.agentdetails) \
            .filter(Extrent.rentcode.startswith([rcd]),
                    Extrent.tenantname.ilike('%{}%'.format(ten)),
                    Extrent.propaddr.ilike('%{}%'.format(pop))) \
            .all()
    return render_template('externalrent.html', title='External Rents', rent=rent)


@app.route('/extrentpage/<int:id>', methods=["GET"])
@login_required
def extrentpage(id):
    # if request.method == "POST":
    #
    #     return redirect(url_for('index'))
    # else:
    rent = \
        Extrent.query \
            .join(Extmanager) \
            .with_entities(Extrent.rentcode, Extrent.propaddr, Extrent.tenantname, Extrent.owner,
                           Extrent.rentpa, Extrent.arrears, Extrent.lastrentdate, Extrent.source,
                           Extmanager.codename, Extrent.agentdetails) \
            .filter(Extrent.id == id) \
                .one_or_none()
    if rent is None:
        flash('N')
        return redirect(url_for('index'))

    return render_template('extrentpage.html', title ='External Rent', rent=rent)


def filteragents(agd, age, agn):
    agents = \
        Agent.query \
            .with_entities(Agent.id, Agent.agdetails, Agent.agemail, Agent.agnotes) \
            .filter(Agent.agdetails.ilike('%{}%'.format(agd)), \
                    Agent.agemail.ilike('%{}%'.format(age)), \
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


def filterrentprops(rcd, ten, pop):
    rentprops = \
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

    return rentprops


def getrentpropvalues(id, action):
    if action == "clone" or action == "edit":
        rentprop = \
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
        if rentprop is None:
            flash('Invalid rent code')
            return redirect(url_for('login'))
    elif action == "new":
        rentprop = None
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

    return rentprop, actypedets, advarrdets, deedcodes, freqdets, landlords, mailtodets, proptypedets, \
           salegradedets, statusdets, tenuredets


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

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        rcd = request.form["rentcode"]
        ten = request.form["tenantname"]
        pop = request.form["propaddr"]
        rentprops = filterrentprops(rcd, ten, pop)
    else:
        rcd = "ZWEF"
        rentprops = filterrentprops(rcd, "", "")
    return render_template('index.html', title='Rent and property search page', rentprops=rentprops)


@app.route('/landlordpage/<int:id>', methods=["POST", "GET"])
@login_required
def landlordpage(id):
    if request.method == "POST":
        landlord = Landlord.query.get(id)
        landlord.name = request.form["name"]
        landlord.addr = request.form["address"]
        landlord.taxdate = request.form["taxdate"]
        emailacc = request.form["emailacc"]
        landlord.emailacc_id = \
            Emailaccount.query.with_entities(Emailaccount.id).filter \
                (Emailaccount.smtp_server == emailacc).one()[0]
        bankacc = request.form["bankacc"]
        landlord.bankacc_id = \
                Typebankacc.query.with_entities(Typebankacc.id).filter \
                    (Typebankacc.accnum == bankacc).one()[0]
        manager = request.form["manager"]
        landlord.manager_id = \
            Manager.query.with_entities(Manager.id).filter \
                (Manager.name == manager).one()[0]
        db.session.commit()

        return redirect(url_for('landlords'))

    else:
        idl = id
        managers = [value for (value,) in Manager.query.with_entities(Manager.name).all()]
        emailaccs = [value for (value,) in Emailaccount.query.with_entities(Emailaccount.smtp_server).all()]
        bankaccs = [value for (value,) in Typebankacc.query.with_entities(Typebankacc.accnum).all()]
        landlord = \
            Landlord.query.join(Manager).join(Emailaccount).join(Typebankacc) \
                .with_entities(Landlord.name, Landlord.addr, Landlord.taxdate, Manager.name.label("manager"),
                               Emailaccount.smtp_server, Typebankacc.accnum) \
                .filter(Landlord.id == idl) \
                .one_or_none()

    return render_template('landlordpage.html', title='Landlord', landlord=landlord, bankaccs=bankaccs,
                           managers=managers, emailaccs=emailaccs)


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


@app.route('/newemailacc', methods=['GET', 'POST'])
def newemailacc():
    id = 0
    if request.method == "POST":
        emailacc = postemailacc(id, action="new")
        db.session.add(emailacc)
        db.session.commit()
        new_id = emailacc.id

        return redirect('/emailaccpage/{}'.format(new_id))

    else:
        emailacc = []

        return render_template('emailaccpage.html', title='New rent', emailacc=emailacc)


@app.route('/newrentprop', methods=['GET', 'POST'])
def newrentprop():
    id = 0
    if request.method == "POST":
        rent, property, agent = postrentprop(id, action="new")
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

        return redirect('/editrentprop/{}'.format(new_id))
    else:
        rentprop, actypedets, advarrdets, deedcodes, freqdets, landlords, mailtodets, proptypedets, salegradedets, \
        statusdets, tenuredets = getrentpropvalues(id, action="new")

    return render_template('newrent.html', title='New rent', actypedets=actypedets, advarrdets=advarrdets,
                           deedcodes=deedcodes, freqdets=freqdets, landlords=landlords, mailtodets=mailtodets,
                           proptypedets=proptypedets, salegradedets=salegradedets, statusdets=statusdets,
                           tenuredets=tenuredets)


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


def postemailacc(id, action):
    if action == "edit":
        emailacc = Emailaccount.query.get(id)
    else:
        emailacc = Emailaccount()
    emailacc.smtp_server = request.form["smtp_server"]
    emailacc.smtp_port = request.form["smtp_port"]
    emailacc.smtp_timeout = request.form["smtp_timeout"]
    emailacc.smtp_debug = request.form["smtp_debug"]
    emailacc.smtp_tls = request.form["smtp_tls"]
    emailacc.smtp_user = request.form["smtp_user"]
    emailacc.smtp_password = request.form["smtp_password"]
    emailacc.smtp_sendfrom = request.form["smtp_sendfrom"]
    emailacc.imap_port = request.form["imap_port"]
    emailacc.imap_tls = request.form["imap_tls"]
    emailacc.imap_user = request.form["imap_user"]
    emailacc.imap_password = request.form["imap_password"]
    emailacc.imap_sentfolder = request.form["imap_sentfolder"]
    emailacc.imap_draftfolder = request.form["imap_draftfolder"]

    return emailacc


def postrentprop(id, action):
    if action == "edit":
        rent = Rent.query.get(id)
        property = Property.query.filter(Property.rent_id == id).first()
        agent = Agent.query.filter(Agent.id == rent.agent_id).one_or_none()
    else:
        rent = Rent()
        property = Property()

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

    agdetails = request.form["agent"]
    if agdetails and agdetails != "None":
        if not agent:
            agent = Agent()
            agent.agdetails = agdetails
            agent.rent_agent.append(rent)
            db.session.add(agent)
        else:
            agent.agdetails = agdetails
    property.propaddr = request.form["propaddr"]
    proptype = request.form["proptype"]
    property.typeprop_id = \
        Typeproperty.query.with_entities(Typeproperty.id).filter(Typeproperty.proptypedet == proptype).one()[0]

    # lots of challenges: I have allowed for editing an existing agent, but not switching to another or new agent
    # I have not dealt with case where someone simply deletes all existing agentdetails
    db.session.commit()


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


@app.route('/rentproppage/<int:id>', methods=["GET"])
@login_required
def rentproppage(id):
    rentprop, actypedets, advarrdets, deedcodes, freqdets, landlords, mailtodets, proptypedets, salegradedets, \
    statusdets, tenuredets = getrentpropvalues(id, action="edit")
    # totcharges = Rent.query.join(Charge).with_entities(func.sum(Charge.chargebalance).label("totcharges")). \
    #     filter(Rent.id == id) \
    #         .one_or_none()

    return render_template('rentproppage.html', action="view", title='View rent', rentprop=rentprop, actypedets=actypedets,
                           advarrdets=advarrdets, deedcodes=deedcodes, freqdets=freqdets, landlords=landlords,
                           mailtodets=mailtodets, proptypedets=proptypedets, salegradedets=salegradedets,
                           statusdets=statusdets, tenuredets=tenuredets)


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
