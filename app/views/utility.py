from flask import Blueprint, redirect, render_template, request, url_for, current_app
from flask_login import login_required
from app.dao.agent import get_agent, get_agents, get_agent_rents, post_agent
from app.dao.email_acc import get_email_acc, get_email_accs, post_email_acc
from app.dao.filter import get_rent_s
from app.dao.headrent import post_headrent_agent_update
from app.dao.landlord import get_landlord, get_landlords, get_landlord_dict, post_landlord
from app.dao.property import get_properties, get_property, get_proptypes, post_property
from app.dao.rent import get_rent_external, post_rent_agent
from app.email import test_email_connect, test_send_email
from app.dao.common import delete_record, get_deed, get_deed_types, post_deed

util_bp = Blueprint('util_bp', __name__)


@util_bp.route('/agent/<int:agent_id>', methods=["GET", "POST"])
@login_required
def agent(agent_id):
    rent_id = int(request.args.get('rent_id', "0", type=str))
    rentcode = request.args.get('rentcode', "ABC1", type=str)
    action = request.args.get('action', type=str)
    rents = None
    headrents = None
    if request.method == "POST":
        agent_id, message = post_agent(agent_id, rent_id)
        if rent_id != 0:
            return redirect(url_for('rent_bp.rent', rent_id=rent_id, message=message))
    if agent_id == 0:
        agent = {"id": 0, "detail": "", "email": "", "note": "", "code": ""}
    else:
        agent = get_agent(agent_id)
        rents = get_agent_rents(agent_id, 'rent')
        headrents = get_agent_rents(agent_id, 'headrent')
    return render_template('agent.html', action=action, agent=agent, rent_id=rent_id, rentcode=rentcode,
                           rents=rents, headrents=headrents)


# TODO: Delete route can be simplified if we do not allow for agent delete when the agent is linked to multiple rents
@util_bp.route('/agent_delete/<int:agent_id>', methods=["GET", "POST"])
@login_required
def agent_delete(agent_id):
    if request.method == "POST":
        rent_id = request.args.get('rent_id', 0, type=int)
        rents = get_agent_rents(agent_id, 'rent')
        message = ""
        if rents:
            for rent in rents:
                post_rent_agent(0, rent.id)
        headrents = get_agent_rents(agent_id, 'headrent')
        if headrents:
            for rent in headrents:
                post_headrent_agent_update(0, rent.id)
        delete_record(agent_id, 'agent')
        if rent_id == 0:
            return redirect(url_for('util_bp.agents'))
        else:
            return redirect(url_for('rent_bp.rent', rent_id=rent_id,
                                    message=message))


@util_bp.route('/agent_rents/<int:agent_id>', methods=["GET"])
@login_required
def agent_rents(agent_id):
    type = request.args.get('type', "rent", type=str)
    agent = get_agent(agent_id)
    agent_rents = get_agent_rents(agent_id, type)
    return render_template('agent_rents.html', agent=agent, agent_rents=agent_rents, type=type)


@util_bp.route('/agent_unlink/<int:rent_id>', methods=["GET", "POST"])
@login_required
def agent_unlink(rent_id):
    if request.method == "POST":
        message = post_rent_agent(0, rent_id)
        return redirect(url_for('rent_bp.rent', rent_id=rent_id, message=message))


@util_bp.route('/agents', methods=['GET', 'POST'])
@login_required
def agents():
    rent_id = int(request.args.get('rent_id', "0", type=str))
    rentcode = request.args.get('rentcode', "ABC1", type=str)
    agent_id = request.args.get('agent_id', 0, type=int)
    agents = get_agents()
    return render_template('agents.html', agents=agents, agent_id=agent_id, rent_id=rent_id, rentcode=rentcode)


@util_bp.route('/agents_select', methods=['GET', 'POST'])
@login_required
def agents_select():
    rent_id = request.args.get('rent_id', type=int)
    agent_id = request.args.get('agent_id', type=int)
    try:
        message = post_rent_agent(agent_id, rent_id)
    except Exception as e:
        message = 'Unable to update rent. Database write failed.'
    return redirect(url_for('rent_bp.rent', rent_id=rent_id, message=message))


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


@util_bp.route('/', methods=['GET', 'POST'])
@util_bp.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    filterdict, rent_s = get_rent_s("basic", 0)
    return render_template('home.html', filterdict=filterdict, rent_s=rent_s)


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


@util_bp.route('/property/<int:property_id>', methods=["GET", "POST"])
# @login_required
def property(property_id):
    rent_id = int(request.args.get('rent_id', "0", type=str))
    if request.method == "POST":
        property_id = post_property(property_id, rent_id)
        return redirect(url_for('util_bp.property', property_id=property_id))
    property_ = get_property(property_id, rent_id)
    proptypes = get_proptypes("basic")

    return render_template('property.html', property_=property_, proptypes=proptypes)


@util_bp.route('/properties/<int:rent_id>', methods=['GET', 'POST'])
@login_required
def properties(rent_id):
    properties, proptypes = get_properties(rent_id)
    print(rent_id)

    return render_template('properties.html', rent_id=rent_id, properties=properties, proptypes=proptypes)


@util_bp.route('/rent_external/<int:rent_external_id>', methods=["GET"])
@login_required
def rent_external(rent_external_id):
    rent_external = get_rent_external(rent_external_id)

    return render_template('rent_external.html', rent_external=rent_external)


@util_bp.route('/rents_ex', methods=['GET', 'POST'])
@login_required
def rents_ex():
    filterdict, rent_s = get_rent_xdata("external", 0)

    return render_template('rents_ex.html', filterdict=filterdict, rent_s=rent_s)


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
