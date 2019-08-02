#from datetime import datetime
import datetime
from dateutil.relativedelta import relativedelta
from app import app, db
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from sqlalchemy import desc, func, literal, and_, or_
from app.forms import EditProfileForm, LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, ResetPasswordForm, JinnForm, RentForm
from app.email import send_password_reset_email
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
        charges = []
        charges = Charge.query.join(Rent).join(Chargetype).with_entities(Charge.id, Rent.rentcode, \
                  Chargetype.chargedesc, Charge.chargestartdate, Charge.chargetotal, Charge.chargedetails, \
                  Charge.chargebalance).filter(Rent.rentcode.startswith([rcd]), \
                  Charge.chargedetails.ilike ('%{}%'.format(cdt))).all()
    else:
        idr = id
        print ("idr", idr)
        charges = []
        charges = Charge.query.join(Rent).join(Chargetype).with_entities(Charge.id, Rent.rentcode, \
                  Chargetype.chargedesc, Charge.chargestartdate, Charge.chargetotal, Charge.chargedetails, \
                  Charge.chargebalance).filter(Rent.id==('{}'.format(idr))).all()
        print (charges)
    return render_template('chargepage.html', title='Charges', charges=charges)


@app.route('/clonerent/<int:id>', methods=["POST", "GET"])
@login_required
def clonerent(id):
    if request.method == "POST":
        thisrent = Rent.query.get(id)
        thisrent.tenantname = request.form["tenantname"]
        thisrent.source = request.form["source"]
        thisrent.note = request.form["note"]
        thisrent.email = request.form["email"]
        thisrent.rentpa = request.form["rentpa"]
        thisrent.lastrentdate = request.form["lastrentdate"]
        thisprop = Property.query.filter(Property.rent_id == id).first()
        thisprop.propaddr = request.form["propaddr"]
        thisagent = Agent.query.filter(Agent.id == thisrent.agent_id).first()
        if thisagent is not None:
            thisagent.agdetails = request.form["agent"]
        db.session.commit()
        return redirect('/editrent/{}'.format(id))
    else:
        rentdet = Property.query.join(Rent).join(Landlord).outerjoin(Agent).join(Typeactype).join(Typeadvarr).join(Typedeed).\
                  join(Typemailto).join(Typesalegrade).join(Typestatus).join(Typetenure).with_entities(Rent.id, \
                   Rent.rentcode, Rent.tenantname, Rent.rentpa, Rent.arrears, Rent.lastrentdate, Rent.frequency, \
                   Rent.datecode, Rent.source, Rent.price, Rent.note, Rent.email, Property.propaddr, Landlord.name, \
                   Agent.agdetails, Typeactype.actypedet, Typeadvarr.advarrdet, Typedeed.deedcode, Typemailto.mailtodet, \
                   Typesalegrade.salegradedet, Typestatus.statusdet, Typetenure.tenuredet).filter(Rent.id==('{}'.format(id))).first()
        print (rentdet)
        if rentdet is None:
            flash('Invalid rent code')
            return redirect(url_for('login'))
    return render_template('clonerent.html', rent=rentdet)


@app.route('/editcharge/<int:id>', methods=["POST", "GET"])
@login_required
def editcharge(id):
    if request.method == "POST":
        thischarge = Charge.query.get(id)
        thischarge.chargetype_id = Chargetype.query.with_entities(Chargetype.id).filter(Chargetype.chargedesc == request.form["chargedesc"]).first()[0]
        thischarge.chargestartdate = request.form["chargestartdate"]
        thischarge.chargetotal = request.form["chargetotal"]
        thischarge.chargedetails = request.form["chargedetails"]
        thischarge.chargebalance = request.form["chargebalance"]
        db.session.commit()
        return redirect('/editcharge/{}'.format(id))
    else:
        chargedet = Charge.query.join(Rent).join(Chargetype).with_entities(Charge.id, Rent.rentcode, \
                   Charge.chargetype_id, Chargetype.chargedesc, Charge.chargestartdate, Charge.chargetotal, \
                   Charge.chargedetails, Charge.chargebalance).filter(Charge.id==('{}'.format(id))).first()
        if chargedet is None:
            flash('N')
            return redirect(url_for('login'))
        chargedescs = Chargetype.query.with_entities(Chargetype.chargedesc).all()
        chargedescs = [value for (value,) in chargedescs]

    return render_template('editcharge.html', chargedescs=chargedescs, charge=chargedet)


@app.route('/edit_profile', methods=['GET', 'POST'])
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
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

                           
@app.route('/editrent/<int:id>', methods=["POST", "GET"])
@login_required
def editrent(id):
    if request.method == "POST":
        thisrent = Rent.query.get(id)
        thislandlord = request.form["landlord"]
        thisrent.landlord_id = Landlord.query.with_entities(Landlord.id).filter(Landlord.name == thislandlord).first()[0]
        thisrent.tenantname = request.form["tenantname"]
        thisrent.source = request.form["source"]
        thisrent.note = request.form["note"]
        thisrent.email = request.form["email"]
        thismailto = request.form["mailto"]
        thisrent.mailto_id = Typemailto.query.with_entities(Typemailto.id).filter(Typemailto.mailtodet == thismailto).first()[0]
        thisagent = Agent.query.filter(Agent.id == thisrent.agent_id).first()
        thisrent.rentpa = request.form["rentpa"]
        thisrent.arrears = request.form["arrears"]
        thisfrequency = request.form["frequency"]
        thisrent.freq_id = Typefreq.query.with_entities(Typefreq.id).filter(Typefreq.freqdet == thisfrequency).first()[0]
        thisrent.lastrentdate = request.form["lastrentdate"]
        thisadvarr = request.form["advarr"]
        thisrent.advarr_id = Typeadvarr.query.with_entities(Typeadvarr.id).filter(Typeadvarr.advarrdet == thisadvarr).first()[0]
        thistenure = request.form["tenure"]
        thisrent.tenure_id = Typetenure.query.with_entities(Typetenure.id).filter(Typetenure.tenuredet == thistenure).first()[0]
        thisdeedtype = request.form["deedtype"]
        thisrent.deed_id = Typedeed.query.with_entities(Typedeed.id).filter(Typedeed.deedcode == thisdeedtype).first()[0]
        thissalegrade = request.form["salegrade"]
        thisrent.salegrade_id = Typesalegrade.query.with_entities(Typesalegrade.id).filter(Typesalegrade.salegradedet == thissalegrade).first()[0]
        thisstatus = request.form["status"]
        thisrent.status_id = Typestatus.query.with_entities(Typestatus.id).filter(Typestatus.statusdet == thisstatus).first()[0]
        thisprop = Property.query.filter(Property.rent_id == id).first()
        thisprop.propaddr = request.form["propaddr"]
        if thisagent is not None:
            thisagent.agdetails = request.form["agent"]
        db.session.commit()
        return redirect('/editrent/{}'.format(id))
    else:
        rentdet = Property.query.join(Rent).join(Landlord).outerjoin(Agent).join(Typeactype).join(Typeadvarr).join(Typedeed).\
                  join(Typemailto).join(Typesalegrade).join(Typestatus).join(Typetenure).join(Typefreq).with_entities(Rent.id, \
                   Rent.rentcode, Rent.tenantname, Rent.rentpa, Rent.arrears, Rent.lastrentdate, Typefreq.freqdet, \
                   Rent.datecode, Rent.source, Rent.price, Rent.note, Rent.email, Property.propaddr, Landlord.name, \
                   Agent.agdetails, Typeactype.actypedet, Typeadvarr.advarrdet, Typedeed.deedcode, Typemailto.mailtodet, \
                   Typesalegrade.salegradedet, Typestatus.statusdet, Typetenure.tenuredet).filter(Rent.id==('{}'.format(id))).first()
        print (rentdet)
        landlords = Landlord.query.with_entities(Landlord.name).all()
        landlords = [value for (value,) in landlords]
        mailtos = Typemailto.query.with_entities(Typemailto.mailtodet).all()
        mailtos = [value for (value,) in mailtos]
        freqdets = Typefreq.query.with_entities(Typefreq.freqdet).all()
        freqdets = [value for (value,) in freqdets]
        advarrdets = Typeadvarr.query.with_entities(Typeadvarr.advarrdet).all()
        advarrdets = [value for (value,) in advarrdets]
        tenuredets = Typetenure.query.with_entities(Typetenure.tenuredet).all()
        tenuredets = [value for (value,) in tenuredets]
        deedcodes = Typedeed.query.with_entities(Typedeed.deedcode).all()
        deedcodes = [value for (value,) in deedcodes]
        salegradedets = Typesalegrade.query.with_entities(Typesalegrade.salegradedet).all()
        salegradedets = [value for (value,) in salegradedets]
        statusdets = Typestatus.query.with_entities(Typestatus.statusdet).all()
        statusdets = [value for (value,) in statusdets]
        if rentdet is None:
            flash('Invalid rent code')
            return redirect(url_for('login'))
    return render_template('editrent.html', rent=rentdet, landlords=landlords, mailtos=mailtos, freqdets=freqdets, \
            advarrdets=advarrdets, tenuredets=tenuredets, deedcodes=deedcodes, salegradedets=salegradedets, statusdets=statusdets)


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
    rents = Extrent.query.join(Extmanager).with_entities(Extrent.id, Extrent.rentcode, Extrent.propaddr, \
            Extrent.owner, Extrent.tenantname, Extrent.rentpa, Extrent.arrears, Extrent.lastrentdate, \
            Extmanager.codename).filter(Extrent.rentcode.startswith([rcd]), \
            Extrent.propaddr.ilike ('%{}%'.format(pop))).all()
    return render_template('externalrent.html', title='ExternalRents', rents=rents)

    
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == "POST":
        rcd = request.form["rentcode"]
        ten = request.form["tenantname"]
        pop = request.form["propaddr"]
        rents = []
        rents = Property.query.join(Rent).join(Landlord).outerjoin(Agent).with_entities(Rent.id, Rent.rentcode, \
               Rent.tenantname, Rent.rentpa, Rent.arrears, Rent.lastrentdate, \
               Property.propaddr, Landlord.name, Agent.agdetails).filter(Rent.rentcode.startswith([rcd]), \
               Rent.tenantname.ilike ('%{}%'.format(ten)), \
               Property.propaddr.ilike ('%{}%'.format(pop))).all()
        print ("rents are:", rents)
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
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

    
@app.route('/newrent', methods=['GET', 'POST'])
def newrent():
    if request.method == "POST":
        rentcode = request.form["tenantname"]
        tenantname = request.form["tenantname"]
        rentpa = request.form["rentpa"]
        source = request.form["source"]
        note = request.form["note"]
        email = request.form["email"]
        lastrentdate = request.form["lastrentdate"]
        mailto = request.form["mailto"]
        mailto_id = Typemailto.query.with_entities(Typemailto.id).filter(Typemailto.mailtodet == mailto).first()[0]
        arrears = request.form["arrears"]
        frequency = request.form["frequency"]
        freq_id = Typefreq.query.with_entities(Typefreq.id).filter(Typefreq.freqdet == frequency).first()[0]
        advarr = request.form["advarr"]
        advarr_id = Typeadvarr.query.with_entities(Typeadvarr.id).filter(Typeadvarr.advarrdet == advarr).first()[0]
        tenure = request.form["tenure"]
        tenure_id = Typetenure.query.with_entities(Typetenure.id).filter(Typetenure.tenuredet == tenure).first()[0]
        deedtype = request.form["deedtype"]
        deed_id = Typedeed.query.with_entities(Typedeed.id).filter(Typedeed.deedcode == deedtype).first()[0]
        salegrade = request.form["salegrade"]
        salegrade_id = Typesalegrade.query.with_entities(Typesalegrade.id).filter(Typesalegrade.salegradedet == salegrade).first()[0]
        status = request.form["status"]
        status_id = Typestatus.query.with_entities(Typestatus.id).filter(Typestatus.statusdet == status).first()[0]
        newrent = Rent(0, rentcode, tenantname, rentpa, arrears, lastrentdate, datecode, \
            source, price, email, note, landlord_id, agent_id, actype, advarr_id, deed_id, \
            freq_id, mailto_id, salegrade_id, status_id, tenure_id) 
        propaddr = request.form["propaddr"]
        agent = request.form["agent"]
        if propaddr is not None and propaddr != "" and propaddr != "None":
            newprop = Fitstory(storydet=thisstory)
            newfit.story_fit.append(newstory)
            db.session.add(newfit)
            db.session.commit()
        return redirect('/index')
        if agent is not None:
            thisagent.agdetails = request.form["agent"]
        newfit.users.append(user)
        db.session.commit()
        return redirect('/editrent/{}'.format(id))
    else:
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
        salegradedets = Typesalegrade.query.with_entities(Typesalegrade.salegradedet).all()
        salegradedets = [value for (value,) in salegradedets]
        statusdets = Typestatus.query.with_entities(Typestatus.statusdet).all()
        statusdets = [value for (value,) in statusdets]
        tenuredets = Typetenure.query.with_entities(Typetenure.tenuredet).all()
        tenuredets = [value for (value,) in tenuredets]
        print (landlords)
        return render_template('newrent.html', title='New rent', actypedets=actypedets, advarrdets=advarrdets, \
            deedcodes=deedcodes, landlords=landlords, freqdets=freqdets, mailtodets=mailtodets, \
            salegradedets= salegradedets, statusdets=statusdets, tenuredets=tenuredets)


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
    return render_template('register.html', title='Register', form=form)


@app.route('/rentpage')
@login_required
def rentpage():
    rentid = 111
    rentdet = Property.query.join(Rent).join(Landlord).outerjoin(Agent).with_entities(Rent.id, Rent.rentcode, \
               Rent.tenantname, Rent.mailto_id, Rent.rentpa, Rent.arrears, Rent.advarr_id, \
               Rent.lastrentdate, Rent.frequency, Rent.datecode, Rent.actype_id, Rent.tenure_id, \
               Rent.source, Rent.deed_id, Rent.status_id, Rent.salegrade_id, Rent.price, Rent.note, \
               Rent.email, Property.propaddr, Landlord.name, Agent.agdetails).filter(Rent.id==('{}'.format(rentid))).first()
    if rentdet is None:
        flash('Invalid rent code')
        return redirect(url_for('login'))
    return render_template('rentpage.html', rents=rentdet)

    
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
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


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
    return render_template('reset_password.html', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    return render_template('user.html', user=user)
