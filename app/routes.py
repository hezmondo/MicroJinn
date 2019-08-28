from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse

from app import app, db
from app.email import send_password_reset_email
from app.forms import EditProfileForm, LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import User
from app.subroutes.sub import subagents, subagentp, subcharges, subchargep, subdeleteitem, subemailaccp, \
    subemailaccs, subextrentp, subextrents, subheadrents, subincome, subindex, sublandlordp, \
    sublandlords, submoney, subpayrequests, subproperties, subrentobjp


@app.route('/agents', methods=['GET', 'POST'])
def agents():
    agents = subagents()
    return render_template('agents.html', title='Agent search page', agents=agents)


@app.route('/agentpage/<int:id>', methods=["GET", "POST"])
@login_required
def agentpage(id):
    agent = subagentp(id)
    return render_template('agentpage.html', title='Agent', agent=agent)


@app.route('/charges', methods=['GET', 'POST'])
def charges():
    charges = subcharges()
    return render_template('charges.html', title='Charges page', charges=charges)


@app.route('/chargepage/<int:id>', methods=["GET", "POST"])
@login_required
def chargepage(id):
    charge, chargedescs = subchargep(id)
    return render_template('chargepage.html', charge=charge, chargedescs=chargedescs)


@app.route('/deleteitem/<int:id>')
@login_required
def deleteitem(id):
    subdeleteitem(id)
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


@app.route('/emailaccpage/<int:id>', methods=["POST", "GET"])
@login_required
def emailaccpage(id):
    emailacc = subemailaccp(id)
    return render_template('emailaccpage.html', title='Email account', emailacc=emailacc)


@app.route('/emailaccs', methods=['GET'])
def emailaccs():
    emailaccs = subemailaccs()
    return render_template('emailaccs.html', title='Email accounts', emailaccs=emailaccs)


@app.route('/externalrents', methods=['GET', 'POST'])
def externalrents():
    extrents = subextrents()
    return render_template('externalrents.html', title='External rents', extrents=extrents)


@app.route('/extrentpage/<int:id>', methods=["GET"])
@login_required
def extrentpage(id):
    extrent = subextrentp(id)
    return render_template('extrentpage.html', title ='External Rent', extrent=extrent)


@app.route('/headrents', methods=['GET', 'POST'])
def headrents():
    headrents = subheadrents()
    return render_template('headrents.html', title='Headrents', headrents=headrents)


@app.route('/income', methods=['GET', 'POST'])
def income():
    income = subincome()
    return render_template('income.html', title='Income', income=income)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    rentobjs = subindex()
    return render_template('index.html', title='Rent and property search page', rentobjs=rentobjs)


@app.route('/landlordpage/<int:id>', methods=["POST", "GET"])
@login_required
def landlordpage(id):
    landlord, managers, emailaccs, bankaccs = sublandlordp(id)
    return render_template('landlordpage.html', title='Landlord', landlord=landlord, bankaccs=bankaccs,
                               managers=managers, emailaccs=emailaccs)


@app.route('/landlords', methods=['GET'])
def landlords():
    landlords = sublandlords()
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
def money():
    money = submoney()
    return render_template('money.html', title='Money', money=money)


@app.route('/payrequests', methods=['GET', 'POST'])
@login_required
def payrequests():
    payrequests = subpayrequests()
    return render_template('payrequests.html', title='Payrequests', payrequests=payrequests)


@app.route('/properties', methods=['GET', 'POST'])
@login_required
def properties():
    properties = subproperties()
    return render_template('properties.html', title='Properties', properties=properties)


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


@app.route('/rentobjpage/<int:id>', methods=['GET', 'POST'])
@login_required
def rentobjpage(id):
        action, rentobj, actypedets, advarrdets, deedcodes, freqdets, landlords, mailtodets, \
        proptypedets, salegradedets, statusdets, tenuredets = subrentobjp(id)

        return render_template('rentobjpage.html', action=action, title=action, rentobj=rentobj,
                       actypedets=actypedets, advarrdets=advarrdets, deedcodes=deedcodes, freqdets=freqdets,
                       landlords=landlords, mailtodets=mailtodets, proptypedets=proptypedets,
                       salegradedets=salegradedets, statusdets=statusdets, tenuredets=tenuredets)


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


@app.route('/utilities', methods=['GET'])
def utilities():
    return render_template('utilities.html', title='utilities')
