import sqlalchemy
import datetime
from flask import render_template, redirect, url_for, request, session, jsonify
from flask_login import login_required
from app import db
from app.main import bp
from app.main.get import get_agent, get_agents, get_charge, get_charges, get_docfile, get_docfiles, \
    get_emailaccount, get_emailaccounts, get_externalrent, get_formletter, get_formletters, get_headrents, \
    get_incomeobject, get_incomepost, get_incomeitems, get_incomeoptions, get_incomeobjectoptions, get_landlord, \
    get_landlords, get_lease, get_loan, get_loan_options, get_loans, \
    get_loanstatement, get_moneyaccount, get_moneydets, get_moneyitem, get_moneyitems, get_money_options, \
    get_property, get_rental, getrentals, get_rentalstatement, getrentobj_combos, getrentobj_main, \
    get_rentobjects_advanced, get_rentobjects_basic
from app.main.delete import delete_record
from app.main.post import post_agent, post_charge, post_emailaccount, post_incomeobject, post_landlord, post_formletter, \
    post_docfile, post_lease, post_loan, post_moneyaccount, post_moneyitem, post_property, post_rental, postrentobj
from app.main.writemail import writeMail
from app.main.functions import backup_database, dateToStr, strToDate
from app.models import Agent, Charge, Formletter, Docfile, Emailaccount, Income, Incomealloc, Jstore, Landlord, Loan, \
    Money_account, Money_category, Money_item, Loan_interest_rate, Loan_trans, Property, Rent, Rental, \
    Template, Typedoc, Typemailto


@bp.route('/agents', methods=['GET', 'POST'])
def agents():
    agents = get_agents()

    return render_template('agents.html', agents=agents)


@bp.route('/agent/<int:id>', methods=["GET", "POST"])
@login_required
def agent(id):
    action = request.args.get('action', "view", type=str)
    if request.method == "POST":
        id = post_agent(id, action)
        action = "view"
    agent = get_agent(id)

    return render_template('agent.html', action=action, agent=agent)


@bp.route('/backup', methods=['GET', 'POST'])
# @login_required
def backup():
    if request.method == "POST":
        backup_database()

    return render_template('backup.html')


@bp.route('/charges', methods=['GET', 'POST'])
def charges():
    rentid = request.args.get('rentid', "", type=str)
    charges = get_charges(rentid)

    return render_template('charges.html', charges=charges)


@bp.route('/charge/<int:id>', methods=["GET", "POST"])
@login_required
def charge(id):
    action = request.args.get('action', "view", type=str)
    if request.method == "POST":
        id = post_charge(id, action)
    charge, chargedescs = get_charge(id)

    return render_template('charge.html', action=action, charge=charge, chargedescs=chargedescs)


@bp.route('/delete_item/<int:id>')
@login_required
def delete_item(id):
    item = request.args.get('item', "view", type=str)
    delete_record(id, item)


@bp.route('/docfile/<int:id>', methods=['GET', 'POST'])
@login_required
def docfile(id):
    # incoming id is docfile id for existing docfile and rent id for new docfile! -see guide
    action = request.args.get('action', "view", type=str)
    if request.method == "POST":
        id_ = post_docfile(id)
        return redirect('/docfile/{}?action=view'.format(id_))

    docfile, dfoutin = get_docfile(id, action)
    # this id is docfile id for existing docfile and rent id for new docfile!

    return render_template('docfile.html', action=action, docfile=docfile, dfoutin=dfoutin)


@bp.route('/docfiles/<int:rentid>', methods=['GET', 'POST'])
def docfiles(rentid):
    docfiles, dfoutin = get_docfiles(rentid)
    outins = ["all", "out", "in"]

    return render_template('docfiles.html', rentid=rentid, dfoutin=dfoutin, docfiles=docfiles, outins=outins)


@bp.route('/email_accounts', methods=['GET'])
def email_accounts():
    emailaccs = get_emailaccounts()

    return render_template('email_accounts.html', emailaccs=emailaccs)


@bp.route('/email_account/<int:id>', methods=['GET', 'POST'])
@login_required
def email_account(id):
    action = request.args.get('action', "view", type=str)
    if request.method == "POST":
        id = post_emailaccount(id, action)
    emailacc = get_emailaccount(id)

    return render_template('email_account.html', action=action, emailacc=emailacc)


@bp.route('/external_rents', methods=['GET', 'POST'])
def external_rents():
    agentdetails, propaddr, rentcode, source, tenantname, rentprops = get_rentobjects_basic("external")

    return render_template('external_rents.html', agentdetails=agentdetails, propaddr=propaddr, rentcode=rentcode,
                           source=source, tenantname=tenantname, rentprops=rentprops)


@bp.route('/external_rent/<int:id>', methods=["GET"])
@login_required
def external_rent(id):
    externalrent = get_externalrent(id)

    return render_template('external_rent.html', externalrent=externalrent)


@bp.route('/formletter/<int:id>', methods=['GET', 'POST'])
@login_required
def formletter(id):
    action = request.args.get('action', "view", type=str)
    if request.method == "POST":
        id_ = post_formletter(id, action)
        return redirect('/formletter/{}?action=view'.format(id_))
    formletter = get_formletter(id)
    templates = [value for (value,) in Template.query.with_entities(Template.code).all()]

    return render_template('formletter.html', action=action, formletter=formletter, templates=templates)


@bp.route('/formletters', methods=['GET'])
def formletters():
    formletters = get_formletters("normal")

    return render_template('formletters.html', formletters=formletters)


@bp.route('/headrents', methods=['GET', 'POST'])
def headrents():
    headrents, statuses = get_headrents()

    return render_template('headrents.html', headrents=headrents, statuses=statuses)


@bp.route('/income', methods=['GET', 'POST'])
def income():
    incomeitems = get_incomeitems()
    bankaccs, paytypes = get_incomeoptions()

    return render_template('income.html', bankaccs=bankaccs, paytypes=paytypes, incomeitems=incomeitems)


@bp.route('/income_object/<int:id>', methods=['GET', 'POST'])
@login_required
def income_object(id):
    action = request.args.get('action', "view", type=str)
    if request.method == "POST":
        id = post_incomeobject(id, action)

    bankaccs, chargedescs, landlords, paytypes = get_incomeobjectoptions()
    income, incomeallocs = get_incomeobject(id)

    return render_template('income_object.html', action=action, bankaccs=bankaccs, chargedescs=chargedescs,
                           income=income, incomeallocs=incomeallocs, landlords=landlords, paytypes=paytypes)


@bp.route('/income_post/<int:id>', methods=['GET', 'POST'])
@login_required
def income_post(id):
    if request.method == "POST":
        post_incomeobject(id, "new")

    bankaccs, chargedescs, landlords, paytypes = get_incomeobjectoptions()
    allocs, post, post_tot, today = get_incomepost(id)

    return render_template('income_post.html', allocs=allocs, bankaccs=bankaccs, chargedescs=chargedescs,
                           paytypes=paytypes, post=post, post_tot=post_tot, today=today)


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index/', methods=['GET', 'POST'])
@login_required
def index():
    session['doc_types'] = [value for (value,) in Typedoc.query.with_entities(Typedoc.desc).all()]
    action = request.args.get('action', "view", type=str)
    agentdetails, propaddr, rentcode, source, tenantname, rentprops = get_rentobjects_basic(action)


    return render_template('home.html', agentdetails=agentdetails, propaddr=propaddr,
                           rentcode=rentcode, source=source, tenantname=tenantname, rentprops=rentprops)


@bp.route('/landlords', methods=['GET'])
def landlords():
    landlords = get_landlords()

    return render_template('landlords.html', landlords=landlords)


@bp.route('/landlord/<int:id>', methods=['GET', 'POST'])
@login_required
def landlord(id):
    action = request.args.get('action', "view", type=str)
    if request.method == "POST":
        id_ = post_landlord(id, action)

        return redirect('/landlord/{}?action=view'.format(id_))

    landlord, managers, emailaccs, bankaccs = get_landlord(id)

    return render_template('landlord.html', action=action, landlord=landlord, bankaccs=bankaccs,
                           managers=managers, emailaccs=emailaccs)


@bp.route('/lease/<int:id>', methods=['GET', 'POST'])
@login_required
def lease(id):
    action = request.args.get('action', "view", type=str)
    if request.method == "POST":
        id_ = post_lease(id, action)

        return redirect('/lease/{}?action=view'.format(id_))

    lease, uplift_types = get_lease(id)

    return render_template('lease.html', action=action, lease=lease, uplift_types=uplift_types)


@bp.route('/load_query', methods=['GET', 'POST'])
def load_query():
    if request.method == "POST":
        jqname = request.form["jqname"]

        return redirect("/queries/?name={}".format(jqname))

    jqueries = [value for (value,) in Jstore.query.with_entities(Jstore.name).all()]

    return render_template('load_query.html', jqueries=jqueries)


@bp.route('/loan/<int:id>', methods=['GET', 'POST'])
@login_required
def loan(id):
    action = request.args.get('action', "view", type=str)
    if request.method == "POST":
        id = post_loan(id, action)

    loan = get_loan(id)
    advarrdets, freqdets = get_loan_options()

    return render_template('loan.html', action=action, loan=loan, advarrdets=advarrdets, freqdets=freqdets)


@bp.route('/loans', methods=['GET', 'POST'])
def loans():
    loans, loansum = get_loans()

    return render_template('loans.html', loans=loans, loansum=loansum)


@bp.route('/loanstat_dialog/<int:id>', methods=["GET", "POST"])
def loanstat_dialog(id):

    return render_template('loanstat_dialog.html', loanid = id, today = datetime.date.today())


@bp.route('/loan_statement/<int:id>', methods=["GET", "POST"])
@login_required
def loan_statement(id):
    if request.method == "POST":
        stat_date = request.form["statdate"]
        rproxy = db.session.execute(sqlalchemy.text("CALL pop_loan_statement(:x, :y)"), params={"x": id, "y": stat_date})
        checksums = rproxy.fetchall()
        db.session.commit()
        loanstatement = get_loanstatement()
        loan = Loan.query.get(id)
        loancode = loan.code

        return render_template('loan_statement.html', loanstatement=loanstatement, loancode=loancode,
                               checksums=checksums)


@bp.route('/mail_dialog/<int:id>', methods=["GET", "POST"])
@login_required
def mail_dialog(id):
    action = request.args.get('action', "normal", type=str)
    formletters = get_formletters(action)

    return render_template('mail_dialog.html', action=action, formletters=formletters, rent_id = id)


@bp.route('/mail_edit/<int:id>', methods=["GET", "POST"])
@login_required
def mail_edit(id):
    action = request.args.get('action', "normal", type=str)
    method = request.args.get('method', "email", type=str)
    if request.method == "POST":
        mailaddr = request.form['mailaddr']
        mailaddr = mailaddr.split(", ")
        print(request.form)
        formletter_id = id
        rent_id = request.form['rent_id']
        subject, part1, block, bold, rentobj, formletter, addressdata, leasedata = writeMail(rent_id, 0, formletter_id, action)

        return render_template('mergedocs/LTS.html', action=action, subject=subject, part1=part1, block=block,
                                   bold=bold, rentobj=rentobj, formletter=formletter, addressdata=addressdata,
                                   leasedata=leasedata, mailaddr=mailaddr, method=method)


@bp.route('/money', methods=['GET', 'POST'])
def money():
    moneydets, accsums = get_moneydets()

    return render_template('money.html', moneydets=moneydets, accsums=accsums)


@bp.route('/money_account/<int:id>', methods=['GET', 'POST'])
@login_required
def money_account(id):
    action = request.args.get('action', "view", type=str)
    if request.method == "POST":
        id_ = post_moneyaccount(id, action)
        return redirect('/money_account/{}?action=view'.format(id_))
    moneyacc = get_moneyaccount(id)

    return render_template('money_account.html', action=action, moneyacc=moneyacc)


@bp.route('/money_deduce/<int:id>', methods=['GET', 'POST'])
def money_deduce(id):
    action = request.args.get('action', "view", type=str)
    if action == "X":
        return redirect('/income_object/{}'.format(id))
    else:
        return redirect('/money_item/{}'.format(id))


@bp.route('/money_items/<int:id>', methods=["GET", "POST"])
@login_required
def money_items(id):
    action = request.args.get('action', "account", type=str)
    bankaccs, cats, cleareds = get_money_options()
    accsums, moneyitems, values = get_moneyitems(id, action)

    return render_template('money_items.html', action=action, moneyitems=moneyitems, values=values,
                           bankaccs=bankaccs, accsums=accsums, cats=cats, cleareds=cleareds)


@bp.route('/money_item/<int:id>', methods=['GET', 'POST'])
def money_item(id):
    action = request.args.get('action', "view", type=str)
    if request.method == "POST":
        id_ = post_moneyitem(id, action)
        return redirect('/money_item/{}?action=view'.format(id_))

    bankaccs, cats, cleareds = get_money_options()
    moneyitem = get_moneyitem(id)

    return render_template('money_item.html', action=action, moneyitem=moneyitem, bankaccs=bankaccs,
                           cats=cats, cleareds=cleareds)


@bp.route('/payrequests', methods=['GET', 'POST'])
@login_required
def payrequests():
    payrequests = None

    return render_template('payrequests.html', payrequests=payrequests)


@bp.route('/properties', methods=['GET', 'POST'])
# @login_required
def properties():
    properties = None

    return render_template('properties.html', properties=properties)


@bp.route('/property/<int:id>', methods=["GET", "POST"])
# @login_required
def property(id):
    action = request.args.get('action', "view", type=str)
    if request.method == "POST":
        id = post_property(id, action)

    property, proptypedets = get_property(id)

    return render_template('property.html', action=action, property=property, proptypedets=proptypedets)


@bp.route('/queries/', methods=['GET', 'POST'])
def queries():
    action = request.args.get('action', "view", type=str)
    name = request.args.get('name', "queryall", type=str)
    actypes, floads, landlords, options, prdeliveries, salegrades, statuses, tenures, \
    actype, agentdetails, arrears, enddate, jname, landlord, prdelivery, propaddr, rentcode, rentpa, rentperiods, \
    runsize, salegrade, source, status, tenantname, tenure, rentprops = get_rentobjects_advanced(action, name)

    return render_template('queries.html', action=action, actypes=actypes, floads=floads,
                           landlords=landlords, options=options, prdeliveries=prdeliveries, salegrades=salegrades,
                           statuses=statuses, tenures=tenures, actype=actype, agentdetails=agentdetails,
                           arrears=arrears, enddate=enddate, jname=jname, landlord=landlord, prdelivery=prdelivery,
                           propaddr=propaddr, rentcode=rentcode, rentpa=rentpa, rentperiods=rentperiods,
                           runsize=runsize, salegrade=salegrade, source=source, status=status,
                           tenantname=tenantname, tenure=tenure, rentprops=rentprops)


@bp.route('/rentals', methods=['GET', 'POST'])
def rentals():
    rentals, rentsum = getrentals()

    return render_template('rentals.html', rentals=rentals, rentsum=rentsum)


@bp.route('/rental/<int:id>', methods=['GET', 'POST'])
# @login_required
def rental(id):
    action = request.args.get('action', "view", type=str)
    if request.method == "POST":
        id = post_rental(id, action)

    rental, advarrdets, freqdets = get_rental(id)

    return render_template('rental.html', action=action, rental=rental,
                           advarrdets=advarrdets, freqdets=freqdets)


@bp.route('/rental_statement/<int:id>', methods=["GET", "POST"])
# @login_required
def rental_statement(id):
    db.session.execute(sqlalchemy.text("CALL pop_rental_statement(:x)"), params={"x": id})
    db.session.commit()
    rentalstatem = get_rentalstatement()
    print("rentalstatem")
    print(rentalstatem)

    return render_template('rental_statement.html', rentalstatem=rentalstatem)


@bp.route('/rent_object/<int:id>', methods=['GET', 'POST'])
# @login_required
def rent_object(id):
    action = request.args.get('action', "view", type=str)
    if request.method == "POST":
        postrentobj(id)
    else:
        pass

    rentobj, properties = getrentobj_main(id)
    charges = get_charges(id)
    # owingstat = owingstat(rentobj, charges)

    actypedets, advarrdets, deedcodes, freqdets, landlords, mailtodets, salegradedets, \
        statusdets, tenuredets = getrentobj_combos(id)

    if not session['mailtodets']:
        session['mailtodets'] = [value for (value,) in Typemailto.query.with_entities(Typemailto.mailtodet).all()]
    session['mailtodet'] = rentobj.mailtodet
    session['mailaddr'] = rentobj.mailaddr
    session['propaddr'] = rentobj.propaddr
    session['tenantname'] = rentobj.tenantname

    return render_template('rent_object.html', action=action, rentobj=rentobj,
                       properties=properties, actypedets=actypedets, advarrdets=advarrdets, charges=charges,
                       deedcodes=deedcodes, freqdets=freqdets, landlords=landlords, mailtodets=mailtodets,
                       salegradedets=salegradedets, statusdets=statusdets, tenuredets=tenuredets)


@bp.route('/save_html', methods=['GET', 'POST'])
def save_html():
    item = request.args.get('item', "docfile_out", type=str)
    if request.method == "POST":
        id = post_docfile(item)

        return redirect('/rent_object/{}'.format(id))
