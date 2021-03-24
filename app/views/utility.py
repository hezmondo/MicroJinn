from flask import Blueprint, redirect, render_template, request, url_for, current_app
from flask_login import login_required
from app.dao.common import delete_record, get_deed, get_deed_types, post_deed
from app.dao.email_acc import get_email_acc, get_email_accs, post_email_acc
from app.dao.landlord import get_landlord, get_landlords, get_landlord_dict, post_landlord
from app.email import test_email_connect, test_send_email
from app.main.property import get_property, get_properties, post_property
from app.modeltypes import PropTypes

util_bp = Blueprint('util_bp', __name__)


@util_bp.route('/deed/<int:deed_id>', methods=["GET", "POST"])
@login_required
def deed(deed_id):
    rent_id = int(request.args.get('rent_id', "0", type=str))
    rentcode = request.args.get('rentcode', "ABC1", type=str)
    if request.method == "POST":
        deed_id = post_deed(deed_id, rent_id)
        return redirect(url_for('util_bp.deed', deed_id=deed_id))
    if deed_id == 0:
        deed = {"id": 0, "deedcode": "", "nfee": 75.00, "nfeeindeed": "£10", "info": ""}
    else:
        deed = get_deed(deed_id)
    return render_template('deed.html', deed=deed, rent_id=rent_id, rentcode=rentcode)


@util_bp.route('/deeds', methods=['GET', 'POST'])
@login_required
def deeds():
    rent_id = int(request.args.get('rent_id', "0", type=str))
    rentcode = request.args.get('rentcode', "ABC1", type=str)
    deeds = get_deed_types()
    return render_template('deeds.html', deeds=deeds, rent_id=rent_id, rentcode=rentcode)


@util_bp.route('/delete_item/<int:item_id>/<item>', methods=['GET', 'POST'])
@login_required
def delete_item(item_id, item=''):
    redir, id_dict = delete_record(item_id, item)
    return redirect(url_for(redir, **id_dict))


@util_bp.route('/email_acc/<int:email_acc_id>', methods=['GET', 'POST'])
@login_required
def email_acc(email_acc_id):
    if request.method == "POST":
        id_ = post_email_acc(email_acc_id)
        return redirect(url_for('util_bp.email_acc', email_acc_id=id_))
    emailacc = get_email_acc(email_acc_id) if email_acc_id != 0 else {"id": 0}

    return render_template('email_acc.html', emailacc=emailacc)


@util_bp.route('/email_accs', methods=['GET'])
@login_required
def email_accs():
    emailaccs = get_email_accs()

    return render_template('email_accs.html', emailaccs=emailaccs)


@util_bp.route('/landlord/<int:landlord_id>', methods=['GET', 'POST'])
@login_required
def landlord(landlord_id):
    if request.method == "POST":
        landlord_id = post_landlord(landlord_id)
        return redirect(url_for('util_bp.landlords', landlord_id=landlord_id))

    landlord = get_landlord(landlord_id) if landlord_id != 0 else {"id": 0}
    landlord_dict = get_landlord_dict()

    return render_template('landlord.html', landlord=landlord, landlord_dict=landlord_dict)


@util_bp.route('/landlords', methods=['GET'])
def landlords():
    landlords = get_landlords()

    return render_template('landlords.html', landlords=landlords)


@util_bp.route('/properties/<int:rent_id>', methods=['GET', 'POST'])
@login_required
def properties(rent_id):
    rentcode = request.args.get('rentcode', "0", type=str)
    properties, fdict = get_properties(rent_id)
    proptypes = PropTypes.names()
    proptypes.insert(0, "all proptypes")

    return render_template('properties.html', fdict=fdict, rentcode=rentcode, rent_id=rent_id, properties=properties,
                           proptypes=proptypes)


@util_bp.route('/property/<int:prop_id>', methods=["GET", "POST"])
# @login_required
def property(prop_id):
    rent_id = int(request.args.get('rent_id', "0", type=str))
    rentcode = request.args.get('rentcode', "0", type=str)
    if request.method == "POST":
        prop_id = post_property(prop_id, rent_id)
        return redirect(url_for('util_bp.property', prop_id=prop_id))
    property = get_property(prop_id, rent_id, rentcode)
    proptypes = PropTypes.names()

    return render_template('property.html', property=property, proptypes=proptypes)


@util_bp.route('/test_emailing', methods=['GET'])
def test_emailing():
    mail = current_app.extensions['mail']

    return render_template('test_emailing.html', mail=mail)


@util_bp.route('/test_emailing_connect', methods=['GET'])
def test_emailing_connect():
    appmail = current_app.extensions['mail']
    response = test_email_connect(appmail)

    return render_template('test_emailing.html', mail=appmail, test_response=response)


@util_bp.route('/test_emailing_send', methods=['POST'])
def test_emailing_send():
    appmail = current_app.extensions['mail']
    recipient = request.form.get('test_send_mail_to', "", type=str)
    response = test_send_email(appmail, recipient)

    return render_template('test_emailing.html', mail=appmail, test_response=response)


@util_bp.route('/utilities', methods=['GET', 'POST'])
@login_required
def utilities():

    return render_template('utilities.html')
