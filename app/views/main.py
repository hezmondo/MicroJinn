from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required
from app.dao.agent import get_agent, get_agents, post_agent
from app.dao.filter import get_rent_s
from app.dao.main import get_emailaccount, get_emailaccounts, get_rent_ex, post_emailaccount
from app.dao.property import get_properties, get_property, get_proptypes, post_property
from app.dao.landlord import get_landlord, get_landlords, get_landlord_dict, post_landlord

main_bp = Blueprint('main_bp', __name__)


@main_bp.route('/agents', methods=['GET', 'POST'])
def agents():
    agents = get_agents()

    return render_template('agents.html', agents=agents)


@main_bp.route('/agent/<int:id>', methods=["GET", "POST"])
@login_required
def agent(id):
    if request.method == "POST":
        id = post_agent(id)
        return redirect(url_for('main_bp.agent', id=id))
    agent = get_agent(id) if id != 0 else {"id": 0, "detail": "", "email": "", "note": "", "code": ""}

    return render_template('agent.html', agent=agent)


@main_bp.route('/email_accounts', methods=['GET'])
def email_accounts():
    emailaccs = get_emailaccounts()

    return render_template('email_accounts.html', emailaccs=emailaccs)


@main_bp.route('/email_account/<int:id>', methods=['GET', 'POST'])
@login_required
def email_account(id):
    if request.method == "POST":
        id = post_emailaccount(id)
        return redirect(url_for('main_bp.email_account', id=id))

    emailacc = get_emailaccount(id) if id != 0 else {"id": 0}

    return render_template('email_account.html', emailacc=emailacc)


@main_bp.route('/', methods=['GET', 'POST'])
@main_bp.route('/home', methods=['GET', 'POST'])
# @login_required
def home():
    filterdict, rent_s = get_rent_s("basic", 0)

    return render_template('home.html', filterdict=filterdict, rent_s=rent_s)


@main_bp.route('/landlord/<int:id>', methods=['GET', 'POST'])
@login_required
def landlord(id):
    if request.method == "POST":
        id = post_landlord(id)

        return redirect(url_for('landlord_bp.property', id=id))

    landlord = get_landlord(id) if id != 0 else {"id": 0}
    landlord_dict = get_landlord_dict()

    return render_template('landlord.html', landlord=landlord, landlord_dict=landlord_dict)


@main_bp.route('/landlords', methods=['GET'])
def landlords():
    landlords = get_landlords()

    return render_template('landlords.html', landlords=landlords)


@main_bp.route('/properties/<int:rentid>', methods=['GET', 'POST'])
# @login_required
def properties(rentid):
    properties, proptypes = get_properties(rentid)
    print(rentid)

    return render_template('properties.html', rentid=rentid, properties=properties, proptypes=proptypes)


@main_bp.route('/property/<int:id>', methods=["GET", "POST"])
# @login_required
def property(id):
    rentid = int(request.args.get('rentid', "0", type=str))
    if request.method == "POST":
        id = post_property(id, rentid)

        return redirect(url_for('main_bp.property', id=id))

    property_ = get_property(id, rentid)
    proptypes = get_proptypes("basic")

    return render_template('property.html', property_=property_, proptypes=proptypes)


@main_bp.route('/rent_ex/<int:id>', methods=["GET"])
@login_required
def rent_ex(id):
    rent_ex = get_rent_ex(id)

    return render_template('rent_ex.html', rent_ex=rent_ex)


@main_bp.route('/rents_ex', methods=['GET', 'POST'])
def rents_ex():
    filterdict, rent_s = get_rent_s("external", 0)

    return render_template('rents_ex.html', filterdict=filterdict, rent_s=rent_s)
