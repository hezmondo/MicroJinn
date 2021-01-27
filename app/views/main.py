from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required
from app.dao.agent import delete_agent, get_agent, get_agents, get_agent_rents, post_agent
from app.dao.filter import get_rent_s
from app.dao.main import get_emailaccount, get_emailaccounts, get_rent_ex, post_emailaccount
from app.dao.property import get_properties, get_property, get_proptypes, post_property
from app.dao.landlord import get_landlord, get_landlords, get_landlord_dict, post_landlord

main_bp = Blueprint('main_bp', __name__)


@main_bp.route('/agents', methods=['GET', 'POST'])
def agents():
    agents = get_agents()
    return render_template('agents.html', agents=agents)


@main_bp.route('/agent/<int:agent_id>', methods=["GET", "POST"])
@login_required
def agent(agent_id):
    rent_id = int(request.args.get('rent_id', "0", type=str))
    if request.method == "POST":
        id_ = post_agent(agent_id)
        return redirect(url_for('main_bp.agent', agent_id=id_))

    if id == 0:
        agent = {"id": 0, "detail": "", "email": "", "note": "", "code": ""}
    else:
        agent = get_agent(agent_id)
    return render_template('agent.html', agent=agent, rent_id=rent_id)


@main_bp.route('/agent_delete/<int:agent_id>')
@login_required
def agent_delete(agent_id):
    delete_agent(agent_id)
    return redirect(url_for('main_bp.agents'))


@main_bp.route('/agent_rents/<int:agent_id>', methods=["GET"])
@login_required
def agent_rents(agent_id):
    agent = get_agent(agent_id)
    agent_headrents, agent_rents = get_agent_rents(agent_id)
    return render_template('agent_rents.html', agent=agent, agent_rents=agent_rents, agent_headrents=agent_headrents)


@main_bp.route('/email_accounts', methods=['GET'])
def email_accounts():
    emailaccs = get_emailaccounts()
    return render_template('email_accounts.html', emailaccs=emailaccs)


@main_bp.route('/email_account/<int:email_account_id>', methods=['GET', 'POST'])
@login_required
def email_account(email_account_id):
    if request.method == "POST":
        id_ = post_emailaccount(email_account_id)
        return redirect(url_for('main_bp.email_account', email_account_id=id_))
    emailacc = get_emailaccount(email_account_id) if email_account_id != 0 else {"id": 0}
    return render_template('email_account.html', emailacc=emailacc)


@main_bp.route('/', methods=['GET', 'POST'])
@main_bp.route('/home', methods=['GET', 'POST'])
# @login_required
def home():
    filterdict, rent_s = get_rent_s("basic", 0)

    return render_template('home.html', filterdict=filterdict, rent_s=rent_s)


@main_bp.route('/landlord/<int:landlord_id>', methods=['GET', 'POST'])
@login_required
def landlord(landlord_id):
    if request.method == "POST":
        id_ = post_landlord(landlord_id)

        return redirect(url_for('landlord_bp.property', landlord_id=id_))

    landlord = get_landlord(landlord_id) if landlord_id != 0 else {"id": 0}
    landlord_dict = get_landlord_dict()

    return render_template('landlord.html', landlord=landlord, landlord_dict=landlord_dict)


@main_bp.route('/landlords', methods=['GET'])
def landlords():
    landlords = get_landlords()

    return render_template('landlords.html', landlords=landlords)


@main_bp.route('/properties/<int:rent_id>', methods=['GET', 'POST'])
# @login_required
def properties(rent_id):
    properties, proptypes = get_properties(rent_id)
    print(rent_id)

    return render_template('properties.html', rent_id=rent_id, properties=properties, proptypes=proptypes)


@main_bp.route('/property/<int:property_id>', methods=["GET", "POST"])
# @login_required
def property(property_id):
    rent_id = int(request.args.get('rent_id', "0", type=str))
    if request.method == "POST":
        id = post_property(property_id, rent_id)

        return redirect(url_for('main_bp.property', property_id=id))

    property_ = get_property(property_id, rent_id)
    proptypes = get_proptypes("basic")

    return render_template('property.html', property_=property_, proptypes=proptypes)


@main_bp.route('/rent_ex/<int:rent_ex_id>', methods=["GET"])
@login_required
def rent_ex(rent_ex_id):
    rent_ex = get_rent_ex(rent_ex_id)

    return render_template('rent_ex.html', rent_ex=rent_ex)


@main_bp.route('/rents_ex', methods=['GET', 'POST'])
def rents_ex():
    filterdict, rent_s = get_rent_s("external", 0)

    return render_template('rents_ex.html', filterdict=filterdict, rent_s=rent_s)
