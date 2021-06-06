import json
from app import app
from flask import Blueprint, redirect, render_template, request, url_for, current_app
from flask_login import login_required
from app.dao.action import delete_action, delete_actions, get_actions, resolve_action
from app.dao.common import delete_record, get_deed, get_deed_types, post_deed
from app.dao.database import rollback_database
from app.dao.email_acc import get_email_acc, get_email_accs, post_email_acc
from app.dao.landlord import get_landlord, get_landlords, get_landlord_dict, post_landlord
from app.email import app_send_email, test_email_connect, test_send_email
from app.main.property import mget_properties_dict, mget_filter, mget_property, mget_properties_from_filter, mget_properties_all, \
    mget_properties_from_rent_id, mpost_new_property, mpost_property


util_bp = Blueprint('util_bp', __name__)


@util_bp.route('/action_link/<url>', methods=["GET", "POST"])
@login_required
def action_link(url):
    url_vars = json.loads(request.args.get('url_vars'))
    return redirect(url_for(url, **url_vars))


@util_bp.route('/action_delete/<int:action_id>', methods=["GET", "POST"])
@login_required
def action_delete(action_id):
    message = ''
    try:
        if action_id == 0:
            delete_actions()
        else:
            delete_action(action_id)
    except Exception as ex:
        message = f'Unable to clear action(s). Error: {str(ex)}'
    return redirect(url_for('util_bp.actions', message=message))


@util_bp.route('/action_resolve/<int:action_id>', methods=["GET", "POST"])
@login_required
def action_resolve(action_id):
    resolve_action(action_id)
    return redirect(url_for('util_bp.actions'))


@util_bp.route('/actions', methods=["GET", "POST"])
@login_required
def actions():
    actions = get_actions()
    return render_template('actions.html', actions=actions)


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


@util_bp.route('/email_submit_error', methods=["GET", "POST"])
@login_required
def email_submit_error():
    appmail = current_app.extensions['mail']
    html_body = request.args.get('body')
    subject = 'Test error'
    recipients = app.config['ADMINS']
    response = app_send_email(appmail, recipients, subject, html_body)
    return render_template('utilities.html', message=response)


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


@util_bp.route('/properties', methods=['GET', 'POST'])
@login_required
def properties():
    rent_id = request.args.get('rent_id', type=int)
    action = request.args.get('action')
    messages = []
    properties = []
    if request.method == "POST":
        if action == 'post_new':
            propaddr = request.form.get('new_propaddr')
            proptype_id = request.form.get('new_proptype')
            try:
                mpost_new_property(rent_id, propaddr, proptype_id)
            except Exception as ex:
                messages.append(f"Post new property failed. Database rolled back. Error:  {str(ex)}")
                rollback_database()
        elif action == 'edit':
            propaddr = request.form.get('propaddr')
            proptype_id = request.form.get('proptype')
            prop_id = request.args.get('prop_id')
            try:
                mpost_property(prop_id, propaddr, proptype_id)
            except Exception as ex:
                messages.append(f"Edit property failed. Database rolled back. Error:  {str(ex)}")
                rollback_database()
        elif action == 'search':
            fdict, filtr = mget_filter()
            try:
                properties = mget_properties_from_filter(filtr)
            except Exception as ex:
                messages.append(f"Cannot retrieve properties. Error:  {str(ex)}")
            return render_template('properties.html', fdict=fdict, rent_id=rent_id, properties=properties)
    try:
        properties = mget_properties_from_rent_id(rent_id) if rent_id else mget_properties_all()
    except Exception as ex:
        messages.append(f"Cannot retrieve properties. Error:  {str(ex)}")
    # if we are posting a new property or updating a previous one, we do not include the action in the template as
    # the action will cause the relevant modal to pop up on page load
    if request.method == "POST":
        return render_template('properties.html', fdict=mget_properties_dict(), rent_id=rent_id, properties=properties,
                               messages=messages)
    else:
        return render_template('properties.html', action=action, fdict=mget_properties_dict(), rent_id=rent_id,
                               properties=properties, messages=messages)


@util_bp.route('/property/<int:prop_id>', methods=["GET", "POST"])
@login_required
def property(prop_id):
    rent_id = request.args.get('rent_id', type=int)
    action = request.args.get('action', type=str)
    if request.method == "POST":
        propaddr = request.form.get('propaddr')
        proptype_id = request.form.get('proptype')
        prop_id = mpost_property(prop_id, propaddr, proptype_id)
        return redirect(url_for('util_bp.property', prop_id=prop_id))
    property = mget_property(prop_id, rent_id)

    return render_template('property.html', action=action, property=property)


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
