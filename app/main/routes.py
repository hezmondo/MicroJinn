import sqlalchemy
import datetime
from flask import flash, jsonify, redirect, render_template, request, send_from_directory, send_file, session, url_for
from flask_login import login_required
from io import BytesIO
from app import db
from app.main import bp
from app.main.common import get_combodict
from app.main.delete import delete_record
from app.main.doc_obj import get_docfile, get_docfiles, post_docfile, post_upload, post_payrequestfile
from app.main.functions import backup_database
from app.main.other import get_emailaccount, get_emailaccounts, get_formletter, get_formletters, get_formpayrequests, \
    get_headrent, get_headrents, get_loan, get_loan_options, get_loans, get_loanstatement, \
    get_rental, getrentals, get_rentalstatement, \
    post_emailaccount, post_formletter, post_headrent, post_loan, post_rental
from app.main.inc_obj import get_incobj_post, get_incomes, get_incobj, get_incobj_options, \
    get_inc_options, post_inc_obj
from app.main.money import get_moneyaccount, get_moneydets, get_moneyitem, get_moneyitems, get_money_options, \
    post_moneyaccount, post_moneyitem
from app.main.rent_obj import get_agent, get_agents, get_charge, get_charges, get_externalrent, get_landlord, \
        get_landlord_extras, get_landlords, get_lease, get_leases, get_property, getrentobj_main, get_rentobjs, \
        post_agent, post_charge, post_landlord, post_lease, post_property, postrentobj
from app.main.writemail import writeMail, write_payrequest
from app.main.payrequests import forward_rents
from app.models import Digfile, Jstore, Loan, Pr_filter, Template, Typedoc


@bp.route('/agents', methods=['GET', 'POST'])
def agents():
    agents = get_agents()

    return render_template('agents.html', agents=agents)


@bp.route('/agent/<int:id>', methods=["GET", "POST"])
@login_required
def agent(id):
    if request.method == "POST":
        agent = post_agent(id)
    else:
        agent = get_agent(id)

    return render_template('agent.html', agent=agent)


@bp.route('/backup', methods=['GET', 'POST'])
# @login_required
def backup():
    if request.method == "POST":
        backup_database()

    return render_template('backup.html')


@bp.route('/charge/<int:id>', methods=["GET", "POST"])
@login_required
def charge(id):
    if request.method == "POST":
        rentid = post_charge(id)

        return redirect('/rent_object/{}'.format(rentid))

    charge, chargedescs = get_charge(id)

    return render_template('charge.html', charge=charge, chargedescs=chargedescs)


@bp.route('/charges', methods=['GET', 'POST'])
def charges():
    rentid = request.args.get('rentid', "0", type=str)
    rentcode = request.args.get('rentcode', "", type=str)
    charges = get_charges(rentid)

    return render_template('charges.html', charges=charges, rentid=rentid, rentcode=rentcode)


@bp.route('/delete_item/<int:id>')
@login_required
def delete_item(id):
    rentid = delete_record(id)
    if rentid != 0:
        return redirect('/rent_object/{}'.format(rentid))

    return redirect(url_for('main.index'))


@bp.route('/docfile/<int:id>', methods=['GET', 'POST'])
@login_required
def docfile(id):
    if request.method == "POST":
        rent_id = post_docfile(id)

        return redirect('/rent_object/{}'.format(rent_id))

    docfile, doc_dig = get_docfile(id)

    return render_template('docfile.html', docfile=docfile, doc_dig=doc_dig)


@bp.route('/docfiles/<int:rentid>', methods=['GET', 'POST'])
def docfiles(rentid):
    docfiles, dfoutin = get_docfiles(rentid)
    outins = ["all", "out", "in"]

    return render_template('docfiles.html', rentid=rentid, dfoutin=dfoutin, docfiles=docfiles, outins=outins)


@bp.route('/download/<int:id>')
@login_required
def download(id):
    digfile = Digfile.query.filter(Digfile.id == id).one_or_none()
    return send_file(BytesIO(digfile.dig_data), attachment_filename=digfile.summary, as_attachment=True,
                     mimetype='application/pdf')


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
    filterdict, rentprops = get_rentobjs("external", 0)

    return render_template('external_rents.html', filterdict=filterdict, rentprops=rentprops)


@bp.route('/external_rent/<int:id>', methods=["GET"])
@login_required
def external_rent(id):
    external_rent = get_externalrent(id)

    return render_template('external_rent.html', external_rent=external_rent)


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
    headrents, statusdets = get_headrents()

    return render_template('headrents.html', headrents=headrents, statusdets=statusdets)


@bp.route('/headrent/<int:id>', methods=["GET", "POST"])
@login_required
def headrent(id):
    action = request.args.get('action', "view", type=str)
    if request.method == "POST":
        id = post_headrent(id, action)
        action = "view"
    headrent = get_headrent(id)
    advarrdets, freqdets, landlords, statusdets, tenuredets = get_combos_common()

    return render_template('headrent.html', action=action, advarrdets=advarrdets, freqdets=freqdets,
                           landlords=landlords, statusdets=statusdets, tenuredets=tenuredets, headrent=headrent)


@bp.route('/income', methods=['GET', 'POST'])
def income():
    rentid = int(request.args.get('rentid', "0", type=str))
    incomes = get_incomes(rentid)
    bankaccs, paytypes = get_inc_options()

    return render_template('income.html', rentid=rentid, bankaccs=bankaccs, paytypes=paytypes, incomes=incomes)


@bp.route('/income_object/<int:id>', methods=['GET', 'POST'])
@login_required
def income_object(id):
    action = request.args.get('action', "view", type=str)
    if request.method == "POST":
        id = post_inc_obj(id, action)

    bankaccs, chargedescs, landlords, paytypes = get_incobj_options()
    income, incomeallocs = get_incobj(id)

    return render_template('income_object.html', action=action, bankaccs=bankaccs, chargedescs=chargedescs,
                           income=income, incomeallocs=incomeallocs, landlords=landlords, paytypes=paytypes)


@bp.route('/income_post/<int:id>', methods=['GET', 'POST'])
@login_required
def income_post(id):
    if request.method == "POST":
        post_inc_obj(id, "new")

    bankaccs, chargedescs, landlords, paytypes = get_incobj_options()
    allocs, post, post_tot, today = get_incobj_post(id)

    return render_template('income_post.html', allocs=allocs, bankaccs=bankaccs, chargedescs=chargedescs,
                           paytypes=paytypes, post=post, post_tot=post_tot, today=today)


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    session['doc_types'] = [value for (value,) in Typedoc.query.with_entities(Typedoc.desc).all()]
    filterdict, rentprops = get_rentobjs("basic", 0)

    return render_template('home.html', filterdict=filterdict, rentprops=rentprops)


@bp.route('/landlord/<int:id>', methods=['GET', 'POST'])
@login_required
def landlord(id):
    if request.method == "POST":
        landlord = post_landlord(id)
    else:
        landlord = get_landlord(id)

    managers, emailaccs, bankaccs = get_landlord_extras()

    return render_template('landlord.html', landlord=landlord, bankaccs=bankaccs,
                           managers=managers, emailaccs=emailaccs)


@bp.route('/landlords', methods=['GET'])
def landlords():
    landlords = get_landlords()

    return render_template('landlords.html', landlords=landlords)


@bp.route('/lease/<int:id>', methods=['GET', 'POST'])
@login_required
def lease(id):
    # id can be actual lease id or 0 (for new lease or for id unknown as coming from rent)
    if request.method == "POST":
        rentid = post_lease(id)

        return redirect('/rent_object/{}'.format(rentid))

    action, lease, uplift_types = get_lease(id)

    return render_template('lease.html', action=action, lease=lease, uplift_types=uplift_types)


@bp.route('/leases', methods=['GET', 'POST'])
def leases():
    leases, uplift_types, rcd, uld, ult = get_leases()

    return render_template('leases.html', leases=leases, uplift_types=uplift_types, rcd=rcd, uld=uld, ult=ult)


@bp.route('/load_filter', methods=['GET', 'POST'])
def load_filter():
    # load predefined filters from jstore for queries and payrequests
    jfilters = Jstore.query.all()

    return render_template('load_filter.html', jfilters=jfilters)


@bp.route('/loan/<int:id>', methods=['GET', 'POST'])
@login_required
def loan(id):
    action = request.args.get('action', "view", type=str)
    if request.method == "POST":
        id = post_loan(id, action)
        action = "view"
    loan = get_loan(id)
    advarrdets, freqdets = get_loan_options()

    return render_template('loan.html', action=action, loan=loan, advarrdets=advarrdets, freqdets=freqdets)


@bp.route('/loans', methods=['GET', 'POST'])
def loans():
    action = request.args.get('action', "view", type=str)
    loans, loansum = get_loans(action)

    return render_template('loans.html', loans=loans, loansum=loansum)


@bp.route('/loanstat_dialog/<int:id>', methods=["GET", "POST"])
def loanstat_dialog(id):
    return render_template('loanstat_dialog.html', loanid=id, today=datetime.date.today())


@bp.route('/loan_statement/<int:id>', methods=["GET", "POST"])
@login_required
def loan_statement(id):
    if request.method == "POST":
        stat_date = request.form.get("statdate")
        rproxy = db.session.execute(sqlalchemy.text("CALL pop_loan_statement(:x, :y)"),
                                    params={"x": id, "y": stat_date})
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

    return render_template('mail_dialog.html', action=action, formletters=formletters, rent_id=id)


@bp.route('/mail_edit/<int:id>', methods=["GET", "POST"])
@login_required
def mail_edit(id):
    method = request.args.get('method', "email", type=str)
    action = request.args.get('action', "normal", type=str)
    if request.method == "POST":
            # print(request.form)
        formletter_id = id
        rent_id = request.form.get('rent_id')
        addressdata, block, leasedata, rentobj, subject, doctype, dcode = writeMail(rent_id, 0, formletter_id,
                                                                                    action)
        mailaddr = request.form.get('mailaddr')
        summary = dcode + "-" + method + "-" + mailaddr[0:25]
        mailaddr = mailaddr.split(", ")

        return render_template('mergedocs/LTS.html', addressdata=addressdata, block=block, doctype=doctype,
                               summary=summary, formletter=formletter, leasedata=leasedata, mailaddr=mailaddr,
                               method=method, rentobj=rentobj, subject=subject)


@bp.route('/money', methods=['GET', 'POST'])
def money():
    moneydets, accsums = get_moneydets()

    return render_template('money.html', moneydets=moneydets, accsums=accsums)


@bp.route('/money_account/<int:id>', methods=['GET', 'POST'])
@login_required
def money_account(id):
    if request.method == "POST":
        id_ = post_moneyaccount(id)
        return redirect('/money_account/{}'.format(id_))
    moneyacc = get_moneyaccount(id)

    return render_template('money_account.html', moneyacc=moneyacc)


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
    bankaccs, cats, cleareds = get_money_options()
    accsums, moneyitems, values = get_moneyitems(id)

    return render_template('money_items.html', moneyitems=moneyitems, values=values,
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


# TODO: Possible refactor of payrequests - currently a duplication of queries but with forward_rents function
@bp.route('/payrequests/', methods=['GET', 'POST'])
@login_required
def payrequests():
    action = request.args.get('action', "view", type=str)
    name = request.args.get('name', "queryall", type=str)

    combodict = get_combodict("advanced")

    filterdict, rentprops = get_rentobjs(action, name)

    # TODO: forward rents using ajax so that the page needn't be reloaded
    if action == "run":
        forward_rents(rentprops)

    return render_template('payrequests.html', combodict=combodict, filterdict=filterdict, rentprops=rentprops)


@bp.route('/pr_dialog/<int:id>', methods=["GET", "POST"])
@login_required
def pr_dialog(id):
    formpayrequests = get_formpayrequests()

    return render_template('pr_dialog.html', formpayrequests=formpayrequests, rent_id=id)


@bp.route('/pr_edit/<int:id>', methods=["GET", "POST"])
@login_required
def pr_edit(id):
    method = request.args.get('method', "email", type=str)
    if request.method == "POST":
        # formpayrequest_id is the id of the pr template
        formpayrequest_id = id
        rent_id = request.form.get('rent_id')
        # TODO: passing both totdue and totdue_string with money formatting. Is there a better way?
        addressdata, block, rentobj, subject, \
            table_rows, totdue, totdue_string = write_payrequest(rent_id, formpayrequest_id)
        mailaddr = request.form.get('mailaddr')
        # TODO: Do we want a specific PR code to begin the summary?
        summary = "PR" + "-" + method + "-" + mailaddr[0:25]
        mailaddr = mailaddr.split(", ")

        return render_template('mergedocs/PR.html', addressdata=addressdata, block=block, mailaddr=mailaddr,
                               method=method, rentobj=rentobj, subject=subject, summary=summary, table_rows=table_rows,
                               totdue=totdue, totdue_string=totdue_string)


@bp.route('/pr_main/<int:id>', methods=['GET', 'POST'])
@login_required
def pr_main(id):
    combodict = get_combodict("advanced")
    filterdict, rentprops = get_rentobjs("payrequest", id)

    return render_template('pr_main.html', combodict=combodict, filterdict=filterdict, rentprops=rentprops)


@bp.route('/pr_start', methods=['GET', 'POST'])
@login_required
def pr_start():
    filters = Pr_filter.query.all()

    return render_template('pr_start.html', filters=filters)


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


@bp.route('/queries/<int:id>', methods=['GET', 'POST'])
def queries(id):
    # allows the user to obtain a selection of rent objects using multiple filter inputs
    action = request.args.get('action', "advanced", type=str)
    combodict = get_combodict("enhanced")
    #gather combobox values, with "all" added as an option, in a dictionary
    filterdict, rentprops = get_rentobjs(action, id)
    #gather filter values and selected rent objects in two dictionaries

    return render_template('queries.html', combodict=combodict, filterdict=filterdict, rentprops=rentprops)


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
    combodict = get_combodict("basic")
    rentobj, properties = getrentobj_main(id)
    charges = get_charges(id)
    session['mailtodet'] = rentobj.mailtodet
    session['mailaddr'] = rentobj.mailaddr
    session['propaddr'] = rentobj.propaddr
    session['tenantname'] = rentobj.tenantname

    return render_template('rent_object.html', action=action, charges=charges, rentobj=rentobj, properties=properties,
                           combodict=combodict)


@bp.route('/save_html', methods=['GET', 'POST'])
def save_html():
    action = request.args.get('action', "view", type=str)
    if request.method == "POST":
        if action == "payrequest":
            id_ = post_payrequestfile()
        else:
            id_ = post_docfile(0)

        return redirect('/docfiles/{}'.format(id_))

        # return redirect('/docfile/{}?doc_dig_doc'.format(id_))


@bp.route('/upload_file/<int:rentid>', methods=["GET", "POST"])
@login_required
def upload_file(rentid):
    rentcode = request.args.get('rentcode', "dummy", type=str)
    if request.method == "POST":
        post_upload()

        return redirect('/rent_object/{}'.format(rentid))

    return render_template('upload_dialog.html', rentcode=rentcode, rent_id=rentid)

# @bp.route('/uploads/<filename>')
# def upload(filename):
#     return send_from_directory(app.config['UPLOAD_PATH'], filename)
