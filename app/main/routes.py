from flask import render_template, redirect, url_for, request
from flask_login import login_required
from app import db
from app.main import bp
from app.main.get import filteragents, filtercharges, filteremailaccs, filterextrents, filterheadrents, \
    filterincome, filterlandlords, filterrentobjs, getagent, getcharge, getemailacc, \
    getextrent, getincome, getlandlord, getproperty, getrentobj
from app.main.post import postagent, postcharge, postemailacc, postincome, postlandlord, \
    postproperty, postrentobj


@bp.route('/agents', methods=['GET', 'POST'])
def agents():
    if request.method == "POST":
        agd = request.form["address"]
        age = request.form["email"]
        agn = request.form["notes"]
    else:
        agd = "Jones"
        age = ""
        agn = ""
    agents = filteragents(agd, age, agn)

    return render_template('agents.html', title='Agent search page', agents=agents)


@bp.route('/agentpage/<int:id>', methods=["GET", "POST"])
@login_required
def agentpage(id):
    if request.method == "POST":
        postagent(id)
    else:
        pass
    agent = getagent(id)

    return render_template('agentpage.html', title='Agent', agent=agent)


@bp.route('/charges', methods=['GET', 'POST'])
def charges():
    rentcode = request.args.get('rentcode', "view", type=str)
    if request.method == "POST":
        rcd = request.form["rentcode"]
        cdt = request.form["chargedetails"]
    else:
        if not rentcode == "view":
            rcd = rentcode
        else:
            rcd = ""
        cdt = ""
    charges = filtercharges(rcd, cdt)

    return render_template('charges.html', title='Charges page', charges=charges)


@bp.route('/chargepage/<int:id>', methods=["GET", "POST"])
@login_required
def chargepage(id):
    if request.method == "POST":
        postcharge(id)
    else:
        pass
    charge, chargedescs = getcharge(id)

    return render_template('chargepage.html', charge=charge, chargedescs=chargedescs)


@bp.route('/deleteitem/<int:id>')
@login_required
def deleteitem(id):
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

    return redirect(url_for('main.index'))


@bp.route('/emailaccpage/<int:id>', methods=["POST", "GET"])
@login_required
def emailaccpage(id):
    action = request.args.get('action', "view", type=str)
    if request.method == "POST":
        postemailacc(id, action)
    else:
        pass
    emailacc = getemailacc(id)

    return render_template('emailaccpage.html', title='Email account', action=action, emailacc=emailacc)


@bp.route('/emailaccs', methods=['GET'])
def emailaccs():
    emailaccs = filteremailaccs()

    return render_template('emailaccs.html', title='Email accounts', emailaccs=emailaccs)


@bp.route('/externalrents', methods=['GET', 'POST'])
def externalrents():
    extrents = filterextrents()

    return render_template('externalrents.html', title='External rents', extrents=extrents)


@bp.route('/extrentpage/<int:id>', methods=["GET"])
@login_required
def extrentpage(id):
    extrent = getextrent(id)

    return render_template('extrentpage.html', title ='External Rent', extrent=extrent)


@bp.route('/headrents', methods=['GET', 'POST'])
def headrents():
    headrents = filterheadrents()

    return render_template('headrents.html', title='Headrents', headrents=headrents)


@bp.route('/income', methods=['GET', 'POST'])
def income():
    if request.method == "POST":
        rcd = request.form["rentcode"]
        pay = request.form["payer"]
        typ = request.form["type"]
        income = filterincome(rcd, pay, typ)
    else:
        income = filterincome("", "", "")

    return render_template('income.html', title='Income', income=income)


@bp.route('/incomeallocpage/<int:id>', methods=["POST", "GET"])
@login_required
def incomeallocpage(id):
    action = request.args.get('action', "view", type=str)
    if request.method == "POST":
        postincome(id, action)
    else:
        pass
    bankaccs, chargedescs, income, incomeallocs, landlords = getincome(id)

    return render_template('incomeallocpage.html', title='Income allocation', action=action, bankaccs=bankaccs,
                           chargedescs=chargedescs, income=income, incomeallocs=incomeallocs, landlords=landlords
                           )


@bp.route('/incomepage/<int:id>', methods=["POST", "GET"])
@login_required
def incomepage(id):
    action = request.args.get('action', "view", type=str)
    if request.method == "POST":
        postincome(id, action)
    else:
        pass
    bankaccs, chargedescs, income, incomeallocs, landlords = getincome(id)

    return render_template('incomepage.html', title='Income', action=action, bankaccs=bankaccs,
                           chargedescs=chargedescs, income=income, incomeallocs=incomeallocs, landlords=landlords
                           )


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        rcd = request.form["rentcode"]
        ten = request.form["tenantname"]
        pop = request.form["propaddr"]
        rentobjs = filterrentobjs(rcd, ten, pop)
    else:
        rentobjs = filterrentobjs("ZWEF", "", "")

    return render_template('index.html', title='Rent and property search page', rentobjs=rentobjs)


@bp.route('/landlordpage/<int:id>', methods=["POST", "GET"])
@login_required
def landlordpage(id):
    action = request.args.get('action', "view", type=str)
    if request.method == "POST":
        postlandlord(id, action)
    else:
        pass
    landlord, managers, emailaccs, bankaccs = getlandlord(id)

    return render_template('landlordpage.html', title='Landlord', action=action, landlord=landlord,
                           bankaccs=bankaccs, managers=managers, emailaccs=emailaccs)


@bp.route('/landlords', methods=['GET'])
def landlords():
    landlords = filterlandlords()

    return render_template('landlords.html', title='Landlords', landlords=landlords)


@bp.route('/money', methods=['GET', 'POST'])
def money():
    money = None

    return render_template('money.html', title='Money', money=money)


@bp.route('/payrequests', methods=['GET', 'POST'])
@login_required
def payrequests():
    payrequests = None

    return render_template('payrequests.html', title='Payrequests', payrequests=payrequests)


@bp.route('/properties', methods=['GET', 'POST'])
@login_required
def properties():
    properties = None

    return render_template('properties.html', title='Properties', properties=properties)


@bp.route('/propertypage/<int:id>', methods=["GET", "POST"])
@login_required
def propertypage(id):
    if request.method == "POST":
        postproperty(id)
    else:
        pass
    property, proptypedets = getproperty(id)

    return render_template('propertypage.html', title='Property', property=property, proptypedets=proptypedets)


@bp.route('/rentobjpage/<int:id>', methods=['GET', 'POST'])
@login_required
def rentobjpage(id):
    action = request.args.get('action', "view", type=str)
    if request.method == "POST":
        postrentobj(id)
    else:
        pass
    rentobj, actypedets, advarrdets, deedcodes, freqdets, landlords, mailtodets, properties, \
            salegradedets, statusdets, tenuredets, totcharges = getrentobj(id)

    return render_template('rentobjpage.html', action=action, title=action, rentobj=rentobj,
                       actypedets=actypedets, advarrdets=advarrdets, deedcodes=deedcodes, freqdets=freqdets,
                       landlords=landlords, mailtodets=mailtodets, properties=properties,
                       salegradedets=salegradedets, statusdets=statusdets, tenuredets=tenuredets, totcharges=totcharges)


@bp.route('/utilities', methods=['GET'])
def utilities():

    return render_template('utilities.html', title='utilities')