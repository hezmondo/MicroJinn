from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required
from app.dao.agent import get_agent, get_agents, get_agent_rents, post_agent
from app.dao.email_acc import get_email_acc, get_email_accs, post_email_acc
from app.dao.filter import get_rent_s
from app.dao.functions import backup_database
from app.dao.landlord import get_landlord, get_landlords, get_landlord_dict, post_landlord
from app.dao.property import get_properties, get_property, get_proptypes, post_property
from app.dao.rent_ex import get_rent_ex
from app.dao.utility import delete_record

util_bp = Blueprint('util_bp', __name__)


@util_bp.route('/agent/<int:agent_id>', methods=["GET", "POST"])
@login_required
def agent(agent_id):
    rent_id = int(request.args.get('rent_id', "0", type=str))
    if request.method == "POST":
        agent_id = post_agent(agent_id)
        return redirect(url_for('util_bp.agent', agent_id=agent_id))

    if agent_id == 0:
        agent = {"id": 0, "detail": "", "email": "", "note": "", "code": ""}
    else:
        agent = get_agent(agent_id)
    return render_template('agent.html', agent=agent, rent_id=rent_id)


@util_bp.route('/agent_rents/<int:agent_id>', methods=["GET"])
@login_required
def agent_rents(agent_id):
    agent = get_agent(agent_id)
    agent_headrents, agent_rents = get_agent_rents(agent_id)
    return render_template('agent_rents.html', agent=agent, agent_rents=agent_rents, agent_headrents=agent_headrents)


@util_bp.route('/agents', methods=['GET', 'POST'])
def agents():
    agents = get_agents()
    return render_template('agents.html', agents=agents)


@util_bp.route('/delete_item/<int:item_id>/<item>')
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
    return render_template('email_account.html', emailacc=emailacc)


@util_bp.route('/email_accounts', methods=['GET'])
def email_accounts():
    emailaccs = get_email_accs()
    return render_template('email_accounts.html', emailaccs=emailaccs)


@util_bp.route('/', methods=['GET', 'POST'])
@util_bp.route('/home', methods=['GET', 'POST'])
# @login_required
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
# @login_required
def properties(rent_id):
    properties, proptypes = get_properties(rent_id)
    print(rent_id)
    return render_template('properties.html', rent_id=rent_id, properties=properties, proptypes=proptypes)


@util_bp.route('/rent_ex/<int:rent_ex_id>', methods=["GET"])
@login_required
def rent_ex(rent_ex_id):
    rent_ex = get_rent_ex(rent_ex_id)
    return render_template('rent_ex.html', rent_ex=rent_ex)


@util_bp.route('/rents_ex', methods=['GET', 'POST'])
def rents_ex():
    filterdict, rent_s = get_rent_s("external", 0)
    return render_template('rents_ex.html', filterdict=filterdict, rent_s=rent_s)
