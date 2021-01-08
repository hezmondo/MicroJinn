import sqlalchemy
import datetime
from flask import redirect, render_template, request, send_from_directory, send_file, session, url_for
from flask_login import login_required
from io import BytesIO
from app import db
from app.main import bp
from app.main.agent import get_agent, get_agents, post_agent
from app.main.charge import get_charge, get_charges, post_charge
from app.main.common import get_combodict
from app.main.delete import delete_record
from app.main.doc_obj import get_docfile, get_docfiles, post_docfile, post_upload, post_payrequestfile
from app.main.email import get_emailaccount, get_emailaccounts, post_emailaccount
from app.main.filter import get_rentobjects
from app.main.form_letter import get_formletter, get_formletters, get_formpayrequests, post_formletter
from app.main.functions import backup_database
from app.main.headrent import get_headrent, get_headrents, post_headrent
from app.main.income_obj import get_incomes, get_incomeobj, get_income_dict, post_incomeobj
from app.main.landlord import get_landlord, get_landlords, get_landlord_dict, post_landlord
from app.main.lease import get_lease, get_leases, post_lease
from app.main.loan import get_loan, get_loan_options, get_loans, get_loanstatement, post_loan
from app.main.mail import writeMail, write_payrequest
from app.main.money import get_moneyaccount, get_moneydets, get_moneyitem, get_moneyitems, get_moneydict, \
        post_moneyitem
from app.main.property import get_property
from app.main.rental import get_rental, getrentals, get_rentalstatement, post_rental
from app.main.rent_external import get_rent_external
from app.main.rentobject import get_rentobject
from app.models import Digfile, Jstore, Loan, Template, Typedoc


@bp.route('/agents', methods=['GET', 'POST'])
def agents():
    agents = get_agents()

    return render_template('agents.html', agents=agents)


@bp.route('/agent/<int:id>', methods=["GET", "POST"])
@login_required
def agent(id):
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


@bp.route('/form_letter/<int:id>', methods=['GET', 'POST'])
@login_required
def form_letter(id):
    action = request.args.get('action', "view", type=str)
    if request.method == "POST":
        id_ = post_formletter(id, action)
        return redirect('/form_letter/{}?action=view'.format(id_))
    formletter = get_formletter(id)
    templates = [value for (value,) in Template.query.with_entities(Template.code).all()]

    return render_template('form_letter.html', action=action, formletter=formletter, templates=templates)


@bp.route('/form_letters', methods=['GET'])
def form_letters():
    formletters = get_formletters("normal")

    return render_template('form_letters.html', formletters=formletters)


@bp.route('/headrents', methods=['GET', 'POST'])
def headrents():
    headrents, statusdets = get_headrents()

    return render_template('headrents.html', headrents=headrents, statusdets=statusdets)


@bp.route('/headrent/<int:id>', methods=["GET", "POST"])
@login_required
def headrent(id):
    headrent = get_headrent(id)
    combodict = get_combodict("basic")
    #gather basic combobox values in a dictionary

    return render_template('headrent.html', combodict=combodict, headrent=headrent)


@bp.route('/income/<int:id>', methods=['GET', 'POST'])
def income(id):
    # display recent income postings - id is money account id - if 0, display postings for all accounts
    incomes, incomevals = get_incomes(id)
    income_dict = get_income_dict("basic")

    return render_template('income.html', income_dict=income_dict, incomes=incomes, incomevals=incomevals)


@bp.route('/income_object/<int:id>', methods=['GET', 'POST'])
@login_required
def income_object(id):
    action = request.args.get('action', "view", type=str)
    if request.method == "POST":
        id = post_incomeobj(id, action)

    income_dict = get_income_dict("enhanced")
    income, incomeallocs = get_incomeobj(id)

    return render_template('income_object.html', action=action, income=income, incomeallocs=incomeallocs,
                           income_dict=income_dict)


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    session['doc_types'] = [value for (value,) in Typedoc.query.with_entities(Typedoc.desc).all()]
    filterdict, rentobjects = get_rentobjects("basic", 0)

    return render_template('home.html', filterdict=filterdict, rentobjects=rentobjects)


@bp.route('/landlord/<int:id>', methods=['GET', 'POST'])
@login_required
def landlord(id):
    if request.method == "POST":
        landlord = post_landlord(id)
    else:
        landlord = get_landlord(id)

    landlord_dict = get_landlord_dict()

    return render_template('landlord.html', landlord=landlord, landlord_dict=landlord_dict)


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
        addressdata, block, leasedata, rentobject, subject, doctype, dcode = writeMail(rent_id, 0, formletter_id,
                                                                                    action)
        mailaddr = request.form.get('mailaddr')
        summary = dcode + "-" + method + "-" + mailaddr[0:25]
        mailaddr = mailaddr.split(", ")

        return render_template('mergedocs/LTS.html', addressdata=addressdata, block=block, doctype=doctype,
                               summary=summary, leasedata=leasedata, mailaddr=mailaddr,
                               method=method, rentobject=rentobject, subject=subject)


@bp.route('/money', methods=['GET', 'POST'])
def money():
    accsums, moneydets = get_moneydets()

    return render_template('money.html', accsums=accsums, moneydets=moneydets)


@bp.route('/money_account/<int:id>', methods=['GET', 'POST'])
@login_required
def money_account(id):
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
    money_dict = get_moneydict()
    accsums, moneyvals, transitems = get_moneyitems(id)

    return render_template('money_items.html', accsums=accsums, money_dict=money_dict, moneyvals=moneyvals,
                           transitems=transitems)


@bp.route('/money_item/<int:id>', methods=['GET', 'POST'])
def money_item(id):
    if request.method == "POST":
        bank_id = post_moneyitem(id)

        return redirect('/money_items/{}'.format(bank_id))

    money_dict = get_moneydict()
    money_item, cleared = get_moneyitem(id)

    return render_template('money_item.html', cleared=cleared, id=id, money_dict=money_dict, money_item=money_item)


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
        addressdata, block, rentobject, subject, \
            table_rows, totdue, totdue_string = write_payrequest(rent_id, formpayrequest_id)
        mailaddr = request.form.get('mailaddr')
        # TODO: Do we want a specific PR code to begin the summary?
        summary = "PR" + "-" + method + "-" + mailaddr[0:25]
        mailaddr = mailaddr.split(", ")

        return render_template('mergedocs/PR.html', addressdata=addressdata, block=block, mailaddr=mailaddr,
                               method=method, rentobject=rentobject, subject=subject, summary=summary, table_rows=table_rows,
                               totdue=totdue, totdue_string=totdue_string)


@bp.route('/pr_start', methods=['GET', 'POST'])
@login_required
def pr_start():
    filters = Jstore.query.filter(Jstore.type == 1).all()

    return render_template('pr_start.html', filters=filters)


@bp.route('/properties', methods=['GET', 'POST'])
# @login_required
def properties():
    properties = None

    return render_template('properties.html', properties=properties)


@bp.route('/property/<int:id>', methods=["GET", "POST"])
# @login_required
def property(id):
    property, proptypes, proptype = get_property(id)

    return render_template('property.html', property=property, proptypes=proptypes, proptype=proptype)


@bp.route('/queries/<int:id>', methods=['GET', 'POST'])
def queries(id):
    # allows the selection of rent objects using multiple filter inputs for query and pr_query
    action = request.args.get('action', "query", type=str)
    combodict = get_combodict("enhanced")
    #gather combobox values, with "all" added as an option, in a dictionary
    filterdict, rentobjects = get_rentobjects(action, id)
    #gather filter values and selected rent objects in two dictionaries

    return render_template('queries.html', action=action, combodict=combodict, filterdict=filterdict,
                                             rentobjects=rentobjects)


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


@bp.route('/rent_external/<int:id>', methods=["GET"])
@login_required
def rent_external(id):
    rent_external = get_rent_external(id)

    return render_template('rent_external.html', rent_external=rent_external)


@bp.route('/rents_external', methods=['GET', 'POST'])
def rents_external():
    filterdict, rentobjects = get_rentobjects("external", 0)

    return render_template('rents_external.html', filterdict=filterdict, rentobjects=rentobjects)


@bp.route('/rent_object/<int:id>', methods=['GET', 'POST'])
# @login_required
def rent_object(id):
    combodict = get_combodict("basic")
    rentobject, properties = get_rentobject(id)
    charges = get_charges(id)
    session['mailtodet'] = rentobject.mailtodet
    session['mailaddr'] = rentobject.mailaddr
    session['propaddr'] = rentobject.propaddr
    session['tenantname'] = rentobject.tenantname

    return render_template('rentobject.html', charges=charges, rentobject=rentobject, properties=properties,
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
